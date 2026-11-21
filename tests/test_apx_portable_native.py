from copy import deepcopy
import sys
from pathlib import Path
import unittest
from uuid import uuid4

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import apx_portable_native as native


def fixture(disk='/dev/nvme1n2',sector=512):
    alignment=native.MIB//sector
    table=dict(label='gpt',id=str(uuid4()),device=disk,unit='sectors',sectorsize=sector,
               firstlba=alignment,lastlba=1024*native.GIB//sector-34)
    parts=[];start=alignment
    for number,size,type_ in [(1,native.GIB,native.ESP),(2,2*native.GIB,native.LINUX)]:
        parts.append(dict(node=native.partition_node(disk,number),start=start,size=size//sector,type=type_,uuid=str(uuid4())))
        start+=size//sector
    parts.append(dict(node=native.partition_node(disk,3),start=start,size=table['lastlba']+1-start,type=native.LINUX,uuid=str(uuid4())))
    table['partitions']=parts
    identity=native.installation_identity(table,serial='NEW-PC-SSD-123',wwn='naa.123',root_uuid=str(uuid4()),root_partuuid=parts[2]['uuid'],esp_partuuid=parts[0]['uuid'],recovery_partuuid=parts[1]['uuid'])
    return identity,table


def create(identity,table,**overrides):
    args=dict(serial=identity['serial'],wwn=identity['wwn'],name='windows-personal',generation=str(uuid4()),size_gib=120,used_bytes=50*native.GIB)
    args.update(overrides)
    return native.plan_create(identity,table,**args)


class PortableNativeTests(unittest.TestCase):
    def test_new_sata_nvme_virtio_mmc_and_4k_geometry(self):
        for disk in ['/dev/sdb','/dev/vda','/dev/nvme1n2','/dev/mmcblk0']:
            for sector in [512,4096]:
                with self.subTest(disk=disk,sector=sector):
                    identity,table=fixture(disk,sector)
                    plan=create(identity,table)
                    self.assertFalse(plan['executable'])
                    self.assertEqual(native.validate_plan(plan),plan)
                    self.assertEqual(plan['after']['partitions'][:2],table['partitions'][:2])
                    self.assertEqual(plan['slots'][0]['size']*sector,120*native.GIB)
                    self.assertTrue(all(p['start']*sector%native.MIB==0 for p in plan['slots']))
                    self.assertEqual(len({p['uuid'] for p in plan['after']['partitions']}),7)

    def test_wrong_disk_sector_checkpoint_serial_and_root_uuid_refused(self):
        identity,table=fixture()
        for field,value in [('id',str(uuid4())),('sectorsize',4096)]:
            altered=deepcopy(table);altered[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):create(identity,altered)
        with self.assertRaises(ValueError):create(identity,table,serial='OTHER-SSD')
        altered=deepcopy(table);altered['partitions'][2]['uuid']=str(uuid4())
        with self.assertRaises(ValueError):create(identity,altered)
        altered=deepcopy(table);altered['partitions'][2]['size']-=2048
        with self.assertRaises(ValueError):create(identity,altered)

    def test_96gib_reserve_and_creation_headroom_not_crossed(self):
        identity,table=fixture()
        probe=create(identity,table)
        maximum=probe['retained_root_bytes']-native.RESERVE-16*native.GIB
        self.assertEqual(create(identity,table,used_bytes=maximum)['retained_root_bytes'],probe['retained_root_bytes'])
        with self.assertRaisesRegex(ValueError,'reserve'):create(identity,table,used_bytes=maximum+1)
        for value in [-1,True,'12']:
            with self.assertRaises(ValueError):create(identity,table,used_bytes=value)

    def test_name_capacity_aliases_and_duplicate_partition_identity_rejected(self):
        identity,table=fixture()
        for name in ['hub','../windows','two--hyphens','windows;reboot','']:
            with self.assertRaises(ValueError):create(identity,table,name=name)
        for size in [0,63,100,True,'120']:
            with self.assertRaises(ValueError):create(identity,table,size_gib=size)
        for disk in ['/dev/mapper/root','/dev/disk/by-id/x','/dev/nvme0n1p2','/dev/sda1']:
            with self.assertRaises(ValueError):native.partition_node(disk,4)
        altered=deepcopy(table);altered['partitions'][1]['uuid']=altered['partitions'][0]['uuid']
        with self.assertRaises(ValueError):native.canonical_layout(altered)

    def test_rehashed_modified_plan_does_not_authorize_changed_geometry(self):
        identity,table=fixture();plan=create(identity,table)
        for field in ['slots','after','protected','remaining_gates','executable']:
            altered=deepcopy(plan)
            if field=='slots':altered[field][0]['uuid']=str(uuid4())
            elif field=='after':altered[field]['partitions'][0]['size']-=2048
            elif field=='executable':altered[field]=True
            else:altered[field]=[]
            altered['sha256']=native.digest({k:v for k,v in altered.items() if k!='sha256'})
            with self.subTest(field=field),self.assertRaises(ValueError):native.validate_plan(altered)

    def test_foreign_sibling_partition_is_preserved_exactly(self):
        identity,table=fixture();table['partitions'][2]['size']-=100*native.GIB//512
        last=table['partitions'][2]['start']+table['partitions'][2]['size']
        table['partitions'].append(dict(node='/dev/nvme1n2p8',start=(last+2047)//2048*2048,size=90*native.GIB//512,type=native.BASIC,uuid=str(uuid4()),name='OWNER_DATA'))
        # Deliberate refreshed identity of the reviewed topology, not accepting drift.
        identity=native.installation_identity(table,serial=identity['serial'],wwn=identity['wwn'],root_uuid=identity['root_uuid'],root_partuuid=identity['root_partuuid'],esp_partuuid=identity['esp_partuuid'],recovery_partuuid=identity['recovery_partuuid'])
        plan=create(identity,table)
        self.assertIn(table['partitions'][-1],plan['after']['partitions'])
        self.assertNotIn('/dev/nvme1n2p8',[p['node'] for p in plan['slots']])

    def test_stages_cannot_skip_gpt_or_windows_completion_proofs(self):
        identity,table=fixture();plan=create(identity,table);record=native.transaction(plan)
        with self.assertRaises(ValueError):native.advance(record,plan,'winpe-launched',layout=plan['after'])
        record=native.advance(record,plan,'root-shrunk')
        with self.assertRaises(ValueError):native.advance(record,plan,'table-written')
        for stage in ['table-written','partitions-formatted','media-ready','winpe-launched']:
            record=native.advance(record,plan,stage,layout=plan['after'])
        self.assertFalse(native.rollback_allowed(record))
        with self.assertRaises(ValueError):native.advance(record,plan,'install-verified',layout=plan['after'])
        status=dict(profile='apx-portable-WinPE-status-v4',generation=plan['generation'],plan_sha256=plan['sha256'],state='boot-prepared',windows_partuuid=plan['slots'][0]['uuid'],esp_partuuid=plan['slots'][1]['uuid'])
        bad=dict(status,generation=str(uuid4()))
        with self.assertRaises(ValueError):native.advance(record,plan,'install-verified',layout=plan['after'],install_status=bad)
        for stage in ['install-verified','ready']:record=native.advance(record,plan,stage,layout=plan['after'],install_status=status)
        with self.assertRaises(ValueError):native.advance(record,plan,'ready',layout=plan['after'],install_status=status)

    def test_gpt_serializer_preserves_identity_and_rejects_unknown_metadata(self):
        identity,table=fixture('/dev/sdb',4096);plan=create(identity,table)
        script=native.sfdisk_script(plan['after'])
        self.assertIn('sector-size: 4096',script)
        self.assertIn('label-id: '+identity['disk_id'],script)
        for part in plan['after']['partitions']:
            self.assertIn(part['node']+': start='+str(part['start']),script)
            self.assertIn('uuid='+part['uuid'],script)
        altered=deepcopy(table);altered['partitions'][0]['unknown_flag']='retain me'
        with self.assertRaises(ValueError):native.sfdisk_script(altered)
        altered=deepcopy(table);altered['partitions'][0]['name']='bad"name'
        with self.assertRaises(ValueError):native.sfdisk_script(altered)

    def test_rollback_bound_to_valid_transaction_and_pre_launch_stage(self):
        identity,table=fixture();plan=create(identity,table);record=native.transaction(plan)
        self.assertTrue(native.rollback_allowed(record))
        record['stage']='winpe-launched'
        with self.assertRaises(ValueError):native.rollback_allowed(record)


class PortableNativeDeletionTests(unittest.TestCase):
    def identity(self,original,table):
        return native.installation_identity(table,serial=original['serial'],wwn=original['wwn'],root_uuid=original['root_uuid'],root_partuuid=original['root_partuuid'],esp_partuuid=original['esp_partuuid'],recovery_partuuid=original['recovery_partuuid'])

    def retirement(self,plan,table):
        return dict(schema=4,profile='apx-portable-native-retirement-v4',name=plan['name'],generation=plan['generation'],source_plan_sha256=plan['sha256'],state='deleting',layout_sha256=native.digest(native.canonical_layout(table)),efi_entries_retired=True)

    def test_adjacent_slot_returns_space_to_root_preserving_esp_recovery(self):
        original,table=fixture();source=create(original,table);current=source['after'];identity=self.identity(original,current)
        plan=native.plan_delete(identity,current,source,self.retirement(source,current),serial=identity['serial'],wwn=identity['wwn'])
        self.assertEqual(plan['mode'],'grow-root');self.assertIsNone(plan['boot_dependency'])
        self.assertEqual(len(plan['after']['partitions']),3)
        self.assertEqual(plan['after']['partitions'][:2],table['partitions'][:2])
        self.assertEqual(native.validate_delete(plan),plan)

    def test_nonadjacent_slot_has_explicit_new_member_boot_dependency(self):
        original,table=fixture();first=create(original,table)
        identity=self.identity(original,first['after']);second=create(identity,first['after'],name='windows-study')
        current=second['after'];identity=self.identity(original,current)
        plan=native.plan_delete(identity,current,first,self.retirement(first,current),serial=identity['serial'],wwn=identity['wwn'])
        self.assertEqual(plan['mode'],'add-btrfs-member')
        self.assertEqual(plan['boot_dependency'],'/dev/disk/by-partuuid/'+first['slots'][0]['uuid'])
        self.assertFalse(plan['executable'])
        for part in second['slots']:self.assertIn(part,plan['after']['partitions'])
        oldroot=next(p for p in current['partitions'] if p['uuid']==identity['root_partuuid'])
        self.assertIn(oldroot,plan['after']['partitions'])

    def test_wrong_generation_unretired_firmware_or_extent_prevents_deletion(self):
        original,table=fixture();source=create(original,table);current=source['after'];identity=self.identity(original,current)
        good=self.retirement(source,current)
        for key,value in [('generation',str(uuid4())),('efi_entries_retired',False),('efi_entries_retired',1),('state','ready')]:
            bad=dict(good);bad[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):native.plan_delete(identity,current,source,bad,serial=identity['serial'],wwn=identity['wwn'])
        current=deepcopy(current);current['partitions'][-1]['size']-=2048
        altered=self.identity(original,current)
        with self.assertRaises(ValueError):native.plan_delete(altered,current,source,self.retirement(source,current),serial=identity['serial'],wwn=identity['wwn'])

    def test_rehashed_delete_that_changes_other_windows_is_rejected(self):
        original,table=fixture();source=create(original,table);current=source['after'];identity=self.identity(original,current)
        plan=native.plan_delete(identity,current,source,self.retirement(source,current),serial=identity['serial'],wwn=identity['wwn'])
        plan['after']['partitions'][0]['size']-=2048
        plan['sha256']=native.digest({k:v for k,v in plan.items() if k!='sha256'})
        with self.assertRaises(ValueError):native.validate_delete(plan)


class NativeIdentityInstallerTests(unittest.TestCase):
    def test_empty_disk_installer_records_actual_partition_uuids_without_enabling_native(self):
        import importlib.util,json,tempfile
        from unittest.mock import patch
        spec=importlib.util.spec_from_file_location('native_disk_identity_test',Path(__file__).resolve().parents[1]/'scripts/portable/install_apx_disk.py')
        installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
        identity,table=fixture('/dev/sdb');parts=table['partitions']
        lookup={(parts[2]['node'],'UUID'):identity['root_uuid'],(parts[2]['node'],'PARTUUID'):identity['root_partuuid'],(parts[0]['node'],'PARTUUID'):identity['esp_partuuid'],(parts[1]['node'],'PARTUUID'):identity['recovery_partuuid']}
        def run(*args,**kwargs):
            if args[0]=='sfdisk':return json.dumps({'partitiontable':table})
            return lookup[(args[-1],args[2])]
        with tempfile.TemporaryDirectory() as temp,patch.object(installer,'run',side_effect=run):
            root=Path(temp)
            installer.record_native_identity(root,{'disk':{'serial':identity['serial'],'wwn':identity['wwn']}},table['device'],parts[0]['node'],parts[1]['node'],parts[2]['node'])
            record=root/'etc/apx-portable-native-identity-v4.json';value=json.loads(record.read_text())
            self.assertEqual(value,identity);self.assertEqual(record.stat().st_mode&0o777,0o600)
            self.assertFalse(value['native_executor_enabled'])

    def test_disk_without_stable_identity_keeps_linux_installation_and_disables_native(self):
        import importlib.util,json,tempfile
        from unittest.mock import patch
        spec=importlib.util.spec_from_file_location('native_missing_disk_identity_test',Path(__file__).resolve().parents[1]/'scripts/portable/install_apx_disk.py')
        installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
        with tempfile.TemporaryDirectory() as temp,patch.object(installer,'run') as command:
            installer.record_native_identity(Path(temp),{'disk':{'serial':None,'wwn':None}},'/dev/vda','/dev/vda1','/dev/vda2','/dev/vda3')
            command.assert_not_called()
            value=json.loads((Path(temp)/'etc/apx-portable-native-identity-v4.json').read_text())
            self.assertFalse(value['native_executor_enabled']);self.assertIn('no stable',value['reason'])


if __name__=='__main__':unittest.main()
