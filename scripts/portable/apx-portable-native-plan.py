#!/usr/bin/env python3
"""Read-only portable Windows preview against the exact fresh-install checkpoint."""
import argparse
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import uuid

sys.path.insert(0,'/usr/lib/apx')
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from apx_portable_native import NAME, plan_create

IDENTITY=Path('/etc/apx-portable-native-identity-v4.json')


def read_identity():
    info=IDENTITY.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or stat.S_IMODE(info.st_mode)!=0o600 or info.st_size>16384:
        raise ValueError('untrusted native installation identity')
    value=json.loads(IDENTITY.read_text())
    if value.get('profile')!='apx-portable-native-identity-v4':
        raise ValueError(value.get('reason','native installation identity unavailable'))
    return value


def preview(name,size_gib,generation=None):
    if os.geteuid():raise PermissionError('Host root required')
    if type(name) is not str or not NAME.fullmatch(name) or name=='hub':
        raise ValueError('invalid native Environment name')
    if any((base/name).exists() for base in [Path('/var/lib/apx/environments'),Path('/var/lib/apx/native-environments/instances-v4')]):
        raise ValueError('an Environment with that name already exists')
    identity=read_identity()
    def output(*args):
        return subprocess.run(args,text=True,check=True,capture_output=True,timeout=20,env={'PATH':'/usr/bin','LC_ALL':'C'}).stdout
    sources=json.loads(output('/usr/bin/lsblk','--json','--paths','--output','PATH,TYPE,SERIAL,WWN'))
    matches=[item for item in sources['blockdevices'] if item.get('type')=='disk'
             and (item.get('serial') or '')==identity['serial'] and (item.get('wwn') or '')==identity['wwn']]
    if len(matches)!=1:raise ValueError('native disk absent or ambiguous')
    disk=matches[0]['path']
    table=json.loads(output('/usr/bin/sfdisk','--json',disk))['partitiontable']
    filesystems=json.loads(output('/usr/bin/findmnt','--json','--target','/','--output','FSTYPE,UUID'))['filesystems']
    if len(filesystems)!=1 or filesystems[0].get('fstype')!='btrfs' or filesystems[0].get('uuid')!=identity['root_uuid']:
        raise ValueError('running root filesystem differs from the installation identity')
    # Logical Btrfs device allocation is conservative for shrink capacity; do
    # not substitute df's free blocks for actual extents that need relocation.
    usage=output('/usr/bin/btrfs','filesystem','usage','--raw','/')
    import re
    devices=output('/usr/bin/btrfs','filesystem','show','--raw','/')
    if re.search(r'Total devices\s+1\b',devices) is None:
        raise ValueError('native creation on a multi-device Btrfs root is not admitted yet')
    match=re.search(r'^\s*Device allocated:\s*([0-9]+)\s*$',usage,re.M)
    if not match:raise ValueError('Btrfs allocated capacity unavailable')
    plan=plan_create(identity,table,serial=identity['serial'],wwn=identity['wwn'],
        name=name,generation=generation or str(uuid.uuid4()),size_gib=size_gib,used_bytes=int(match[1]))
    return dict(schema=4,profile='apx-portable-native-preview-v4',can_create=False,plan=plan,
                reason='offline, WinPE and native boot/reclaim validation pending')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',required=True)
    parser.add_argument('--size-gib',required=True,type=int)
    args=parser.parse_args()
    try:print(json.dumps(preview(args.target,args.size_gib),indent=2))
    except (OSError,ValueError,subprocess.CalledProcessError) as error:
        print(str(error),file=sys.stderr);raise SystemExit(2)
