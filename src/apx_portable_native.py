"""Hardware-independent native Windows geometry and transaction contracts.

Pure calculations only. No block I/O, firmware calls, mounts or credentials.
The portable executor remains disabled until offline/WinPE/reboot validation.
"""
from copy import deepcopy
import hashlib
import json
import re
from uuid import UUID, uuid5

GIB=1024**3
MIB=1024**2
RESERVE=96*GIB
ESP='c12a7328-f81f-11d2-ba4b-00a0c93ec93b'
MSR='e3c9e316-0b5c-4db8-817d-f92df00215ae'
BASIC='ebd0a0a2-b9e5-4433-87c0-68b6b72699c7'
LINUX='0fc63daf-8483-4772-8e79-3d69d8477de4'
DISK=re.compile(r'/dev/(?:sd[a-z]+|vd[a-z]+|nvme[0-9]+n[0-9]+|mmcblk[0-9]+)')
NAME=re.compile(r'[a-z](?:[a-z0-9]|-(?=[a-z0-9])){0,26}')
STAGES=('approved','root-shrunk','table-written','partitions-formatted','media-ready',
        'winpe-launched','install-verified','ready')


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def guid(value):
    if type(value) is not str or str(UUID(value))!=value.lower():
        raise ValueError('invalid partition/disk generation UUID')
    return value.lower()


def partition_node(disk,number):
    if not DISK.fullmatch(disk) or type(number) is not int or not 1<=number<=128:
        raise ValueError('unsupported whole disk or partition number')
    return disk+('p' if disk[-1].isdigit() else '')+str(number)


def canonical_layout(table):
    if type(table) is not dict or table.get('label')!='gpt' or table.get('unit')!='sectors' or not DISK.fullmatch(table.get('device','')):
        raise ValueError('a direct GPT sector inventory is required')
    result=deepcopy(table);result['id']=guid(result['id'])
    sector=result.get('sectorsize');first=result.get('firstlba');last=result.get('lastlba')
    if type(sector) is not int or sector not in {512,4096} or type(first) is not int or type(last) is not int or not 0<first<last:
        raise ValueError('unsupported GPT sector geometry')
    parts=result.get('partitions')
    if type(parts) is not list or not parts or len(parts)>128:
        raise ValueError('missing or oversized partition inventory')
    result['partitions']=sorted(parts,key=lambda p:p['start'])
    ids=set();nodes=set();end=first
    for p in result['partitions']:
        p['uuid']=guid(p['uuid']);p['type']=guid(p['type'])
        number=next((n for n in range(1,129) if partition_node(result['device'],n)==p['node']),None)
        if number is None or p['uuid'] in ids or p['node'] in nodes:
            raise ValueError('partition node/UUID is ambiguous')
        if type(p['start']) is not int or type(p['size']) is not int or p['start']<end or p['size']<=0 or p['start']+p['size']>last+1 or p['start']*sector%MIB:
            raise ValueError('overlapping, unaligned or out-of-range partition')
        end=p['start']+p['size'];ids.add(p['uuid']);nodes.add(p['node'])
    return result


def installation_identity(table,*,serial,wwn,root_uuid,root_partuuid,esp_partuuid,recovery_partuuid):
    table=canonical_layout(table)
    for value in (serial,wwn):
        if type(value) is not str or len(value)>256 or any(ord(c)<32 for c in value):
            raise ValueError('invalid hardware identity')
    if not serial and not wwn:raise ValueError('stable disk serial or WWN required')
    keys=[guid(x) for x in (root_partuuid,esp_partuuid,recovery_partuuid)]
    if len(set(keys))!=3:raise ValueError('root, ESP and Recovery must be independent')
    parts={p['uuid']:p for p in table['partitions']}
    if not set(keys)<=set(parts) or parts[keys[1]]['type']!=ESP or parts[keys[0]]['type']!=LINUX or parts[keys[2]]['type']!=LINUX:
        raise ValueError('installation partitions differ from the portable profile')
    record=dict(schema=4,profile='apx-portable-native-identity-v4',disk_id=table['id'],
        serial=serial,wwn=wwn,sector_size=table['sectorsize'],root_uuid=guid(root_uuid),
        root_partuuid=keys[0],esp_partuuid=keys[1],recovery_partuuid=keys[2],
        layout_sha256=digest(table),native_executor_enabled=False)
    record['sha256']=digest(record)
    return record


def validate_identity(identity,table,serial,wwn):
    table=canonical_layout(table)
    regenerated=installation_identity(table,serial=serial,wwn=wwn,root_uuid=identity['root_uuid'],
        root_partuuid=identity['root_partuuid'],esp_partuuid=identity['esp_partuuid'],recovery_partuuid=identity['recovery_partuuid'])
    if identity!=regenerated:raise ValueError('disk identity or exact GPT checkpoint changed')
    return table


