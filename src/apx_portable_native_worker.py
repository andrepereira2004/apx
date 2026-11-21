"""Explicit portable Windows lifecycle, executed by future Host/Recovery units.

No commands run on import. Recovery is an independent ext4 root; its journal is
written/fsynced before boot handoffs and retained until Host completion.
"""
from pathlib import Path
import array
import fcntl
import json
import os
import re
import shutil
import stat
import subprocess
import time
from apx_portable_native import (RESERVE,GIB,STAGES,digest,plan_delete,validate_plan,
    validate_delete,sfdisk_script,canonical_layout)
from apx_portable_native_io import (STATE,IDENTITY,run,trusted,atomic,regular,file_hash,
    locked,disk_for,part,exact_layout,remap,identity_at,mounted,root_mounted,
    linux_first,entry,boot_next,retire,matching_entries,EFI_PATH,check_recovery)
from apx_portable_native_media import build,source_check
from apx_native_slot_wipe_v3 import zero_exact_fd

RECOVERY_STATE=Path('/var/lib/apx-native-v4')
MANAGEMENT_LOCK=Path('/run/apx/environment-management-v1.lock')
# Matches the existing authenticated Hub presentation contract.
MANAGEMENT_STATE=Path('/run/apx/environment-management-v1.json')
WINDOWS_PATH=r'\EFI\Microsoft\Boot\bootmgfw.efi'
SETUP_PATH=r'\EFI\BOOT\BOOTX64.EFI'


def state(job,stage,message=None,**changes):
    messages={'preparing':'A preparar os ficheiros de instalação Windows.',
        'prepared':'Windows preparado. Confirma a instalação e o reinício no Hub.',
        'root-shrunk':'Espaço Linux preparado; a configurar o novo Windows.',
        'table-written':'Partições verificadas; a preparar os volumes Windows.',
        'partitions-formatted':'A copiar os ficheiros de instalação Windows.',
        'media-ready':'Instalação preparada; a verificar o arranque.',
        'winpe-launched':'A iniciar o instalador Windows.',
        'delete-approved':'A preparar a remoção deste Windows.',
        'delete-wiping':'A eliminar os dados deste Windows. Esta etapa pode demorar.',
        'delete-wiped':'Dados eliminados; a recuperar o espaço para Linux.',
        'delete-table-written':'A integrar o espaço recuperado no Linux.',
        'offline-failed':'A operação parou. A recuperação e os registos foram preservados.',
        'rolled-back':'Preparação cancelada; espaço Linux recuperado.',
        'complete':'Operação Windows concluída.'}
    message=message or messages.get(stage,'A processar a operação Windows.')
    print('APX Windows: '+message,flush=True)
    job.update(stage=stage,updated_at=int(time.time()),**changes)
    path=RECOVERY_STATE/'active.json' if job.get('_recovery') else STATE/'pending.json'
    value={k:v for k,v in job.items() if not k.startswith('_')}
    atomic(path,value)
    if not job.get('_recovery'):
        atomic(MANAGEMENT_STATE,dict(schema=1,profile='apx-environment-management-v1',
            phase='prepared' if stage=='prepared' else 'applying',progress=0,
            action=job['action'],target=job['target'],message=message or stage))


def validate_job(job):
    if job.get('schema')!=4 or job.get('profile')!='apx-portable-native-job-v4' or job.get('action') not in {'create','delete','rollback','retry'}:
        raise ValueError('unknown native Recovery job')
    plan=validate_plan(job['plan'])
    if job.get('generation')!=plan['generation'] or job.get('target')!=plan['name']:
        raise ValueError('Recovery job instance differs')
    retries=job.get('retries',0)
    if type(retries) is not int or not 0<=retries<=2:raise ValueError('invalid explicit retry bound')
    if job['action'] in {'create','retry'} and job.get('stage') not in {'preparing','prepare-failed','rolled-back'}:
        media=job.get('media',{})
        if media.get('profile')!='apx-portable-native-media-v4' or media.get('generation')!=plan['generation'] or media.get('plan_sha256')!=plan['sha256'] or not media.get('files'):
            raise ValueError('generation-bound verified media is required before native writes')
    if job['action']=='delete':
        deletion=validate_delete(job['delete_plan'])
        if deletion['source_plan']!=plan:raise ValueError('delete job and selected native instance differ')
    return plan


