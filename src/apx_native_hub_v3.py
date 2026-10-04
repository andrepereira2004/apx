"""Trusted per-instance catalogue and bounded Hub job dispatch."""
import hashlib,json,os,re,secrets,stat,subprocess,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from apx_native_instances_v3 import validate_windows_install_plan,validate_instances,select_instance,offline_rollback_allowed

ROOT=Path('/var/lib/apx/native-environments')
PENDING=ROOT/'pending-v3.json'
PLANS=Path('/run/apx/native-plans-v3')
ENABLE=Path('/usr/share/apx/native-v3-enabled.json')
LIFECYCLE='/usr/lib/apx/apx-native-lifecycle-v3.py'
BOOT='/usr/lib/apx/apx-native-boot-runner-v3.py'
CRITICAL={LIFECYCLE,BOOT,'/usr/lib/apx/apx_native_instances_v3.py','/usr/lib/apx/apx_native_offline_v3.py',
    '/usr/lib/apx/apx_native_backup_v3.py','/usr/lib/apx/apx_native_winpe_v3.py',
    '/usr/lib/apx/apx_native_slot_wipe_v3.py',
    '/usr/lib/apx/build-native-windows-uki-v3.py','/usr/lib/apx/apx-native-offline-layout-v3.py',
    '/usr/lib/apx/apx_native_hub_v3.py','/usr/lib/apx/apx-environment-switch-v1.py',
    '/usr/lib/apx/apx-native-windows-plan-v3.py',
    '/usr/lib/apx/apx-environment-switch-client-v1.py',
    '/usr/lib/apx/apx_environment_switch_contract.py',
    '/etc/systemd/system/apx-native-finalize-v3.service'}


def trusted(path,limit=32768):
    info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or stat.S_IMODE(info.st_mode) not in {0o400,0o600} or info.st_size>limit:
        raise ValueError('untrusted native instance data')
    return json.loads(path.read_bytes())


def enabled():
    try:
        record=trusted(ENABLE)
        if record.get('profile')!='apx-native-validated-release-v3' or set(record.get('files',{}))!=CRITICAL:return False
        for name,expected in record['files'].items():
            path=Path(name);info=path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or info.st_mode&0o022:return False
            if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:return False
        return True
    except (OSError,ValueError,KeyError):return False


def persist_preview(value):
    if not enabled():return value
    plan=validate_windows_install_plan(value['plan']);generation=plan['new']['generation']
    PLANS.mkdir(mode=0o700,parents=True,exist_ok=True)
    paths=list(PLANS.glob('*.json'))
    for path in paths:
        if time.time()-path.stat().st_mtime>600:path.unlink()
    if len(list(PLANS.glob('*.json')))>=64:raise ValueError('Too many pending Windows previews')
    message=('Podes preparar a instalação no espaço Windows reservado. Depois, o Hub pedirá confirmação para iniciar a instalação.'
             if plan['profile']=='apx-native-slot-reuse-plan-v3' else
             'Podes preparar a cópia do Windows atual. Depois de verificar a cópia e medir o espaço ocupado, o Hub pedirá confirmação separada para a migração e o reinício.')
    value=dict(value,can_create=True,message=message)
    path=PLANS/(generation+'.json');fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as stream:json.dump(value,stream);stream.flush();os.fsync(stream.fileno())
    return value


def records():
    directory=ROOT/'instances-v3'
    if not directory.exists():return []
    info=directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid or info.st_gid or stat.S_IMODE(info.st_mode)!=0o700:raise ValueError('untrusted native catalogue')
    result=[]
    for path in sorted(directory.glob('*.json')):
        value=trusted(path)
        if value.get('name')!=path.stem:raise ValueError('native catalogue name differs')
        result.append(value)
    table=json.loads(subprocess.check_output(['sfdisk','--json','/dev/nvme0n1'],text=True))['partitiontable']
    serial=Path('/sys/class/block/nvme0n1/device/serial').read_text().strip()
    validate_instances(result,table,serial)
    return result


def catalogue():
    return [dict(name=r['name'],generation=r['generation'],display_name=r.get('display_name',r['name']),description=r.get('description',''),
        environment_kind='native-boot',native_version=3,role='native-boot',category='system',release='windows-11-native-v3',
        boot_entry='firmware-'+r['name'],reserved_bytes=r['size_sectors']*512,state=r['state'],system_kind='windows-native',
        system_label='NATIVO',session_restore=False,update_policy='native-system') for r in records()]


