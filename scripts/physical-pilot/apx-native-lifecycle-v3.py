#!/usr/bin/env python3
"""Physical-pilot v3 preparation/finalization candidate. Not deployed/enabled.

Entry into this executor requires an authoritative Hub-owned operation token.
No singleton v1 destructive operation is used for a second installation.
"""
from contextlib import contextmanager
import argparse,hashlib,importlib.util,json,os,re,shutil,stat,subprocess,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,'/usr/lib/apx');sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from apx_native_instances_v3 import validate_plan,validate_windows_install_plan,canonical_layout,validate_instances,free_slot_record,offline_rollback_allowed,validate_install_status,validate_failed_install_status
from apx_native_backup_v3 import prepare_images,image_hash,source_fingerprint
from apx_native_slot_wipe_v3 import wipe_block_partition
from apx_native_winpe_v3 import render

ROOT=Path('/var/lib/apx/native-environments')
PENDING=ROOT/'pending-v3.json'
LOCK=Path('/run/apx/environment-management-v1.lock')
STATE=Path('/run/apx/environment-management-v1.json')
DISK='/dev/nvme0n1'
SOURCE=Path(__file__).parent


def command(*args,**kwargs):
    return subprocess.run(list(args),check=True,text=True,capture_output=True,
        env={'PATH':'/usr/bin','LC_ALL':'C'},**kwargs).stdout