def asserted_power():
    supplies=list(Path('/sys/class/power_supply').glob('*'))
    batteries=[p for p in supplies if (p/'type').is_file() and (p/'type').read_text().strip()=='Battery']
    if batteries and not any((p/'online').is_file() and (p/'online').read_text().strip()=='1' for p in supplies):
        raise ValueError('connect AC power before offline storage changes')


def devices_unmounted(table,uuids):
    mounts=json.loads(run('findmnt','-J','-o','MAJ:MIN,TARGET'))
    def values(items):
        for item in items:
            yield item.get('maj:min');yield from values(item.get('children',[]))
    mounted_ids=set(values(mounts.get('filesystems',[])))
    swaps=run('swapon','--noheadings','--raw','--show=NAME').splitlines()
    for uuid in uuids:
        node=part(table,uuid);info=Path(node).stat();device=f'{os.major(info.st_rdev)}:{os.minor(info.st_rdev)}'
        if device in mounted_ids or node in swaps or list((Path('/sys/dev/block')/device/'holders').iterdir()):
            raise ValueError('selected storage has active mounts, swap or holders')


def erase(table,p):
    node=part(table,p['uuid']);devices_unmounted(table,[p['uuid']])
    fd=os.open(node,os.O_RDWR|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        info=os.fstat(fd);size=array.array('Q',[0]);fcntl.ioctl(fd,0x80081272,size,True)
        if not stat.S_ISBLK(info.st_mode) or info.st_rdev!=Path(node).stat().st_rdev or size[0]!=p['size']*table['sectorsize']:
            raise ValueError('wipe device identity/length changed')
        zero_exact_fd(fd,size[0])
    finally:os.close(fd)


def write_table(disk,current,expected):
    observed=disk_for(expected['identity'])[1]
    if not exact_layout(observed,current):raise ValueError('GPT changed before offline write')
    table=remap(expected['table'],disk)
    def numbered(value):
        from apx_portable_native import partition_node
        return {next(n for n in range(1,129) if partition_node(disk,n)==p['node']):p for p in remap(value,disk)['partitions']}
    before=numbered(current);after=numbered(table)
    changed={n for n in before.keys()|after.keys() if before.get(n)!=after.get(n)}
    for number in sorted(changed&before.keys(),reverse=True):
        run('partx','--delete','--nr',str(number),disk)
    # Recovery itself remains mounted on a protected partition. A whole-disk
    # BLKRRPART is inappropriate; replace only admitted unmounted partitions.
    run('sfdisk','--no-reread','--no-tell-kernel','--wipe','never','--wipe-partitions','never',disk,input=sfdisk_script(table),timeout=60)
    for number in sorted(changed&after.keys()):
        run('partx','--add','--nr',str(number),disk)
    run('udevadm','settle',timeout=60)
    run('sfdisk','--verify',disk)
    observed=disk_for(expected['identity'])[1]
    if not exact_layout(observed,table):raise ValueError('full GPT write/readback differs')
    for p in table['partitions']:part(observed,p['uuid'])
    return observed


def assert_files(directory,manifest):
    files=manifest.get('files')
    if type(files) is not dict or not files or len(files)>100000:raise ValueError('invalid media manifest')
    actual={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    if actual!=set(files):raise ValueError('media file set changed')
    for relative,sha in files.items():
        path=Path(relative)
        if path.is_absolute() or '..' in path.parts or not re.fullmatch('[a-f0-9]{64}',sha):raise ValueError('unsafe media manifest')
        regular(directory/path)
        if file_hash(directory/path)!=sha:raise ValueError('media digest differs: '+relative)


def recovery_node(identity,table):return part(table,identity['recovery_partuuid'])


def queue(job):
    plan=validate_job(job);identity=plan['identity'];disk,table=disk_for(identity)
    recovery=recovery_node(identity,table)
    with mounted(recovery,fstype='ext4') as root:
        check_recovery(root,compare_host=True)
        directory=root/'var/lib/apx-native-v4';directory.mkdir(parents=True,mode=0o700,exist_ok=True)
        active=directory/'active.json'
        if active.exists():
            old=trusted(active)
            if old['generation']!=job['generation'] and old['stage'] not in {'complete','rolled-back'}:
                raise ValueError('another Recovery transaction remains active')
        atomic(active,{k:v for k,v in job.items() if not k.startswith('_')})
    linux_first(identity)
    number=entry(table,identity['esp_partuuid'],r'\EFI\Recovery\APX-Recovery.efi','APX Recovery')
    boot_next(number)
    state(job,'recovery-queued','A reiniciar para preparar o Windows em segurança.')
    run('systemctl','--no-block','reboot')


def prepare(preview):
    plan=validate_plan(preview['plan']);identity=plan['identity'];disk,table=disk_for(identity)
    if not exact_layout(table,plan['before']):raise ValueError('storage changed since preview')
    with mounted(recovery_node(identity,table),readonly=True,fstype='ext4') as recovery:
        check_recovery(recovery,compare_host=True)
    if (STATE/'pending.json').exists():raise ValueError('a portable native transaction already exists')
    job=dict(schema=4,profile='apx-portable-native-job-v4',action='create',target=plan['name'],
        generation=plan['generation'],plan=plan,stage='preparing',retries=0,
        description=preview.get('description',''),created_at=int(time.time()))
    state(job,'preparing','A verificar a ISO e a preparar a instalação Windows.')
    source=source_check(trusted(STATE/'source.json'))
    root=STATE/'jobs'/plan['generation']
    media=build(plan,source,root,int(run('blockdev','--getsize64',disk)))
    atomic(root/'media.json',media);job['media']=media
    if not exact_layout(disk_for(identity)[1],plan['before']):raise ValueError('GPT changed during preparation')
    # Device allocation grew during media/compilation; the preview reserved its
    # bounded staging allowance. Refuse rather than silently amend approval.
    allocated=allocated_bytes('/')
    if allocated>plan['used_bytes']:raise ValueError('prepared media exceeded approved Linux allocation allowance; create a new preview')
    state(job,'prepared','Windows preparado. Confirma no Hub para reiniciar e instalar.')


def allocated_bytes(root):
    match=re.search(r'^\s*Device allocated:\s*([0-9]+)\s*$',run('btrfs','filesystem','usage','--raw',root),re.M)
    if not match:raise ValueError('Btrfs allocation measurement unavailable')
    return int(match[1])


def load_instance(target,generation):
    from apx_portable_native import NAME,guid
    if not NAME.fullmatch(target) or target=='hub':raise ValueError('invalid native instance')
    guid(generation)
    value=trusted(STATE/'instances'/(target+'.json'))
    plan=validate_plan(value['plan'])
    if value.get('target')!=target or value.get('generation')!=generation or plan['name']!=target or plan['generation']!=generation:
        raise ValueError('native instance generation changed')
    return value


def verify_instance(value,table):
    plan=validate_plan(value['plan'])
    by_uuid={p['uuid']:p for p in table['partitions']}
    for p in plan['slots']:
        expected=dict(p,node=next(q['node'] for q in table['partitions'] if q['uuid']==p['uuid']))
        if by_uuid.get(p['uuid'])!=expected:raise ValueError('selected native slot changed')
    return plan


def boot_instance(value):
    if value['state']!='ready':raise ValueError('Windows is not ready for boot')
    identity=trusted(IDENTITY);disk,table=disk_for(identity);plan=verify_instance(value,table)
    from apx_portable_native import validate_identity
    validate_identity(identity,table,identity['serial'],identity['wwn'])
    with mounted(part(table,plan['slots'][0]['uuid']),readonly=True,fstype='ntfs3') as windows:
        for rel in ['Windows/System32/winload.efi','Windows/System32/config/SYSTEM']:
            if not (windows/rel).is_file():raise ValueError('Windows system file absent')
    with mounted(part(table,plan['slots'][1]['uuid']),readonly=True,fstype='vfat') as efi:
        for rel in ['EFI/Microsoft/Boot/bootmgfw.efi','EFI/Microsoft/Boot/BCD']:
            if not (efi/rel).is_file():raise ValueError('Windows boot file absent')
    linux_first(identity)
    number=entry(table,plan['slots'][1]['uuid'],WINDOWS_PATH,'APX Windows '+plan['name'])
    linux_first(identity);boot_next(number);run('systemctl','--no-block','reboot')


def delete_instance(value):
    source=validate_plan(value['plan']);identity=trusted(IDENTITY);disk,table=disk_for(identity)
    verify_instance(value,table)
    # Check the exact current installation layout before retiring firmware.
    from apx_portable_native import validate_identity
    validate_identity(identity,table,identity['serial'],identity['wwn'])
    identity=identity_at(table,identity)
    for slot in source['slots'][1::2]:retire(slot['uuid'])
    retired=dict(schema=4,profile='apx-portable-native-retirement-v4',name=source['name'],
        generation=source['generation'],source_plan_sha256=source['sha256'],state='deleting',
        layout_sha256=digest(table),efi_entries_retired=True)
    deletion=plan_delete(identity,table,source,retired,serial=identity['serial'],wwn=identity['wwn'])
    job=dict(schema=4,profile='apx-portable-native-job-v4',action='delete',target=source['name'],
        generation=source['generation'],plan=source,delete_plan=deletion,stage='delete-approved',retries=0)
    state(job,'delete-approved')
    value['state']='deleting';atomic(STATE/'instances'/(value['target']+'.json'),value)
    queue(job)


def purge_job(generation):
    from apx_portable_native import guid
    guid(generation);directory=STATE/'jobs'/generation
    if not directory.exists():return
    mounts=run('findmnt','-rn','-o','TARGET').splitlines()
    if any(p==str(directory) or p.startswith(str(directory)+'/') for p in mounts):
        raise ValueError('job still has mounts; preserve it for assisted cleanup')
    if directory.is_symlink() or not directory.is_dir():raise ValueError('job directory changed')
    shutil.rmtree(directory)


def host_action(action,target,generation):
    if action=='prepare':
        preview=trusted(STATE/'previews'/(generation+'.json'))
        if preview['plan']['name']!=target or time.time()-preview['created_at']>600:raise ValueError('native preview expired or target changed')
        return prepare(preview)
    if action=='boot':return boot_instance(load_instance(target,generation))
    if action=='delete' and not (STATE/'pending.json').exists():return delete_instance(load_instance(target,generation))
    job=trusted(STATE/'pending.json');plan=validate_job(job)
    if job['target']!=target or job['generation']!=generation:raise ValueError('pending native generation changed')
    if job.get('manual_recovery') and action!='delete':raise ValueError('unknown completion evidence requires operator recovery before retry')
    if action=='activate' and job['stage']=='prepared':
        job['stage']='approved';return queue(job)
    if action=='rollback':
        if job['stage'] in {'preparing','prepared','prepare-failed'}:
            if not exact_layout(disk_for(plan['identity'])[1],plan['before']):raise ValueError('GPT changed; cannot cancel prepared job')
            purge_job(generation)
            job['stage']='rolled-back';atomic(STATE/'history'/(generation+'.json'),job)
            (STATE/'pending.json').unlink();return
        if job['stage'] not in {'offline-failed','recovery-required'} or job.get('offline_stage') not in STAGES[:STAGES.index('winpe-launched')]:
            raise ValueError('rollback is prohibited after WinPE was launched')
        job.update(action='rollback',stage='rollback-approved');return queue(job)
    if action=='retry':
        if job['stage'] not in {'install-failed','offline-failed','recovery-required'} or job.get('retries',0)>=2:
            raise ValueError('retry unavailable or retry bound reached')
        job['retries']=job.get('retries',0)+1
        if job.get('offline_stage') in STAGES[:STAGES.index('winpe-launched')]:
            job['action']='create';job['stage']=job['offline_stage']
        else:job.update(action='retry',stage='retry-approved')
        return queue(job)
    if action=='delete' and job['action']=='delete' and job['stage']=='offline-failed':
        job['stage']=job['offline_stage'];return queue(job)
    if action=='delete' and job['stage'] in {'install-failed','recovery-required','offline-failed'}:
        # Explicitly discard an incomplete Windows using the same exact-slot
        # deletion path; no forced rollback of possibly changed native data.
        value=dict(target=target,generation=generation,plan=plan,state='failed')
        return delete_instance(value)
    raise ValueError('native action is not admitted in the current durable stage')


def offline_create(job):
    plan=validate_job(job);identity=plan['identity'];disk,table=disk_for(identity)
    stage=job['stage']
    if stage=='approved':
        if not exact_layout(table,plan['before']):raise ValueError('before-layout differs before shrink')
        devices_unmounted(table,[identity['root_partuuid']])
        with mounted(part(table,identity['root_partuuid']),fstype='btrfs',options=['subvolid=5']) as root:
            if run('blkid','-s','UUID','-o','value',part(table,identity['root_partuuid'])).strip()!=identity['root_uuid']:
                raise ValueError('Linux filesystem UUID differs')
            devices=run('btrfs','filesystem','show','--raw',root)
            if re.search(r'Total devices\s+1\b',devices) is None:raise ValueError('offline shrink requires the approved single-device Btrfs root')
            if allocated_bytes(root)>plan['used_bytes']:raise ValueError('Linux allocation exceeded the approved bound')
            run('btrfs','filesystem','resize',str(plan['retained_root_bytes']),root,timeout=3600)
            run('btrfs','filesystem','sync',root,timeout=180)
        state(job,'root-shrunk');stage=job['stage']
    if stage=='root-shrunk':
        devices_unmounted(table,[identity['root_partuuid']])
        if exact_layout(table,plan['before']):table=write_table(disk,table,{'identity':identity,'table':plan['after']})
        elif not exact_layout(table,plan['after']):raise ValueError('interrupted GPT write requires assisted recovery')
        state(job,'table-written');stage=job['stage']
    if not exact_layout(table,plan['after']):raise ValueError('after-layout differs')
    if stage=='table-written':
        devices_unmounted(table,[p['uuid'] for p in plan['slots']])
        windows,esp,msr,setup=[part(table,p['uuid']) for p in plan['slots']]
        suffix=plan['generation'].replace('-','')[:7].upper()
        run('mkfs.ntfs','-F','-Q','-L','APXW'+suffix,windows,timeout=600)
        for node,label in [(esp,'APXE'+suffix),(setup,'APXS'+suffix)]:run('mkfs.fat','-F','32','-n',label,node)
        run('wipefs','--all',msr)
        state(job,'partitions-formatted');stage=job['stage']
    if stage=='partitions-formatted':
        with mounted(part(table,identity['root_partuuid']),fstype='btrfs',options=['subvol=@']) as root:
            source=root/str(STATE).lstrip('/')/'jobs'/plan['generation']/'media'
            assert_files(source,job['media'])
            with mounted(part(table,plan['slots'][3]['uuid']),fstype='vfat') as setup:
                # The setup volume was formatted by this transaction. Never
                # delete foreign paths to make an unexpected volume fit.
                for p in source.iterdir():
                    if p.is_dir():shutil.copytree(p,setup/p.name,dirs_exist_ok=True)
                    else:shutil.copyfile(p,setup/p.name)
                verify_copied_media(setup,job['media'])
            atomic(root/str(IDENTITY).lstrip('/'),identity_at(table,identity))
        state(job,'media-ready');stage=job['stage']
    if stage=='media-ready':launch_winpe(job,table)


def verify_copied_media(directory,manifest):
    # FAT ownership is synthetic; require only paths and whole-file digests here.
    for relative,sha in manifest['files'].items():
        if not (directory/relative).is_file() or file_hash(directory/relative)!=sha:raise ValueError('copied WinPE source differs: '+relative)


def launch_winpe(job,table):
    plan=validate_job(job);identity=plan['identity']
    with mounted(part(table,plan['slots'][3]['uuid']),fstype='vfat') as setup:
        verify_copied_media(setup,job['media'])
        (setup/'APX/status.ini').unlink(missing_ok=True)
    number=entry(table,plan['slots'][3]['uuid'],SETUP_PATH,'APX Setup '+plan['name'])
    linux_first(identity)
    state(job,'winpe-launched') # durable before arming; no automatic retry loop
    boot_next(number);run('sync');run('systemctl','--no-block','reboot')


def offline_retry(job):
    plan=validate_job(job);disk,table=disk_for(plan['identity'])
    if not exact_layout(table,plan['after']):raise ValueError('retry GPT checkpoint differs')
    # Formatting only this instance is an explicit retry, bounded on the Host.
    devices_unmounted(table,[p['uuid'] for p in plan['slots']])
    retire(plan['slots'][1]['uuid'])
    run('mkfs.ntfs','-F','-Q','-L','APXW'+plan['generation'].replace('-','')[:7].upper(),part(table,plan['slots'][0]['uuid']),timeout=600)
    run('mkfs.fat','-F','32','-n','APXE'+plan['generation'].replace('-','')[:7].upper(),part(table,plan['slots'][1]['uuid']))
    launch_winpe(job,table)


def offline_rollback(job):
    plan=validate_job(job);identity=plan['identity'];disk,table=disk_for(identity)
    if not exact_layout(table,plan['before']):
        if not exact_layout(table,plan['after']):raise ValueError('rollback layout differs')
        devices_unmounted(table,[identity['root_partuuid']]+[p['uuid'] for p in plan['slots']])
        for p in plan['slots']:retire(p['uuid']);erase(table,p)
        table=write_table(disk,table,{'identity':identity,'table':plan['before']})
    with mounted(part(table,identity['root_partuuid']),fstype='btrfs',options=['subvol=@']) as root:
        run('btrfs','filesystem','resize','max',root,timeout=3600)
        atomic(root/str(IDENTITY).lstrip('/'),identity_at(table,identity))
    state(job,'rolled-back');linux_first(identity);run('systemctl','--no-block','reboot')


def install_member_boot(root,identity,new_member):
    from apx_portable_native import guid
    from apx_portable_native_media import ASSETS
    members={guid(identity['root_partuuid']),guid(new_member)}
    for record in (root/str(STATE).lstrip('/')/'members').glob('*.json'):
        value=trusted(record)
        if value.get('root_uuid')!=identity['root_uuid']:raise ValueError('Btrfs member belongs to another root')
        members.add(guid(value['partuuid']))
    path=root/'etc/apx-portable-btrfs-members-v4'
    path.write_text(''.join(uuid+'\n' for uuid in sorted(members)));path.chmod(0o600)
    assets=root/str(ASSETS).lstrip('/')
    for source,destination,mode in [
        ('members-initcpio-install','etc/initcpio/install/apx_portable_members_v4',0o644),
        ('members-initcpio-hook','etc/initcpio/hooks/apx_portable_members_v4',0o644),
        ('members-early.sh','usr/lib/apx/apx-portable-members-v4.sh',0o755)]:
        dest=root/destination;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(regular(assets/source),dest);dest.chmod(mode)
    units=[run('systemd-escape','--path','--suffix=device','/dev/disk/by-partuuid/'+uuid).strip() for uuid in sorted(members)]
    service=root/'etc/systemd/system/apx-portable-members-v4.service'
    service.write_text('[Unit]\nDescription=APX exact Linux storage members\nDefaultDependencies=no\n'
        +'Requires='+' '.join(units)+'\nAfter='+' '.join(units)+'\nBefore=initrd-root-fs.target sysroot.mount\n'
        +'[Service]\nType=oneshot\nExecStart=/usr/bin/apx-portable-members-v4\nTimeoutStartSec=120\nRemainAfterExit=yes\n')
    config=root/'etc/mkinitcpio.conf';text=config.read_text()
    match=re.search(r'^HOOKS=\(([^)]+)\)',text,re.M)
    if not match or 'filesystems' not in match[1].split():raise ValueError('unsupported initramfs hook configuration')
    hooks=match[1].split()
    if 'apx_portable_members_v4' not in hooks:
        hooks.insert(hooks.index('filesystems'),'apx_portable_members_v4')
        config.write_text(text[:match.start()]+'HOOKS=('+' '.join(hooks)+')'+text[match.end():])
    run('arch-chroot',root,'mkinitcpio','-P',timeout=600)


def offline_delete(job):
    source=validate_job(job);deletion=validate_delete(job['delete_plan']);identity=deletion['identity'];disk,table=disk_for(identity)
    if job['stage'] in {'delete-approved','recovery-queued','delete-wiping'}:
        if not exact_layout(table,deletion['before']):raise ValueError('delete before-layout differs')
        devices_unmounted(table,[identity['root_partuuid']]+[p['uuid'] for p in source['slots']])
        for p in source['slots'][1::2]:retire(p['uuid'])
        state(job,'delete-wiping')
        for p in source['slots']:erase(table,p)
        state(job,'delete-wiped')
    if job['stage']=='delete-wiped':
        if exact_layout(table,deletion['before']):table=write_table(disk,table,{'identity':identity,'table':deletion['after']})
        elif not exact_layout(table,deletion['after']):raise ValueError('delete interrupted GPT requires assisted recovery')
        state(job,'delete-table-written')
    if not exact_layout(table,deletion['after']):raise ValueError('delete after-layout differs')
    if job['stage']=='delete-table-written':
        rootnode=part(table,identity['root_partuuid'])
        run('btrfs','device','scan',rootnode)
        if deletion['mode']=='add-btrfs-member':
            member=part(table,source['slots'][0]['uuid'])
            probe=subprocess.run(['blkid','-s','TYPE','-o','value',member],text=True,capture_output=True)
            if probe.returncode==0 and probe.stdout.strip()=='btrfs':run('btrfs','device','scan',member)
        with mounted(rootnode,fstype='btrfs',options=['subvol=@'],executable=True) as root:
            if deletion['mode']=='grow-root':
                info=run('btrfs','filesystem','show','--raw',root)
                node=os.path.realpath(part(table,identity['root_partuuid']))
                match=re.search(r'devid\s+(\d+)\s+size\s+\d+\s+used\s+\d+\s+path\s+'+re.escape(node)+r'\s*$',info,re.M)
                if not match:raise ValueError('root Btrfs device ID absent')
                run('btrfs','filesystem','resize',match[1]+':max',root,timeout=3600)
            else:
                member=part(table,source['slots'][0]['uuid'])
                boot=root/'boot'
                run('mount',part(table,identity['esp_partuuid']),boot)
                try:install_member_boot(root,identity,source['slots'][0]['uuid'])
                finally:run('umount',boot)
                show=run('btrfs','filesystem','show','--raw',root)
                if os.path.realpath(member) not in show:
                    run('btrfs','device','add',member,root,timeout=600)
                # Explicit durable boot/member dependency, never silently lost.
                atomic(root/str(STATE).lstrip('/')/'members'/(source['generation']+'.json'),
                    dict(profile='apx-portable-btrfs-member-v4',partuuid=source['slots'][0]['uuid'],root_uuid=identity['root_uuid']))
            atomic(root/str(IDENTITY).lstrip('/'),identity_at(table,identity))
        state(job,'complete')
    linux_first(identity);run('systemctl','--no-block','reboot')


def offline():
    check_recovery(Path('/'))
    job=trusted(RECOVERY_STATE/'active.json');plan=validate_job(job);job['_recovery']=True
    identity=job['delete_plan']['identity'] if job['action']=='delete' else plan['identity']
    disk,table=disk_for(identity)
    if os.stat('/').st_dev!=Path(recovery_node(identity,table)).stat().st_rdev:
        raise ValueError('offline worker must boot from this installation independent Recovery root')
    if root_mounted(identity):raise ValueError('normal APX root is already mounted; offline operation refused')
    asserted_power()
    if job['stage'] in {'winpe-launched','complete','rolled-back','offline-failed'}:return
    try:
        if job['action']=='delete':offline_delete(job)
        elif job['action']=='rollback':offline_rollback(job)
        elif job['action']=='retry':offline_retry(job)
        else:offline_create(job)
    except Exception as error:
        previous=job['stage'];state(job,'offline-failed',offline_stage=previous,error=str(error)[-2000:])
        # Never arm another Windows/Recovery boot on failure. The next normal
        # APX boot exposes explicit recovery controls; root remains recoverable.
        try:linux_first(identity)
        except Exception:pass
        raise


def status_record(path,plan):
    raw=path.read_bytes()
    if len(raw)>16384:raise ValueError('oversized WinPE completion record')
    text=raw.decode('ascii').splitlines();pairs=[line.split('=',1) for line in text]
    if any(len(pair)!=2 for pair in pairs) or len({p[0] for p in pairs})!=len(pairs):raise ValueError('ambiguous WinPE status')
    value=dict(pairs)
    expected=dict(profile='apx-portable-WinPE-status-v4',generation=plan['generation'],plan_sha256=plan['sha256'],
                  state=value.get('state'),windows_partuuid=plan['slots'][0]['uuid'],esp_partuuid=plan['slots'][1]['uuid'])
    if value!=expected or value['state'] not in {'boot-prepared','failed','applying'}:raise ValueError('WinPE completion identity differs')
    return value


def finalize():
    if not IDENTITY.exists():return
    identity=trusted(IDENTITY)
    if identity.get('profile')!='apx-portable-native-identity-v4':return
    disk,table=disk_for(identity)
    with mounted(recovery_node(identity,table),fstype='ext4') as recovery:
        active=recovery/'var/lib/apx-native-v4/active.json'
        if not active.exists():return
        job=trusted(active);plan=validate_job(job)
        if not (STATE/'pending.json').exists():
            # Terminal jobs remain as recovery history, never resurrect them.
            if job['stage'] in {'complete','rolled-back'}:return
            raise ValueError('Recovery has an orphaned nonterminal job')
        pending=trusted(STATE/'pending.json')
        if job['stage'] in {'complete','rolled-back'} and pending['generation']!=job['generation']:return
        if pending['generation']!=job['generation']:raise ValueError('Host/Recovery generation differs')
        if job['stage']=='offline-failed':
            job['stage']='offline-failed';state(job,'offline-failed');return
        if job['stage']=='winpe-launched':
            if not exact_layout(table,plan['after']):raise ValueError('installed GPT differs from native transaction')
            with mounted(part(table,plan['slots'][3]['uuid']),readonly=True,fstype='vfat') as setup:
                status_path=setup/'APX/status.ini'
                result=status_record(status_path,plan) if status_path.is_file() else None
            if result is None or result['state']!='boot-prepared':
                state(job,'install-failed','A instalação Windows parou. Podes repetir ou remover este Windows.',error='WinPE failed or did not complete')
                return
            with mounted(part(table,plan['slots'][0]['uuid']),readonly=True,fstype='ntfs3') as windows:
                for relative in ['Windows/System32/winload.efi','Windows/System32/config/SYSTEM','ProgramData/APX/ReturnToHub/apx-native.exe']:
                    if not (windows/relative).is_file():raise ValueError('Windows completion file absent')
                helper=windows/'ProgramData/APX/ReturnToHub/apx-native.exe'
                if file_hash(helper)!=job['media']['files']['APX/apx-native.exe']:raise ValueError('Windows return helper digest differs')
            with mounted(part(table,plan['slots'][1]['uuid']),readonly=True,fstype='vfat') as esp:
                for relative in ['EFI/Microsoft/Boot/bootmgfw.efi','EFI/Microsoft/Boot/BCD']:
                    if not (esp/relative).is_file():raise ValueError('native UEFI payload absent')
            entry(table,plan['slots'][1]['uuid'],WINDOWS_PATH,'APX Windows '+plan['name'])
            retire(plan['slots'][3]['uuid']);linux_first(identity)
            atomic(STATE/'instances'/(plan['name']+'.json'),dict(schema=4,profile='apx-portable-native-instance-v4',
                target=plan['name'],generation=plan['generation'],plan=plan,state='ready',description=job.get('description','')))
            atomic(IDENTITY,identity_at(table,identity));job['stage']='complete';atomic(active,job)
        if job['stage'] in {'complete','rolled-back'}:
            if job['action']=='delete':(STATE/'instances'/(job['target']+'.json')).unlink(missing_ok=True)
            atomic(STATE/'history'/(job['generation']+'.json'),job)
            # Heavy source artifacts are no longer needed once boot integration
            # succeeds. Keep ISO registration, plan, hashes and recovery history.
            purge_job(job['generation'])
            (STATE/'pending.json').unlink(missing_ok=True)
            atomic(MANAGEMENT_STATE,dict(schema=1,profile='apx-environment-management-v1',phase='complete',
                progress=100,action=job['action'],target=job['target'],message='Operação Windows concluída.'))
