"""Portable native v4 trusted records, exact devices and firmware operations.

Imported by the Host and independent Recovery worker. Nothing runs on import.
"""
from contextlib import contextmanager
from pathlib import Path
import fcntl
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
from apx_portable_native import canonical_layout, guid, installation_identity, partition_node

STATE=Path('/var/lib/apx/native-environments/portable-v4')
IDENTITY=Path('/etc/apx-portable-native-identity-v4.json')
EFI_PATH=r'\EFI\BOOT\BOOTX64.EFI'
RUNTIME_FILES=('apx_portable_native.py','apx_portable_native_io.py','apx_portable_native_media.py',
    'apx_portable_native_worker.py','apx_portable_native_hub.py','apx_native_slot_wipe_v3.py','apx-portable-native.py')


def run(*args,input=None,timeout=120):
    return subprocess.run([str(x) for x in args],input=input,text=True,check=True,
        capture_output=True,timeout=timeout,env={'PATH':'/usr/bin','LC_ALL':'C'}).stdout


def trusted(path,limit=2**20):
    path=Path(path)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or info.st_mode&0o077 or info.st_size>limit:
            raise ValueError('untrusted native record: '+str(path))
        with os.fdopen(fd,'r',closefd=False) as stream:return json.load(stream)
    finally:os.close(fd)


def atomic(path,value):
    path=Path(path);path.parent.mkdir(parents=True,mode=0o700,exist_ok=True)
    if path.parent.is_symlink():raise ValueError('native record directory is a symlink')
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as out:
            json.dump(value,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
        os.replace(name,path)
        descriptor=os.open(path.parent,os.O_DIRECTORY);os.fsync(descriptor);os.close(descriptor)
    finally:
        if os.path.exists(name):os.unlink(name)


def file_hash(path):
    result=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(4*1024**2),b''):result.update(chunk)
    return result.hexdigest()


def regular(path,minimum=1,maximum=20*1024**3):
    path=Path(path);info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or info.st_mode&0o022 or not minimum<=info.st_size<=maximum:
        raise ValueError('untrusted native artifact: '+str(path))
    return path