def control():
    if not PENDING.exists():return None
    pending=trusted(PENDING)
    if pending.get('profile')!='apx-native-job-v3':raise ValueError('native pending profile differs')
    stage=pending['stage']
    rollback=offline_rollback_allowed(stage,pending.get('error'))
    attempts=pending.get('install_retries',0)
    retry=stage=='installing' and pending.get('install_failure_kind')=='winpe-failed' and bool(pending.get('error')) and type(attempts) is int and 0<=attempts<2
    delete_retry=stage=='deleting' and bool(pending.get('error'))
    return dict(busy=True,native_v3=True,pending_generation=pending['generation'],pending_target=pending['target'],
        existing_size_gib=pending.get('existing_size_gib'),new_size_gib=pending.get('new_size_gib'),
        pending_stage=stage,pending_mode=pending.get('mode','migration'),native_v3_activate=stage in {'prepared','prepared-reuse'},native_v3_rollback=rollback,
        native_v3_retry=retry,native_v3_delete_retry=delete_retry,
        native_v3_manual_recovery=bool(pending.get('error')) and not (rollback or retry or delete_retry),
        native_recovery=False)


def validate_boot(target,generation):
    # The switch daemon intentionally lacks CAP_SYS_ADMIN. Run the read-only
    # EFI/NTFS mount checks in a transient Host unit, like the boot action.
    unit='apx-native-v3-check-'+generation[:8]+'-'+secrets.token_hex(4)
    result=subprocess.run(['systemd-run','--unit='+unit,'--collect','--wait','--pipe',
        '--property=Type=exec','/usr/bin/python3',BOOT,'--target',target,
        '--generation',generation,'--validate-only'],text=True,capture_output=True,timeout=15)
    if result.returncode:
        detail=(result.stderr or result.stdout).strip().splitlines()
        raise ValueError('A validação do Windows falhou: '+(detail[-1][:240] if detail else 'verifica o registo do serviço.'))


def dispatch(action,target,generation,lock):
    if not enabled():raise ValueError('A criação de Windows ainda está em validação.')
    if action not in {'prepare','activate','rollback','retry','delete','boot'} or not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',generation):raise ValueError('invalid native operation')
    if action=='prepare':
        if PENDING.exists():raise ValueError('Existe uma operação Windows pendente.')
        preview=trusted(PLANS/(generation+'.json'))
        if preview['target']!=target or preview['plan']['new']['generation']!=generation:raise ValueError('selected preview differs')
        if time.time()-(PLANS/(generation+'.json')).stat().st_mtime>600:raise ValueError('Volta a verificar o espaço antes de criar Windows.')
    elif action=='boot':
        if PENDING.exists():raise ValueError('Conclui a operação Windows pendente.')
        record=next((r for r in records() if r['name']==target),None)
        if not record or record['generation']!=generation or record['state']!='ready':raise ValueError('selected native instance changed')
    elif action=='delete':
        if target=='windows':raise ValueError('o Windows original não pertence ao espaço reutilizável')
        if PENDING.exists():
            pending=trusted(PENDING)
            if pending.get('stage')!='deleting' or pending.get('target')!=target or pending.get('generation')!=generation:
                raise ValueError('pending deletion differs')
        else:
            record=next((r for r in records() if r['name']==target),None)
            if not record or record['generation']!=generation or record['state']!='ready':
                raise ValueError('selected native instance changed')
    else:
        pending=trusted(PENDING)
        if pending['target']!=target or pending['generation']!=generation:raise ValueError('pending instance changed')
    if action=='boot':validate_boot(target,generation)
    unit='apx-native-v3-'+action+'-'+generation[:8]
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as stream:stream.write(unit+'\n');stream.flush();os.fsync(stream.fileno())
    args=['systemd-run','--unit='+unit,'--collect','--property=Type=exec']
    if action=='boot':args += ['python3',BOOT,'--target',target,'--generation',generation,'--lock-token',unit]
    else:args += ['python3',LIFECYCLE,action,'--generation',generation,'--lock-token',unit]
    try:subprocess.run(args,check=True,text=True,capture_output=True)
    except Exception:lock.unlink(missing_ok=True);raise
    return dict(accepted=True,target=target,generation=generation,action='native-'+action+'-v3',unit=unit+'.service')