def plan_create(identity,table,*,serial,wwn,name,generation,size_gib,used_bytes):
    table=validate_identity(identity,table,serial,wwn)
    if type(name) is not str or not NAME.fullmatch(name) or name=='hub':raise ValueError('invalid Windows name')
    generation=guid(generation)
    if type(size_gib) is not int or size_gib not in {80,120,180,250} or type(used_bytes) is not int or used_bytes<0:
        raise ValueError('unsupported Windows capacity or Btrfs measurement')
    sector=table['sectorsize'];alignment=MIB//sector
    root=next(p for p in table['partitions'] if p['uuid']==identity['root_partuuid'])
    root_end=root['start']+root['size']
    aligned_end=root_end//alignment*alignment
    sizes=[size_gib*GIB//sector,512*MIB//sector,16*MIB//sector,10*GIB//sector]
    start=aligned_end-sum(sizes)
    retained=(start-root['start'])*sector
    if retained<used_bytes+RESERVE+16*GIB:
        raise ValueError('Windows would cross the 96 GiB Linux recovery reserve or 16 GiB creation headroom')
    occupied={p['node'] for p in table['partitions']}
    numbers=[n for n in range(1,129) if partition_node(table['device'],n) not in occupied][:4]
    if len(numbers)!=4:raise ValueError('no independent GPT slots available')
    after=deepcopy(table)
    next(p for p in after['partitions'] if p['uuid']==root['uuid'])['size']=start-root['start']
    slots=[];cursor=start
    for purpose,type_guid,size,number in zip(('windows','esp','msr','setup'),(BASIC,ESP,MSR,ESP),sizes,numbers):
        p=dict(node=partition_node(table['device'],number),start=cursor,size=size,type=type_guid,
               uuid=str(uuid5(UUID(generation),purpose)),name='APX_'+purpose.upper())
        slots.append(p);after['partitions'].append(p);cursor+=size
    after=canonical_layout(after)
    plan=dict(schema=4,profile='apx-portable-native-create-v4',executable=False,
        identity=deepcopy(identity),before=table,after=after,name=name,generation=generation,
        size_gib=size_gib,used_bytes=used_bytes,retained_root_bytes=retained,
        slots=slots,root_partuuid=root['uuid'],reserve_bytes=RESERVE,
        protected=[p['uuid'] for p in table['partitions'] if p['uuid']!=root['uuid']],
        remaining_gates=['offline-shrink-rollback','verified-WinPE-image','EFI-BCD-identity',
                         'native-install-and-return','delete-and-reclaim-reboot'])
    plan['sha256']=digest(plan)
    return plan


def validate_plan(plan):
    if type(plan) is not dict or plan.get('profile')!='apx-portable-native-create-v4':raise ValueError('invalid portable native plan')
    identity=plan['identity']
    expected=plan_create(identity,plan['before'],serial=identity['serial'],wwn=identity['wwn'],
        name=plan['name'],generation=plan['generation'],size_gib=plan['size_gib'],used_bytes=plan['used_bytes'])
    if plan!=expected:raise ValueError('native plan differs from independently recomputed geometry')
    return deepcopy(plan)


def transaction(plan):
    plan=validate_plan(plan)
    record=dict(schema=4,profile='apx-portable-native-transaction-v4',generation=plan['generation'],
                plan_sha256=plan['sha256'],stage='approved',history=['approved'])
    record['sha256']=digest(record)
    return record


def advance(record,plan,stage,*,layout=None,install_status=None):
    plan=validate_plan(plan);current=dict(record);claimed=current.pop('sha256',None)
    if claimed!=digest(current) or current.get('schema')!=4 or set(current)!={'schema','profile','generation','plan_sha256','stage','history'} or current.get('profile')!='apx-portable-native-transaction-v4' or current.get('generation')!=plan['generation'] or current.get('plan_sha256')!=plan['sha256']:
        raise ValueError('transaction identity changed')
    history=current.get('history');previous=current.get('stage')
    if previous not in STAGES or history!=list(STAGES[:STAGES.index(previous)+1]) or STAGES.index(previous)+1>=len(STAGES) or stage!=STAGES[STAGES.index(previous)+1]:
        raise ValueError('native stage cannot be skipped or repeated')
    if STAGES.index(stage)>=STAGES.index('table-written') and (layout is None or canonical_layout(layout)!=plan['after']):
        raise ValueError('exact after-layout proof is required')
    if stage in {'install-verified','ready'}:
        expected={'profile':'apx-portable-WinPE-status-v4','generation':plan['generation'],
                  'plan_sha256':plan['sha256'],'state':'boot-prepared',
                  'windows_partuuid':plan['slots'][0]['uuid'],'esp_partuuid':plan['slots'][1]['uuid']}
        if install_status!=expected:raise ValueError('generation-bound Windows completion proof differs')
    current['stage']=stage;current['history']=history+[stage];current['sha256']=digest(current)
    return current


def rollback_allowed(record):
    value=dict(record);claimed=value.pop('sha256',None)
    if claimed!=digest(value) or value.get('schema')!=4 or value.get('profile')!='apx-portable-native-transaction-v4' or set(value)!={'schema','profile','generation','plan_sha256','stage','history'}:raise ValueError('invalid rollback transaction')
    stage=value.get('stage')
    if stage not in STAGES or value.get('history')!=list(STAGES[:STAGES.index(stage)+1]):raise ValueError('invalid rollback stage')
    return STAGES.index(stage)<STAGES.index('winpe-launched')


def plan_delete(identity,table,instance_plan,retired,*,serial,wwn):
    """Retire one exact slot, preserving siblings and explicit boot dependencies."""
    table=validate_identity(identity,table,serial,wwn)
    source=validate_plan(instance_plan)
    expected={'schema':4,'profile':'apx-portable-native-retirement-v4',
              'name':source['name'],'generation':source['generation'],
              'source_plan_sha256':source['sha256'],'state':'deleting',
              'layout_sha256':digest(table),'efi_entries_retired':True}
    if retired!=expected or retired.get('efi_entries_retired') is not True or type(retired.get('schema')) is not int:raise ValueError('exact instance/EFI retirement proof required')
    if any(source['identity'][key]!=identity[key] for key in ['disk_id','serial','wwn','sector_size','root_uuid','root_partuuid','esp_partuuid','recovery_partuuid']):
        raise ValueError('native instance belongs to another installation')
    by_uuid={p['uuid']:p for p in table['partitions']}
    slots=source['slots']
    if any(by_uuid.get(p['uuid'])!=p for p in slots):raise ValueError('native slot identity or extent changed')
    if any(a['start']+a['size']!=b['start'] for a,b in zip(slots,slots[1:])):raise ValueError('native slot is not contiguous')
    root=by_uuid[identity['root_partuuid']]
    selected={p['uuid'] for p in slots}
    after=deepcopy(table);after['partitions']=[p for p in after['partitions'] if p['uuid'] not in selected]
    size=sum(p['size'] for p in slots)
    if root['start']+root['size']==slots[0]['start']:
        mode='grow-root'
        next(p for p in after['partitions'] if p['uuid']==root['uuid'])['size']+=size
        dependency=None
    else:
        mode='add-btrfs-member'
        reclaimed=dict(slots[0],size=size,type=LINUX,name='APX_RECLAIMED')
        after['partitions'].append(reclaimed)
        dependency='/dev/disk/by-partuuid/'+reclaimed['uuid']
    after=canonical_layout(after)
    plan=dict(schema=4,profile='apx-portable-native-delete-v4',executable=False,
              identity=deepcopy(identity),before=table,after=after,source_plan=source,
              retirement=deepcopy(retired),mode=mode,reclaimed_bytes=size*table['sectorsize'],
              boot_dependency=dependency,
              protected=[p['uuid'] for p in table['partitions'] if p['uuid'] not in selected and (mode!='grow-root' or p['uuid']!=root['uuid'])],
              remaining_gates=['exact-slot-wipe','GPT-change-and-recovery','Linux-reclaim-second-boot'])
    plan['sha256']=digest(plan)
    return plan


def validate_delete(plan):
    if type(plan) is not dict or plan.get('profile')!='apx-portable-native-delete-v4':raise ValueError('invalid delete plan')
    identity=plan['identity']
    expected=plan_delete(identity,plan['before'],plan['source_plan'],plan['retirement'],serial=identity['serial'],wwn=identity['wwn'])
    if plan!=expected:raise ValueError('delete plan differs from independently recomputed geometry')
    return deepcopy(plan)


def sfdisk_script(table):
    """Serialize a validated full GPT; unknown metadata is never silently lost."""
    table=canonical_layout(table)
    fields={'node','start','size','type','uuid','name','attrs','bootable'}
    lines=['label: gpt','label-id: '+table['id'],'device: '+table['device'],
           'unit: sectors','first-lba: '+str(table['firstlba']),
           'last-lba: '+str(table['lastlba']),'sector-size: '+str(table['sectorsize']),'']
    for part in table['partitions']:
        if set(part)-fields:raise ValueError('unknown GPT partition metadata must be reviewed')
        row=part['node']+': start='+str(part['start'])+', size='+str(part['size'])+', type='+part['type']+', uuid='+part['uuid']
        for key in ['name','attrs']:
            if key in part:
                value=part[key]
                if type(value) is not str or any(ord(c)<32 or c in '\\"' for c in value):raise ValueError('unsupported GPT string escaping')
                row+=', '+key+'="'+value+'"'
        if part.get('bootable') is True:row+=', bootable'
        elif part.get('bootable') not in (None,False):raise ValueError('invalid GPT boot flag')
        lines.append(row)
    return '\n'.join(lines)+'\n'
