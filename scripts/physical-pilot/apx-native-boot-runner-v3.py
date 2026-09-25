#!/usr/bin/env python3
"""Per-instance native boot validation and one-shot reboot (not deployed yet)."""
import argparse
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys

sys.path.insert(0, '/usr/lib/apx')
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from apx_native_instances_v3 import select_instance

REGISTRY = Path('/var/lib/apx/native-environments/instances-v3')
DISK = '/dev/nvme0n1'
SERIAL = 'S4DYNX0R253702'


def load_helpers():
    source = Path(__file__).with_name('apx-native-boot-runner-v1.py')
    spec = importlib.util.spec_from_file_location('native_boot_checks',source)
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def read_records():
    info = REGISTRY.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid or info.st_gid or stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError('untrusted native instance registry')
    result=[]
    for path in sorted(REGISTRY.glob('*.json')):
        info=path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or stat.S_IMODE(info.st_mode) != 0o400 or info.st_size > 16384:
            raise ValueError('untrusted native instance record')
        value=json.loads(path.read_bytes())
        if path.stem != value.get('name'):raise ValueError('native registry name mismatch')
        result.append(value)
    return result


def validate_firmware(output, record, esp_number):
    fields=dict(re.findall(r'^(BootCurrent|BootNext|BootOrder):\s*(\S.*)$',output,re.MULTILINE))
    linux=record['linux_boot_entry']
    order=fields.get('BootOrder','').split(',')
    if fields.get('BootCurrent') != linux or 'BootNext' in fields or not order or order[0] != linux:
        raise ValueError('Linux is not the default current boot or BootNext is already armed')
    expected=f'HD({esp_number},GPT,{record["esp_partuuid"]},'.lower()
    loader=record['efi_path'].replace('/','\\').lower()
    entries=[]
    for line in output.splitlines():
        found=re.match(r'^Boot([0-9A-F]{4})\*?\s+(.+)$',line)
        if found and expected in found.group(2).lower() and loader in found.group(2).lower():
            entries.append(found.group(1))
    if len(entries)!=1 or entries[0] not in order:
        raise ValueError('firmware boot entry does not identify the selected instance')
    return entries[0]


@contextmanager
def selected_esp_root(helper, esp, record):
    if esp.name == 'nvme0n1p1':
        root = Path('/boot')
        if not root.is_mount() or os.stat(root).st_dev != os.stat(esp).st_rdev or \
                helper.checked(('findmnt','-nro','FSTYPE','/boot'),'cannot inspect mounted EFI') != 'vfat' or \
                helper.block_value(esp,'PARTUUID').lower() != record['esp_partuuid'].lower():
            raise ValueError('mounted EFI does not identify the selected instance')
        yield root
    else:
        with helper.mounted_read_only(esp,'vfat') as root:
            yield root


def validate(target,generation):
    if os.geteuid()!=0 or Path('/etc/hostname').read_text().strip()!='apx-host' or Path('/sys/class/dmi/id/product_name').read_text().strip()!='82JU':
        raise ValueError('native boot requires the exact root pilot')
    if Path('/sys/class/block/nvme0n1/device/serial').read_text().strip()!=SERIAL:
        raise ValueError('physical SSD differs')
    if Path('/var/lib/apx/native-environments/pending-v3.json').exists():
        raise ValueError('a native Windows operation is pending')
    helper=load_helpers();helper.validate_secure_boot_policy()
    table=json.loads(helper.checked(('sfdisk','--json',DISK),'cannot read GPT'))['partitiontable']
    record=select_instance(read_records(),table,SERIAL,target,generation,ready=True)
    parts={p['uuid'].lower():p for p in table['partitions']}
    windows=parts[record['windows_partuuid'].lower()];esp=parts[record['esp_partuuid'].lower()]
    entry=validate_firmware(helper.checked(('efibootmgr','-v'),'cannot read firmware'),record,int(esp['node'].rsplit('p',1)[1]))
    with selected_esp_root(helper,Path(esp['node']),record) as root:
        manager=root/record['efi_path'].lstrip('/')
        bcd=root/'EFI/Microsoft/Boot/BCD'
        if not manager.is_file() or not bcd.is_file() or manager.is_symlink() or bcd.is_symlink():
            raise ValueError('selected Windows boot files are absent')
        signature=helper.checked(('sbverify','--list',str(manager)),'cannot inspect Windows signature')
        if 'Microsoft' not in signature or 'image signature certificates' not in signature:
            raise ValueError('selected Windows manager is not Microsoft signed')
    with helper.mounted_read_only(Path(windows['node']),'ntfs3') as root:
        if not (root/'Windows/System32/winload.efi').is_file():raise ValueError('selected Windows loader absent')
        helper.validate_hardware_and_return(root)
    return helper,entry


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--target',required=True);parser.add_argument('--generation',required=True);parser.add_argument('--validate-only',action='store_true');parser.add_argument('--lock-token')
    args=parser.parse_args()
    global LOCK_TOKEN
    LOCK_TOKEN=args.lock_token
    helper,entry=validate(args.target,args.generation)
    if args.validate_only:
        print('Validated selected native Windows: '+args.target);return
    helper.checked(('efibootmgr','-n',entry),'cannot arm selected native boot')
    try:
        output=helper.checked(('efibootmgr',),'cannot verify selected native boot')
        if not re.search(r'^BootNext:\s*'+entry+r'\s*$',output,re.MULTILINE):raise ValueError('BootNext differs')
        helper.checked(('systemctl','--no-block','reboot'),'cannot reboot selected native Windows')
    except Exception:
        helper.run(('efibootmgr','-N'));raise


LOCK_TOKEN=None
if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError,OSError,KeyError) as error:
        print(str(error),file=sys.stderr);raise SystemExit(2)

    finally:
        lock=Path('/run/apx/environment-management-v1.lock')
        if LOCK_TOKEN and lock.exists() and lock.read_text().strip()==LOCK_TOKEN:lock.unlink()