@contextmanager
def locked():
    if os.geteuid():raise PermissionError('Host root required')
    STATE.mkdir(parents=True,mode=0o700,exist_ok=True)
    fd=os.open(STATE/'worker.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);yield
    finally:os.close(fd)


def disk_for(identity):
    data=json.loads(run('lsblk','-J','-p','-o','PATH,TYPE,SERIAL,WWN,PARTUUID'))
    matches=[p['path'] for p in data['blockdevices'] if p['type']=='disk' and
        (p.get('serial') or '')==identity['serial'] and (p.get('wwn') or '')==identity['wwn']]
    if len(matches)!=1:raise ValueError('stable disk identity absent or ambiguous')
    disk=matches[0]
    info=Path(disk).lstat()
    if not stat.S_ISBLK(info.st_mode):raise ValueError('disk is not a direct block device')
    table=canonical_layout(json.loads(run('sfdisk','--json',disk))['partitiontable'])
    from collections import Counter
    def partition_ids(items):
        for item in items:
            if item.get('type')=='part' and item.get('partuuid'):yield item['partuuid'].lower()
            yield from partition_ids(item.get('children',[]))
    counts=Counter(partition_ids(data['blockdevices']))
    if any(counts[p['uuid']]!=1 for p in table['partitions']):
        raise ValueError('partition identity absent or duplicated on another attached disk')
    if table['id']!=identity['disk_id'] or table['sectorsize']!=identity['sector_size']:
        raise ValueError('GPT disk or sector identity changed')
    return disk,table


def remap(table,disk):
    """Linux enumeration may change; preserve GPT identity and partition numbers."""
    import copy
    old=table['device'];value=copy.deepcopy(table);value['device']=disk
    for p in value['partitions']:
        number=next(n for n in range(1,129) if partition_node(old,n)==p['node'])
        p['node']=partition_node(disk,number)
    return canonical_layout(value)


def exact_layout(observed,expected):
    return canonical_layout(observed)==remap(expected,observed['device'])


def part(table,partuuid):
    values=[p for p in table['partitions'] if p['uuid']==guid(partuuid)]
    if len(values)!=1:raise ValueError('exact partition absent or ambiguous')
    node=values[0]['node']
    if not stat.S_ISBLK(Path(node).lstat().st_mode):raise ValueError('partition is not a direct block device')
    if run('blkid','-p','-s','PART_ENTRY_UUID','-o','value',node).strip().lower()!=partuuid.lower():
        raise ValueError('kernel partition identity differs')
    if int(run('blockdev','--getsize64',node))!=values[0]['size']*table['sectorsize']:
        raise ValueError('kernel partition extent differs')
    return node


def identity_at(table,identity):
    return installation_identity(table,serial=identity['serial'],wwn=identity['wwn'],
        root_uuid=identity['root_uuid'],root_partuuid=identity['root_partuuid'],
        esp_partuuid=identity['esp_partuuid'],recovery_partuuid=identity['recovery_partuuid'])


@contextmanager
def mounted(node,*,readonly=False,fstype=None,options=None,executable=False):
    directory=Path(tempfile.mkdtemp(prefix='apx-native-v4-',dir='/run'))
    args=['mount','-o',','.join(['ro' if readonly else 'rw','nosuid','nodev','exec' if executable else 'noexec']+(options or []))]
    if fstype:args+=['-t',fstype]
    try:
        run(*args,node,directory);yield directory
    finally:
        if os.path.ismount(directory):run('umount',directory,timeout=180)
        directory.rmdir()


def root_mounted(identity):
    # Includes bind/subvolume mounts, and never trusts a pathname alone.
    data=json.loads(run('findmnt','-J','-o','UUID,SOURCE,TARGET'))
    def visit(items):
        for item in items:
            if item.get('uuid')==identity['root_uuid']:return True
            if visit(item.get('children',[])):return True
        return False
    return visit(data.get('filesystems',[]))


def firmware():
    text=run('efibootmgr','-v')
    order=re.search(r'^BootOrder:\s*([0-9A-Fa-f,]+)\s*$',text,re.M)
    if not order:raise ValueError('UEFI BootOrder unavailable')
    entries=dict(re.findall(r'^Boot([0-9A-Fa-f]{4})\*?\s+(.+)$',text,re.M))
    return [x.upper() for x in order[1].split(',')],{k.upper():v for k,v in entries.items()}


def matching_entries(partuuid,path):
    _,entries=firmware()
    result=[]
    for number,text in entries.items():
        hd=re.search(r'HD\(\d+,GPT,([0-9a-f-]+),',text,re.I)
        file=re.search(r'(?:File)?\((\\[^)]*)\)',text,re.I)
        if hd and file and hd[1].lower()==partuuid.lower() and file[1].lower()==path.lower():result.append(number)
    return result


def linux_first(identity):
    matches=matching_entries(identity['esp_partuuid'],EFI_PATH)
    if len(matches)!=1:raise ValueError('exact APX UEFI boot entry absent or ambiguous')
    order,_=firmware();number=matches[0]
    run('efibootmgr','-o',','.join([number]+[n for n in order if n!=number]))
    if firmware()[0][0]!=number:raise ValueError('APX default boot readback failed')
    return number


def entry(table,partuuid,path,label):
    matches=matching_entries(partuuid,path)
    if len(matches)>1:
        entries=firmware()[1]
        own=[n for n in matches if re.match(re.escape(label)+r'\s',entries[n])]
        if len(own)!=1:raise ValueError('ambiguous native EFI entries')
        matches=own
    if not matches:
        p=next(p for p in table['partitions'] if p['uuid']==partuuid)
        number=next(n for n in range(1,129) if partition_node(table['device'],n)==p['node'])
        # --create-only deliberately preserves BootOrder; linux_first adds APX.
        run('efibootmgr','--create-only','-d',table['device'],'-p',str(number),'-L',label,'-l',path)
        matches=matching_entries(partuuid,path)
    if len(matches)!=1:raise ValueError('new UEFI entry readback failed')
    return matches[0]


def boot_next(number):
    if not re.fullmatch('[0-9A-F]{4}',number):raise ValueError('invalid EFI entry')
    run('efibootmgr','-n',number)
    if not re.search(r'^BootNext:\s*'+number+r'\s*$',run('efibootmgr'),re.M):raise ValueError('BootNext readback failed')


def retire(partuuid):
    _,entries=firmware()
    for number,text in entries.items():
        match=re.search(r'HD\(\d+,GPT,([0-9a-f-]+),',text,re.I)
        if match and match[1].lower()==partuuid.lower():run('efibootmgr','-b',number,'-B')
    if any(partuuid.lower() in text.lower() for text in firmware()[1].values()):raise ValueError('native EFI retirement failed')


def check_recovery(root,*,compare_host=False):
    root=Path(root);record=trusted(root/'etc/apx-portable-native-recovery-v4.json')
    expected={'usr/lib/apx/'+name for name in RUNTIME_FILES}
    if record.get('profile')!='apx-portable-native-recovery-v4' or set(record.get('files',{}))!=expected:
        raise ValueError('independent Recovery runtime manifest differs')
    for relative,sha in record['files'].items():
        if file_hash(regular(root/relative))!=sha:raise ValueError('Recovery runtime digest differs: '+relative)
        if compare_host and file_hash(regular(Path('/')/relative))!=sha:
            raise ValueError('Host and Recovery native implementations differ')
    return record