def write(path,value,mode=0o400):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd,temporary=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
    with os.fdopen(fd,'w') as stream:
        os.fchmod(stream.fileno(),mode);json.dump(value,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)
    fd=os.open(path.parent,os.O_DIRECTORY|os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def trusted(path,limit=32768):
    info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or stat.S_IMODE(info.st_mode) not in {0o400,0o600} or info.st_size>limit:
        raise ValueError('untrusted native lifecycle record')
    return json.loads(path.read_bytes())


def module(name):
    spec=importlib.util.spec_from_file_location(name.replace('-','_'),SOURCE/(name+'.py'))
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def target():
    if os.geteuid()!=0 or Path('/etc/hostname').read_text().strip()!='apx-host' or Path('/sys/class/dmi/id/product_name').read_text().strip()!='82JU':raise ValueError('pilot identity differs')
    if Path('/sys/class/block/nvme0n1/device/serial').read_text().strip()!='S4DYNX0R253702':raise ValueError('SSD identity differs')
    if Path('/sys/class/power_supply/ADP0/online').read_text().strip()!='1':raise ValueError('Liga o carregador antes de preparar Windows.')
    module('apx-native-boot-runner-v1').validate_secure_boot_policy()


def state(record,phase,progress,message):
    write(STATE,dict(schema=1,profile='apx-environment-management-v1',action=record.get('action','native-create-v3'),
        target=record['target'],phase=phase,progress=progress,message=message,updated_at=int(time.time())),0o600)


@contextmanager
def mounted(device,readonly=True):
    directory=Path(tempfile.mkdtemp(prefix='apx-native-v3-',dir='/run'))
    try:
        command('mount','-o','ro,nosuid,nodev,noexec' if readonly else 'rw,nosuid,nodev,noexec',device,str(directory))
        try:yield directory
        finally:command('umount',str(directory))
    finally:directory.rmdir()


def layout():return json.loads(command('sfdisk','--json',DISK))['partitiontable']


def measured_capacity(plan,path):
    usage=os.statvfs(path)
    used=(usage.f_blocks-usage.f_bfree)*usage.f_frsize
    headroom=16*1024**3
    if used+headroom>plan['apx_payload_bytes']:
        raise ValueError('A cópia e os restantes dados não cabem no APX após a migração.')
    return dict(schema=3,profile='apx-native-measured-capacity-v3',
                plan_sha256=plan['plan_sha256'],used_bytes=used,
                apx_payload_bytes=plan['apx_payload_bytes'],headroom_bytes=headroom)


def validate_capacity_proof(plan,job):
    capacity=trusted(job/'capacity.json')
    current=measured_capacity(plan,job)
    if capacity.get('schema')!=3 or capacity.get('profile')!='apx-native-measured-capacity-v3' or \
            capacity.get('plan_sha256')!=plan['plan_sha256'] or \
            capacity.get('apx_payload_bytes')!=plan['apx_payload_bytes'] or \
            capacity.get('headroom_bytes')!=current['headroom_bytes'] or \
            type(capacity.get('used_bytes')) is not int or \
            capacity['used_bytes']>plan['apx_payload_bytes']-current['headroom_bytes']:
        raise ValueError('verified backup capacity proof differs')
    return current


def display_drivers():
    result=[]
    with mounted(DISK+'p3') as root:
        store=root/'Windows/System32/DriverStore/FileRepository'
        for directory in sorted(store.iterdir()):
            if not re.fullmatch(r'(?:nv|u)[a-z0-9_.]+_amd64_[0-9a-f]{16}',directory.name) or not directory.is_dir() or directory.is_symlink():continue
            for inf in directory.glob('*.inf'):
                raw=inf.read_bytes();text=raw.decode('utf-16' if raw[:2] in (b'\xff\xfe',b'\xfe\xff') else 'utf-8',errors='replace')
                if re.search(r'^\s*Class\s*=\s*Display\s*$',text,re.MULTILINE|re.IGNORECASE):result.append(directory.name);break
    if not any(x.startswith('nv') for x in result) or not any(x.startswith('u') for x in result):raise ValueError('Não foram encontrados os controladores NVIDIA e AMD do Windows atual.')
    return result


def copy_display_driver_trees(job,names):
    """Stage exact read-only source packages inside a private replacement WIM."""
    if not names or len(names)>8 or any(not re.fullmatch(r'[a-z0-9_.]+_amd64_[0-9a-f]{16}',name) for name in names):
        raise ValueError('invalid replacement display driver list')
    destination=job/'drivers'
    if destination.exists():raise ValueError('replacement driver staging already exists')
    destination.mkdir(mode=0o700)
    total=count=0
    with mounted(DISK+'p3') as root:
        store=root/'Windows/System32/DriverStore/FileRepository'
        for name in names:
            source=store/name
            if source.is_symlink() or not source.is_dir():raise ValueError('original Windows driver package changed')
            output=destination/name;output.mkdir(mode=0o700)
            for item in source.rglob('*'):
                info=item.lstat();relative=item.relative_to(source);target=output/relative
                count+=1
                if count>50000 or item.is_symlink():raise ValueError('replacement driver package is unsafe')
                if stat.S_ISDIR(info.st_mode):target.mkdir(parents=True,exist_ok=True,mode=0o700)
                elif stat.S_ISREG(info.st_mode):
                    total+=info.st_size
                    if total>4*1024**3:raise ValueError('replacement driver packages exceed the pilot limit')
                    target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                    shutil.copyfile(item,target);os.chmod(target,0o600)
                else:raise ValueError('replacement driver package contains a special file')
    return dict(packages=len(names),files=count,bytes=total)


def job_path(generation):
    if not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',generation):raise ValueError('invalid generation')
    return ROOT/'migrations-v3'/generation


def prepare(generation,token):
    target()
    if LOCK.read_text().strip()!=token:raise ValueError('Hub management token differs')
    preview=trusted(Path('/run/apx/native-plans-v3')/(generation+'.json'))
    plan=validate_windows_install_plan(preview['plan'])
    if plan['new']['generation']!=generation or preview['target']!=plan['new']['name']:raise ValueError('selected plan differs')
    if plan['profile']=='apx-native-slot-reuse-plan-v3':
        return prepare_replacement(preview,plan,generation)
    if canonical_layout(layout())!=canonical_layout(plan['before']):raise ValueError('O disco mudou desde a verificação.')
    if PENDING.exists():raise ValueError('Existe uma operação Windows pendente.')
    # Refresh capacity with current measurements but require the same reviewed
    # partition extents. UUIDs are generated deterministically from generation.
    planner=module('apx-native-windows-plan-v3')
    current=planner.preview(preview['target'],preview['description'],preview['size_gib'],generation=generation)
    if canonical_layout(current['plan']['after'])!=canonical_layout(plan['after']):raise ValueError('O plano de espaço mudou.')
    job=job_path(generation);job.mkdir(parents=True,mode=0o700)
    record=dict(schema=3,profile='apx-native-job-v3',generation=generation,target=preview['target'],description=preview['description'],stage='preparing',plan_sha256=plan['plan_sha256'],existing_size_gib=plan['existing']['size_gib'],new_size_gib=plan['new']['size_gib'])
    write(job/'plan.json',plan);write(job/'job.json',record);write(PENDING,record)
    state(record,'applying',5,'A preparar uma cópia verificada do Windows atual…')
    drivers=display_drivers()
    template=Path('/usr/share/apx/native-windows-lifecycle-v1/winpe/apx-media.cmd').read_text()
    assets=render(plan,template,display_drivers=drivers)
    (job/'apx-media.cmd').write_bytes(assets['script'].encode());(job/'apx-expected.ini').write_bytes(assets['contract'].encode())
    write(job/'assets.json',{k:v for k,v in assets.items() if k not in {'script','contract'}})
    prepare_images(Path(DISK+'p3'),job/'images',plan['existing']['size_gib']*1024**3,
        prepared_metadata=('APX-'+generation+'.ini',assets['contract'].encode()),plan_sha256=plan['plan_sha256'])
    state(record,'applying',30,'A preparar o instalador independente…')
    with mounted(DISK+'p4') as media:
        shutil.copyfile(media/'sources/boot.wim',job/'boot.wim')
    commands=f'add "{job}/apx-media.cmd" /Windows/System32/apx-media.cmd\nadd "{job}/apx-expected.ini" /Windows/System32/apx-expected.ini\n'
    command('wimlib-imagex','update',str(job/'boot.wim'),'2','--check',input=commands)
    command('wimlib-imagex','verify',str(job/'boot.wim'))
    state(record,'applying',40,'A preparar a migração e a recuperação…')
    builder=module('build-native-windows-uki-v3');builder.build(job);builder.build(job,rollback=True)
    write(job/'capacity.json',measured_capacity(plan,job))
    record['stage']='prepared';write(job/'job.json',record);write(PENDING,record)
    state(record,'prepared',45,'Preparação concluída. Confirma a migração e o reinício no Hub.')


def prepare_replacement(preview,plan,generation):
    if PENDING.exists():raise ValueError('Existe uma operação Windows pendente.')
    if canonical_layout(layout())!=canonical_layout(plan['before']):raise ValueError('O espaço Windows mudou.')
    if trusted(ROOT/'free-slot-v3.json')!=plan['slot_marker'] or \
            trusted(ROOT/'instances-v3/windows.json')!=plan['original_record']:
        raise ValueError('O espaço Windows livre ou a instalação original mudou.')
    planner=module('apx-native-windows-plan-v3')
    current=planner.preview(preview['target'],preview['description'],preview['size_gib'],generation=generation)
    if current['plan']!=plan:raise ValueError('O plano do espaço reutilizável mudou.')
    job=job_path(generation);job.mkdir(parents=True,mode=0o700)
    record=dict(schema=3,profile='apx-native-job-v3',generation=generation,target=preview['target'],
                description=preview['description'],stage='preparing',mode='slot-reuse',
                plan_sha256=plan['plan_sha256'],existing_size_gib=plan['existing']['size_gib'],
                new_size_gib=plan['new']['size_gib'])
    write(job/'plan.json',plan);write(job/'job.json',record);write(PENDING,record)
    state(record,'applying',5,'A preparar o novo instalador Windows…')
    drivers=display_drivers()
    template=Path('/usr/share/apx/native-windows-lifecycle-v1/winpe/apx-media.cmd').read_text()
    assets=render(plan,template,display_drivers=drivers)
    (job/'apx-media.cmd').write_bytes(assets['script'].encode())
    (job/'apx-expected.ini').write_bytes(assets['contract'].encode())
    write(job/'assets.json',{k:v for k,v in assets.items() if k not in {'script','contract'}})
    write(job/'drivers.json',copy_display_driver_trees(job,drivers))
    with mounted(DISK+'p4') as media:
        shutil.copyfile(media/'sources/boot.wim',job/'boot.wim')
    commands=f'add "{job}/apx-media.cmd" /Windows/System32/apx-media.cmd\nadd "{job}/apx-expected.ini" /Windows/System32/apx-expected.ini\n'
    commands+=''.join(f'add "{job}/drivers/{name}" "/APXDrivers/{name}"\n' for name in drivers)
    command('wimlib-imagex','update',str(job/'boot.wim'),'2','--check',input=commands)
    command('wimlib-imagex','verify',str(job/'boot.wim'))
    write(job/'capacity.json',measured_capacity(plan,job))
    record['stage']='prepared-reuse';write(job/'job.json',record);write(PENDING,record)
    state(record,'prepared',45,'Novo instalador preparado. Confirma a instalação no espaço Windows reservado.')


def create_entry(partition,label,loader):
    before=command('efibootmgr','-v');order=re.search(r'^BootOrder:\s*(.+)$',before,re.MULTILINE).group(1)
    if not order.startswith('0005,') or re.search(r'^BootNext:',before,re.MULTILINE):raise ValueError('Linux boot order changed or another one-shot boot is armed')
    part=next(p for p in layout()['partitions'] if p['node']==DISK+'p'+str(partition))
    existing=find_matching_entry(before,partition,part['uuid'],label,loader)
    if existing is not None:return existing
    identities=set(re.findall(r'^Boot([0-9A-F]{4})\*?\s',before,re.MULTILINE))
    command('efibootmgr','--create-only','--disk',DISK,'--part',str(partition),'--label',label,'--loader',loader)
    after=command('efibootmgr','-v');added=set(re.findall(r'^Boot([0-9A-F]{4})\*?\s',after,re.MULTILINE))-identities
    if len(added)!=1 or re.search(r'^BootOrder:\s*(.+)$',after,re.MULTILINE).group(1)!=order:raise ValueError('firmware entry creation was not isolated')
    entry=added.pop()
    line=next(line for line in after.splitlines() if re.match(r'^Boot'+entry+r'\*?\s',line))
    if ('hd('+str(partition)+',gpt,'+part['uuid']+',').lower() not in line.lower() or loader.lower() not in line.lower():
        raise ValueError('new firmware entry identifies a different partition or loader')
    if find_matching_entry(after,partition,part['uuid'],label,loader)!=entry:
        raise ValueError('new firmware entry label or identity differs')
    return entry


def find_matching_entry(firmware,partition,partuuid,label,loader):
    """Reuse only one exact entry; reject aliases to the same EFI target."""
    expected_hd=('HD('+str(partition)+',GPT,'+partuuid+',').lower()
    expected_loader=('File('+loader+')').lower()
    matching=[]
    for line in firmware.splitlines():
        found=re.match(r'^Boot([0-9A-F]{4})\*?\s+(.+)$',line)
        if not found:continue
        entry,body=found.groups()
        owns_target=expected_hd in body.lower() and expected_loader in body.lower()
        owns_label=body.startswith(label+' ')
        if owns_target or owns_label:
            if not (owns_target and owns_label):raise ValueError('native firmware entry aliases a different target')
            matching.append(entry)
    if len(matching)>1:raise ValueError('duplicate native firmware entries')
    return matching[0] if matching else None


def retire_maintenance(job,record):
    # Authorization is retired first; cleanup never selects entries by label.
    write(job/'authorization.json',dict(state='retired',generation=record['generation']))
    entry=record.get('maintenance_entry')
    filename=record.get('maintenance_file')
    if entry:
        firmware=command('efibootmgr','-v')
        lines=[line for line in firmware.splitlines() if re.match(r'^Boot'+re.escape(entry)+r'\*?\s',line)]
        if lines:
            expected='\\EFI\\APX\\'+filename
            if expected.lower() not in lines[0].lower() or 'HD(1,GPT,'.lower() not in lines[0].lower():raise ValueError('maintenance firmware identity changed')
            command('efibootmgr','-b',entry,'-B')
    if filename:
        if filename!='native-v3-'+record['generation']+'-'+record['offline_action']+'.efi':raise ValueError('maintenance filename changed')
        path=Path('/boot/EFI/APX')/filename
        if path.exists():
            if path.is_symlink() or image_hash(path)!=record['maintenance_sha256']:raise ValueError('maintenance file changed')
            path.unlink();command('sync')


def restore_installer(job,record):
    previous=job/'previous-boot.wim'
    if previous.exists():
        with mounted(DISK+'p4',False) as media:
            target=media/'sources/boot.wim'
            current=image_hash(target)
            if current not in {image_hash(job/'boot.wim'),image_hash(previous)}:raise ValueError('installer media changed after preparation')
            shutil.copyfile(previous,target);command('sync')
    entry=record.get('setup_entry')
    if entry:
        firmware=command('efibootmgr','-v')
        lines=[line for line in firmware.splitlines() if re.match(r'^Boot'+re.escape(entry)+r'\*?\s',line)]
        if lines:
            if 'APX setup '+record['generation'][:8] not in lines[0] or 'HD(4,GPT,'.lower() not in lines[0].lower() or '\\EFI\\BOOT\\BOOTX64.EFI'.lower() not in lines[0].lower():raise ValueError('setup firmware identity changed')
            command('efibootmgr','-b',entry,'-B')


def launch_setup(job,record,plan):
    """Mark setup as started before any p5/p6 write; old-GPT rollback ends here."""
    generation=record['generation']
    record['stage']='installing'
    record.pop('error',None)
    write(job/'job.json',record);write(PENDING,record)
    state(record,'applying',65,'A preparar a nova instalação Windows…')
    assets=trusted(job/'assets.json')
    command('mkntfs','-F','-Q','-L',assets['windows_label'],DISK+'p5')
    command('mkfs.fat','-F','32','-n',assets['efi_label'],DISK+'p6')
    with mounted(DISK+'p5',False) as root:
        (root/'APX').mkdir();shutil.copyfile(job/'apx-expected.ini',root/'APX/install-contract-v3.ini')
    with mounted(DISK+'p6',False) as root:
        dest=root/'EFI/APX/native-windows';dest.mkdir(parents=True);shutil.copyfile(job/'apx-expected.ini',dest/'install-contract-v3.ini')
    with mounted(DISK+'p4',False) as root:
        dest=root/assets['media_directory'].replace('\\','/');dest.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(job/'apx-expected.ini',dest/'install-contract-v3.ini')
        if not (job/'previous-boot.wim').exists():shutil.copyfile(root/'sources/boot.wim',job/'previous-boot.wim')
        shutil.copyfile(job/'boot.wim',root/'sources/boot.wim');command('sync')
    entry=create_entry(4,'APX setup '+generation[:8],'\\EFI\\BOOT\\BOOTX64.EFI')
    record['setup_entry']=entry;write(job/'job.json',record);write(PENDING,record)
    state(record,'applying',70,'A reiniciar para instalar o novo Windows…');reboot_entry(entry)


def reboot_entry(entry):
    command('efibootmgr','-n',entry)
    try:
        if not re.search(r'^BootNext:\s*'+entry+r'\s*$',command('efibootmgr'),re.MULTILINE):raise ValueError('BootNext verification failed')
        command('systemctl','--no-block','reboot')
    except Exception:
        command('efibootmgr','-N');raise


def activate(generation,token,rollback=False):
    target()
    if LOCK.read_text().strip()!=token:raise ValueError('Hub management token differs')
    job=job_path(generation);record=trusted(job/'job.json');plan=validate_windows_install_plan(trusted(job/'plan.json'))
    if trusted(PENDING)['generation']!=generation:raise ValueError('pending generation differs')
    if plan['profile']=='apx-native-slot-reuse-plan-v3':
        if rollback:raise ValueError('slot reuse has no GPT rollback')
        return activate_replacement(job,record,plan)
    # Once setup is launched, its new partitions may contain owner data.
    # Restoring the old GPT would destroy that data, even after setup fails.
    if record['stage'] not in ({'offline'} if rollback else {'prepared'}):raise ValueError('native job is not ready for this action')
    if rollback and not offline_rollback_allowed(record['stage'],record.get('error')):raise ValueError('rollback requires a failed offline migration')
    action='rollback' if rollback else 'relocate'
    expected=plan['after'] if rollback else plan['before']
    if canonical_layout(layout())!=canonical_layout(expected):raise ValueError('disk changed before activation')
    if not rollback:
        validate_capacity_proof(plan,job)
        manifest=trusted(job/'images/manifest.json')
        if manifest.get('profile')!='apx-native-image-backup-v3' or manifest.get('state')!='verified-images' or manifest.get('plan_sha256')!=plan['plan_sha256']:
            raise ValueError('verified Windows backup missing')
        source=manifest.get('source_fingerprint')
        if source is None or source.get('bytes')!=plan['before']['partitions'][2]['size']*plan['before']['sectorsize']:
            raise ValueError('backup source extent differs from the migration plan')
        if source_fingerprint(Path(DISK+'p3'))!=source:
            raise ValueError('O Windows atual mudou depois da cópia; prepara uma nova migração.')
    image=job/('maintenance-'+action)/'maintenance.efi'
    destination=Path('/boot/EFI/APX')/('native-v3-'+generation+'-'+action+'.efi')
    if destination.exists():raise ValueError('maintenance image already published')
    shutil.copyfile(image,destination);os.chmod(destination,0o644);command('sync')
    write(job/'authorization.json',dict(schema=3,profile='apx-native-offline-authorization-v3',generation=generation,plan_sha256=plan['plan_sha256'],action=action,state='approved'))
    entry=create_entry(1,'APX native '+action+' '+generation[:8],'\\EFI\\APX\\'+destination.name)
    record.update(stage='offline',offline_action=action,maintenance_entry=entry,maintenance_file=destination.name,maintenance_sha256=image_hash(destination))
    write(job/'job.json',record);write(PENDING,record)
    state(record,'applying',50,'A reiniciar para reorganizar o espaço Windows…');reboot_entry(entry)


def activate_replacement(job,record,plan):
    if record['stage']!='prepared-reuse' or record.get('plan_sha256')!=plan['plan_sha256']:
        raise ValueError('replacement installer is not prepared')
    if canonical_layout(layout())!=canonical_layout(plan['before']) or \
            trusted(ROOT/'free-slot-v3.json')!=plan['slot_marker'] or \
            trusted(ROOT/'instances-v3/windows.json')!=plan['original_record']:
        raise ValueError('the reusable Windows slot changed')
    validate_capacity_proof(plan,job)
    launch_setup(job,record,plan)


def retry_install(generation,token):
    target()
    if LOCK.read_text().strip()!=token:raise ValueError('Hub management token differs')
    record=trusted(PENDING)
    if record['generation']!=generation or record['stage']!='installing' or not record.get('error') or record.get('install_failure_kind')!='winpe-failed':
        raise ValueError('selected Windows installation is not failed')
    attempts=record.get('install_retries',0)
    if type(attempts) is not int or not 0<=attempts<2:
        raise ValueError('Windows installation retry limit reached')
    job=job_path(generation);plan=validate_windows_install_plan(trusted(job/'plan.json'))
    if record['plan_sha256']!=plan['plan_sha256'] or canonical_layout(layout())!=canonical_layout(plan['after']):
        raise ValueError('Windows installation plan or GPT changed')
    assets=trusted(job/'assets.json')
    with mounted(DISK+'p4') as media:
        failed=(media/assets['media_directory'].replace('\\','/')/'install-status-v3.ini').read_bytes()
    validate_failed_install_status(failed,plan)
    setup_part=plan['after']['partitions'][3]
    firmware=command('efibootmgr','-v')
    if not re.search(r'^BootCurrent:\s*0005\s*$',firmware,re.MULTILINE) or \
            not re.search(r'^BootOrder:\s*0005,',firmware,re.MULTILINE) or \
            re.search(r'^BootNext:',firmware,re.MULTILINE):
        raise ValueError('Linux boot authority changed before Windows retry')
    entry=find_matching_entry(firmware,4,setup_part['uuid'],
                              'APX setup '+generation[:8],'\\EFI\\BOOT\\BOOTX64.EFI')
    if entry is None or entry!=record.get('setup_entry'):
        raise ValueError('selected Windows setup firmware entry differs')
    record['install_retries']=attempts+1
    record.pop('error',None)
    record.pop('install_failure_kind',None)
    write(job/'job.json',record);write(PENDING,record)
    state(record,'applying',70,'A repetir apenas a instalação Windows nova…')
    reboot_entry(entry)


def delete_instance(generation,token):
    """Clear only the selected new p5/p6 instance, retaining its 80 GiB slot."""
    target()
    if LOCK.read_text().strip()!=token:raise ValueError('Hub management token differs')
    job=job_path(generation);plan=validate_windows_install_plan(trusted(job/'plan.json'))
    source=plan if plan['profile']=='apx-native-migration-plan-v3' else plan['source_plan']
    table=layout()
    if canonical_layout(table)!=canonical_layout(source['after']) or canonical_layout(table)!=canonical_layout(plan['after']):
        raise ValueError('native slot GPT changed before deletion')
    original=trusted(ROOT/'instances-v3/windows.json')
    selected_path=ROOT/'instances-v3'/(plan['new']['name']+'.json')
    archive=ROOT/'retired-v3'/(plan['new']['name']+'-'+generation+'.json')
    if PENDING.exists():
        pending=trusted(PENDING)
        if pending.get('profile')!='apx-native-job-v3' or pending.get('stage')!='deleting' or \
                pending.get('generation')!=generation or pending.get('target')!=plan['new']['name'] or \
                pending.get('plan_sha256')!=plan['plan_sha256']:
            raise ValueError('selected native deletion differs')
        selected=pending.get('selected_record')
        if type(selected) is not dict:
            raise ValueError('native deletion record missing')
    else:
        if archive.exists() or (ROOT/'free-slot-v3.json').exists():
            raise ValueError('native slot is already retired or free')
        selected=trusted(selected_path)
        if selected.get('name')!=plan['new']['name'] or selected.get('generation')!=generation or selected.get('state')!='ready':
            raise ValueError('selected Windows changed before deletion')
        validate_instances([original,selected],table,plan['disk_serial'])
        pending=dict(schema=3,profile='apx-native-job-v3',generation=generation,target=selected['name'],
                     stage='deleting',action='native-delete-v3',plan_sha256=plan['plan_sha256'],selected_record=selected)
        write(PENDING,pending)
        write(selected_path,dict(selected,state='deleting'))
    if selected.get('generation')!=generation or selected.get('name')!=plan['new']['name'] or \
            selected.get('windows_partuuid','').lower()!=plan['new']['partuuid'].lower() or \
            selected.get('esp_partuuid','').lower()!=plan['new']['esp_partuuid'].lower() or \
            selected.get('windows_boot_entry') in {None,original.get('windows_boot_entry')}:
        raise ValueError('native deletion partition or firmware identity differs')
    if selected.get('state')!='ready':raise ValueError('native deletion source was not ready')
    validate_instances([original,selected],table,plan['disk_serial'])
    if selected_path.exists():
        current=trusted(selected_path)
        if current==selected and PENDING.exists():
            write(selected_path,dict(selected,state='deleting'))
            current=trusted(selected_path)
        if current!=dict(selected,state='deleting'):
            raise ValueError('native deletion active record changed')
    elif not archive.exists() or trusted(archive)!=dict(selected,state='deleting'):
        raise ValueError('native deletion archived record differs')
    firmware=command('efibootmgr','-v')
    if not re.search(r'^BootCurrent:\s*0005\s*$',firmware,re.MULTILINE) or \
            not re.search(r'^BootOrder:\s*0005,',firmware,re.MULTILINE) or \
            re.search(r'^BootNext:',firmware,re.MULTILINE):
        raise ValueError('Linux boot authority changed before native deletion')
    entry=find_matching_entry(firmware,6,plan['new']['esp_partuuid'],
                              'APX '+selected['name'],'\\EFI\\Microsoft\\Boot\\bootmgfw.efi')
    if re.search(r'^Boot'+re.escape(selected['windows_boot_entry'])+r'\*?\s',firmware,re.MULTILINE) and \
            entry!=selected['windows_boot_entry']:
        raise ValueError('selected native firmware number was reassigned')
    if entry is not None:
        if entry!=selected['windows_boot_entry']:
            raise ValueError('selected native firmware entry differs')
        command('efibootmgr','-b',entry,'-B')
        if find_matching_entry(command('efibootmgr','-v'),6,plan['new']['esp_partuuid'],
                               'APX '+selected['name'],'\\EFI\\Microsoft\\Boot\\bootmgfw.efi') is not None:
            raise ValueError('selected native firmware entry remained after deletion')
    state(pending,'applying',20,'A limpar apenas o Windows novo e o seu EFI…')
    for number,key in ((5,'partuuid'),(6,'esp_partuuid')):
        part=next(p for p in table['partitions'] if p['node']==DISK+'p'+str(number))
        if part['uuid'].lower()!=plan['new'][key].lower():raise ValueError('native slot partition changed')
        wipe_block_partition(Path(part['node']),part['size']*table['sectorsize'],part['uuid'].lower(),number)
    if selected_path.exists():
        archive.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        os.replace(selected_path,archive)
    marker=free_slot_record(source,table,[original],generation)
    write(ROOT/'free-slot-v3.json',marker)
    PENDING.unlink()
    state(pending,'complete',100,'Windows de teste apagado. O espaço fica disponível para outro Windows.')


def finalize():
    target();record=trusted(PENDING);generation=record['generation'];job=job_path(generation);plan=validate_windows_install_plan(trusted(job/'plan.json'))
    if record['stage'] in {'prepared','prepared-reuse'}:
        state(record,'prepared',45,'Preparação concluída. Confirma a migração e o reinício no Hub.');return
    if record['stage']=='offline':
        expected=generation+':'+plan['plan_sha256']+':'+record['offline_action']+':complete:write-gpt'
        status=(Path('/boot/EFI/APX/recovery')/('native-v3-'+generation+'.status')).read_text().strip()
        if status!=expected:raise ValueError('A migração não terminou. É necessário recuperar a cópia guardada.')
        desired=plan['before'] if record['offline_action']=='rollback' else plan['after']
        if canonical_layout(layout())!=canonical_layout(desired):raise ValueError('offline result GPT differs')
        # Retire authorization before installation so a stale maintenance image
        # cannot relocate a Windows that has since been used.
        retire_maintenance(job,record)
        if record['offline_action']=='rollback':
            restore_installer(job,record)
            record['stage']='rolled-back';write(job/'job.json',record);PENDING.unlink();state(record,'complete',100,'O Windows anterior foi reposto.');return
        launch_setup(job,record,plan);return
    if record['stage']=='installing':
        if canonical_layout(layout())!=canonical_layout(plan['after']):raise ValueError('installation GPT differs')
        assets=trusted(job/'assets.json')
        with mounted(DISK+'p4') as media:
            path=media/assets['media_directory'].replace('\\','/')/'install-status-v3.ini'
            media_status=path.read_bytes()
        try:
            validate_failed_install_status(media_status,plan)
        except ValueError:
            pass
        else:
            record['install_failure_kind']='winpe-failed'
            write(job/'job.json',record);write(PENDING,record)
            raise ValueError('A instalação Windows nova falhou; a repetição exige confirmação no Hub.')
        validate_install_status(media_status,plan)
        with mounted(DISK+'p6') as root:
            efi_status=(root/'EFI/APX/native-windows/install-status-v3.ini').read_bytes()
            if efi_status!=media_status:raise ValueError('new Windows EFI and installer status differ')
            if not (root/'EFI/Microsoft/Boot/BCD').is_file():raise ValueError('new Windows BCD absent')
            result=command('sbverify','--list',str(root/'EFI/Microsoft/Boot/bootmgfw.efi'))
            if 'Microsoft' not in result:raise ValueError('new Windows boot manager signature differs')
        entry=create_entry(6,'APX '+record['target'],'\\EFI\\Microsoft\\Boot\\bootmgfw.efi')
        reuse=plan['profile']=='apx-native-slot-reuse-plan-v3'
        legacy=trusted(ROOT/'windows.json');records=[]
        if reuse:
            if trusted(ROOT/'free-slot-v3.json')!=plan['slot_marker'] or trusted(ROOT/'instances-v3/windows.json')!=plan['original_record']:
                raise ValueError('the reusable Windows slot changed during installation')
            records.append(plan['original_record'])
        else:
            part=plan['after']['partitions'][2];esp=plan['after']['partitions'][0]
            records.append(dict(schema=3,profile='apx-native-instance-v3',name='windows',generation=legacy['generation'],state='ready',system_kind='windows-native',disk_id=plan['disk_id'],disk_serial=plan['disk_serial'],windows_partuuid=part['uuid'],start_sector=part['start'],size_sectors=part['size'],esp_partuuid=esp['uuid'],linux_boot_entry=legacy['linux_boot_entry'],windows_boot_entry=legacy['windows_boot_entry'],efi_path='/EFI/Microsoft/Boot/bootmgfw.efi',display_name=legacy['display_name'],description=legacy['description']))
        part=plan['after']['partitions'][4];esp=plan['after']['partitions'][5]
        records.append(dict(schema=3,profile='apx-native-instance-v3',name=record['target'],generation=generation,state='ready',system_kind='windows-native',disk_id=plan['disk_id'],disk_serial=plan['disk_serial'],windows_partuuid=part['uuid'],start_sector=part['start'],size_sectors=part['size'],esp_partuuid=esp['uuid'],linux_boot_entry=records[0]['linux_boot_entry'],windows_boot_entry=entry,efi_path='/EFI/Microsoft/Boot/bootmgfw.efi',display_name=record['target'],description=record['description']))
        validate_instances(records,layout(),plan['disk_serial'])
        for value in records:write(ROOT/'instances-v3'/(value['name']+'.json'),value)
        if reuse:(ROOT/'free-slot-v3.json').unlink()
        restore_installer(job,record)
        record['stage']='ready';write(job/'job.json',record);PENDING.unlink();state(record,'complete',100,'Novo Windows criado. Abre-o no Hub para concluir a configuração inicial.');return
    raise ValueError('A operação Windows precisa de recuperação explícita.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','activate','rollback','retry','delete','finalize']);parser.add_argument('--generation');parser.add_argument('--lock-token');args=parser.parse_args()
    try:
        if args.action=='finalize':finalize()
        elif args.action=='prepare':prepare(args.generation,args.lock_token)
        elif args.action=='retry':retry_install(args.generation,args.lock_token)
        elif args.action=='delete':delete_instance(args.generation,args.lock_token)
        else:activate(args.generation,args.lock_token,args.action=='rollback')
    except Exception as error:
        if PENDING.exists():
            record=trusted(PENDING);record['error']=str(error)[-500:]
            if record['stage']=='preparing':
                record['stage']='preparation-failed';write(job_path(record['generation'])/'job.json',record)
                PENDING.unlink();state(record,'failed',0,str(error)[-300:])
            else:
                write(job_path(record['generation'])/'job.json',record);write(PENDING,record)
                state(record,'recovery-required',0,str(error)[-300:])
        raise
    finally:
        if args.lock_token and LOCK.exists() and LOCK.read_text().strip()==args.lock_token:LOCK.unlink()

if __name__=='__main__':main()
