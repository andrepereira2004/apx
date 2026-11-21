"""Portable v4 Hub integration using the existing native-instance wire verbs.

The v3 suffix is retained as protocol compatibility, not pilot implementation.
Only the portable service adapter calls these functions after peer authorization.
"""
from pathlib import Path
import importlib.util
import os
import secrets
import re
import subprocess
import sys
import time
from apx_portable_native import NAME,guid,validate_plan,validate_identity
from apx_portable_native_io import STATE,IDENTITY,atomic,trusted,disk_for,identity_at,exact_layout

RUNNER='/usr/lib/apx/apx-portable-native.py'


def check_available(*,layout=True):
    identity=trusted(IDENTITY)
    if identity.get('profile')!='apx-portable-native-identity-v4':raise ValueError('native disk identity unavailable')
    release=trusted(Path('/usr/share/apx/portable-native-v4/release.json'))
    if release.get('profile')!='apx-portable-native-release-v4':raise ValueError('portable native implementation not installed')
    from apx_portable_native_io import regular,file_hash
    for name,sha in release['files'].items():
        path=Path(name)
        if not str(path).startswith(('/usr/lib/apx/','/usr/share/apx/portable-native-v4/')):
            raise ValueError('native release path is not admitted')
        if file_hash(regular(path))!=sha:raise ValueError('portable native source changed: '+path.name)
    if not Path('/sys/firmware/efi').is_dir():raise ValueError('native Windows requires UEFI')
    for var in Path('/sys/firmware/efi/efivars').glob('SecureBoot-*'):
        if var.read_bytes()[4:5]==b'\x01':raise ValueError('unsigned experimental APX requires Secure Boot disabled')
    disk,table=disk_for(identity)
    if layout:validate_identity(identity,table,identity['serial'],identity['wwn'])
    return identity


def persist_preview(plan,description):
    validate_plan(plan);check_available()
    if (STATE/'pending.json').exists():raise ValueError('finish the current Windows transaction first')
    # Keep the socket preview bounded. Full ISO hashing is repeated by the
    # background preparation worker before any offline work, never in this UI
    # request (the console already verified the imported source).
    from apx_portable_native_io import regular
    source=trusted(STATE/'source.json')
    if source.get('profile')!='apx-portable-native-source-v4' or not re.fullmatch('[a-f0-9]{64}',source.get('sha256','')):
        raise ValueError('Regista uma ISO oficial Windows na consola do Host antes de preparar o Windows.')
    regular(source['iso'],minimum=1024**3)
    directory=STATE/'previews';directory.mkdir(parents=True,mode=0o700,exist_ok=True)
    for path in directory.glob('*.json'):
        if time.time()-path.stat().st_mtime>600:path.unlink()
    if len(list(directory.glob('*.json')))>=64:raise ValueError('too many native previews')
    value=dict(schema=4,profile='apx-portable-native-preview-v4',plan=plan,
               description=description,created_at=int(time.time()))
    atomic(directory/(plan['generation']+'.json'),value)
    return dict(can_create=True,target=plan['name'],description=description,size_gib=plan['size_gib'],
        message='Podes preparar o Windows. Depois confirma separadamente a instalação e o reinício.',
        plan={'new':{'generation':plan['generation']},'sha256':plan['sha256']},
        apx_gib=round(plan['retained_root_bytes']/1024**3,1),portable_native=True)


def records():
    directory=STATE/'instances'
    if not directory.exists():return []
    values=[]
    for path in sorted(directory.glob('*.json')):
        value=trusted(path);plan=validate_plan(value['plan'])
        if value.get('profile')!='apx-portable-native-instance-v4' or value.get('target')!=path.stem or value.get('generation')!=plan['generation']:
            raise ValueError('portable Windows catalogue identity differs')
        values.append(value)
    return values


def catalogue():
    return [dict(name=r['target'],generation=r['generation'],display_name=r.get('display_name',r['target']),
        description=r.get('description',''),environment_kind='native-boot',native_version=3,portable_native=True,
        role='native-boot',category='system',release='windows-native-portable-v4',system_kind='windows-native',
        system_label='NATIVO',session_restore=False,update_policy='native-system',state=r['state'],
        reserved_bytes=r['plan']['size_gib']*1024**3,icon=r.get('icon','monitor')) for r in records()]


def control():
    if not (STATE/'pending.json').exists():return None
    value=trusted(STATE/'pending.json');stage=value['stage'];offline=value.get('offline_stage')
    from apx_portable_native import STAGES
    before_launch=offline in STAGES[:STAGES.index('winpe-launched')]
    rollback=stage in {'preparing','prepared','prepare-failed'} or (stage in {'offline-failed','recovery-required'} and before_launch)
    retry=stage in {'install-failed','offline-failed','recovery-required'} and value.get('retries',0)<2 and value['action']!='delete'
    deleting=stage=='offline-failed' and value['action']=='delete'
    if value.get('manual_recovery'):rollback=retry=deleting=False
    return dict(busy=True,native_v3=True,portable_native=True,native_v3_local_auth=False,
        pending_generation=value['generation'],pending_target=value['target'],pending_stage=stage,pending_mode='portable',
        new_size_gib=value['plan']['size_gib'],native_v3_activate=stage=='prepared',native_v3_rollback=rollback,
        native_v3_retry=retry,native_v3_delete_retry=deleting or stage=='install-failed',
        native_v3_manual_recovery=bool(value.get('error')) and not (rollback or retry or deleting))


