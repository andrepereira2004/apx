"""Dry-run installed deletion with real read-only disk identities and cloned metadata.

All firmware mutations and block wipes are replaced; no live lifecycle metadata
is written. This is not evidence that actual deletion has been performed.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('installed_delete', '/usr/lib/apx/apx-native-lifecycle-v3.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
root = Path('/var/lib/apx/native-environments')
generation = '2770478b-480f-4aea-8910-e3201d5334c5'
m.module('apx-native-boot-runner-v1').validate_secure_boot_policy()
firmware_before = subprocess.check_output(['efibootmgr','-v'], text=True)
table_before = m.layout()
selected = m.trusted(root/'instances-v3/windows-testes.json')
entry = m.find_matching_entry(firmware_before, 6, selected['esp_partuuid'],
                             'APX windows-testes', selected['efi_path'].replace('/','\\'), allow_windows_manager=True)
assert entry == '0000'
wipes = []; removed = False
real_command = m.command

def command(*args, **kwargs):
    global removed
    if args == ('efibootmgr','-b',entry,'-B'):
        removed = True; return ''
    if args == ('efibootmgr','-v'):
        return '\n'.join(line for line in firmware_before.splitlines() if not (removed and line.startswith('Boot'+entry)))+'\n'
    if args == ('sfdisk','--json','/dev/nvme0n1'):
        return real_command(*args, **kwargs)
    raise AssertionError('Unexpected executor command: '+repr(args))


def wipe(path, size, uuid, number):
    observed = subprocess.check_output(['blkid','-p','-s','PART_ENTRY_UUID','-o','value',str(path)],text=True).strip().lower()
    actual_size = int(subprocess.check_output(['blockdev','--getsize64',str(path)],text=True))
    assert observed == uuid and size == actual_size and number in {5,6}
    wipes.append({'partition':number,'bytes':size,'partuuid':uuid})

with tempfile.TemporaryDirectory(prefix='delete-dry-run-',dir=Path(__file__).parent) as directory:
    clone = Path(directory)
    shutil.copytree(root/'instances-v3',clone/'instances-v3')
    shutil.copy2(root/'slot-layout-v3.json',clone/'slot-layout-v3.json')
    job = clone/'migrations-v3'/generation; job.mkdir(parents=True)
    shutil.copy2(root/'migrations-v3'/generation/'plan.json',job/'plan.json')
    lock = clone/'management.lock'; lock.write_text('dry-run-token')
    with mock.patch.object(m,'target'), mock.patch.object(m,'ROOT',clone), mock.patch.object(m,'PENDING',clone/'pending.json'), \
         mock.patch.object(m,'LOCK',lock), mock.patch.object(m,'STATE',clone/'state.json'), \
         mock.patch.object(m,'command',side_effect=command), mock.patch.object(m,'wipe_block_partition',side_effect=wipe):
        m.delete_instance(generation,'dry-run-token')
    marker = json.loads((clone/'free-slot-v3.json').read_text())
    assert marker['size_sectors']*512 == 77*1024**3
    assert not (clone/'instances-v3/windows-testes.json').exists()
    assert (clone/'instances-v3/windows.json').read_bytes() == (root/'instances-v3/windows.json').read_bytes()
assert subprocess.check_output(['efibootmgr','-v'],text=True) == firmware_before
assert m.layout() == table_before
assert (root/'instances-v3/windows-testes.json').exists()
result = dict(installed_delete_dry_run=True, block_writes_performed=False,
              firmware_writes_performed=False, live_registration_preserved=True,
              ac_power_present=Path('/sys/class/power_supply/ADP0/online').read_text().strip()=='1',
              physical_delete_requires_ac=True,
              target_entry=entry, simulated_wipes=wipes, free_slot_gib=77,
              gpt_unchanged=True, firmware_unchanged=True)
Path(__file__).with_name('installed-delete-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