def dispatch(action,target,generation,lock):
    if action not in {'prepare','activate','rollback','retry','delete','boot'} or not NAME.fullmatch(target) or target=='hub':
        raise ValueError('unsupported portable native action')
    guid(generation);check_available(layout=False)
    pending=control()
    if pending and (pending['pending_generation']!=generation or pending['pending_target']!=target):
        raise ValueError('another Windows transaction remains active')
    unit='apx-portable-native-'+secrets.token_hex(6)
    fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:os.write(fd,(unit+'\n').encode());os.fsync(fd)
    finally:os.close(fd)
    try:
        subprocess.run(['systemd-run','--unit='+unit,'--collect','--property=Type=exec',
            '--property=UMask=0077','--property=TimeoutStopSec=30s',
            '--property=ExecStopPost=/usr/bin/python '+RUNNER+' unlock --lock-token '+unit,
            '/usr/bin/python',RUNNER,
            action,'--target',target,'--generation',generation,'--lock-token',unit],
            check=True,capture_output=True,text=True,timeout=15)
    except Exception:
        if Path(lock).read_text().strip()==unit:Path(lock).unlink()
        raise
    return {'accepted':True,'action':action,'target':target,'generation':generation,'unit':unit+'.service'}


def storage_status(authorize_record,environments=Path('/var/lib/apx/environments')):
    """Actual portable storage, including reclaimed members and native slots.

    No pilot device names, fixed 1 TiB ceiling or pilot-only release identifiers.
    """
    from pathlib import PurePosixPath
    import json
    from apx_portable_native_io import run
    stats=os.statvfs(environments);total=stats.f_blocks*stats.f_frsize
    available=stats.f_bavail*stats.f_frsize
    mount=json.loads(run('findmnt','-J','-T',environments,'-o','FSTYPE,FSROOT,TARGET'))['filesystems']
    if len(mount)!=1 or mount[0]['fstype']!='btrfs':raise ValueError('APX Environment storage is not Btrfs')
    info=mount[0]
    prefix=str(PurePosixPath(info['fsroot'].lstrip('/'))/os.path.relpath(environments,info['target']))
    qgroups={}
    for line in run('btrfs','qgroup','show','--raw','-re',environments).splitlines():
        fields=line.split()
        if len(fields)>=3 and re.fullmatch(r'0/\d+',fields[0]) and fields[1].isdigit():qgroups[fields[0][2:]]=int(fields[1])
    ids={}
    for line in run('btrfs','subvolume','list','-a',environments).splitlines():
        found=re.match(r'ID (\d+) .* path (.+)$',line)
        if not found:continue
        path=found[2].removeprefix('<FS_TREE>/')
        if path in ids:ids[path]=None
        else:ids[path]=found[1]
    sizes={}
    for directory in sorted(environments.iterdir()):
        if not NAME.fullmatch(directory.name):continue
        try:authorize_record(directory.name)
        except (OSError,ValueError,KeyError,PermissionError):continue
        parts=[ids.get(prefix+'/'+directory.name+'/'+role) for role in ['root','home']]
        if all(part in qgroups for part in parts):sizes[directory.name]=sum(qgroups[part] for part in parts)
        if len(sizes)>=64:break
    for value in records():sizes[value['target']]=value['plan']['size_gib']*1024**3
    identity=trusted(IDENTITY) if IDENTITY.exists() else {}
    if identity.get('profile')=='apx-portable-native-identity-v4':
        disk,_=disk_for(identity);capacity=int(run('blockdev','--getsize64',disk))
    else:
        # Full graphical installs into an existing Arch root may have no native
        # enrollment. Resolve its parent independently for read-only status.
        source=run('findmnt','-n','-o','SOURCE','-T',environments).strip().split('[',1)[0]
        device=os.path.realpath(source)
        tree=json.loads(run('lsblk','-J','-p','-s','-o','PATH,TYPE',device))
        def parents(items):
            for item in items:
                if item.get('type')=='disk':yield item['path']
                yield from parents(item.get('children',[]))
        disks=set(parents(tree['blockdevices']))
        if len(disks)!=1:raise ValueError('root whole-disk capacity is ambiguous')
        capacity=int(run('blockdev','--getsize64',disks.pop()))
    if not 0<=available<=total<=capacity<=256*1024**4 or not total:
        raise ValueError('portable filesystem/disk capacity differs')
    return dict(schema=1,profile='apx-environment-storage-v1',available_bytes=available,
                total_bytes=total,disk_total_bytes=capacity,sizes=sizes)
