"""Source-only contracts; every storage/firmware command is mocked or excluded."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import apx_portable_native as model
import apx_portable_native_worker as worker
import apx_portable_native_media as media
import apx_portable_native_hub as hub
from test_apx_portable_native import fixture,create


class NativeExecutorContracts(unittest.TestCase):
    def job(self):
        identity,table=fixture('/dev/sdb',4096)
        plan=create(identity,table)
        return dict(schema=4,profile='apx-portable-native-job-v4',action='create',
                    target=plan['name'],generation=plan['generation'],plan=plan,stage='table-written',retries=0,
                    media=dict(profile='apx-portable-native-media-v4',generation=plan['generation'],
                               plan_sha256=plan['sha256'],files={'APX/apx-native.exe':'a'*64}))

    def test_missing_media_stops_before_any_disk_command(self):
        job=self.job();job.pop('media')
        with patch.object(worker,'run') as run:
            with self.assertRaisesRegex(ValueError,'verified media'):worker.validate_job(job)
            run.assert_not_called()

    def test_wrong_after_layout_never_reaches_format_or_firmware(self):
        job=self.job()
        with patch.object(worker,'disk_for',return_value=('/dev/sdb',job['plan']['before'])),patch.object(worker,'run') as run:
            with self.assertRaisesRegex(ValueError,'after-layout'):worker.offline_create(job)
            run.assert_not_called()

    def test_changed_before_layout_never_reaches_gpt_write(self):
        job=self.job();plan=job['plan']
        with patch.object(worker,'disk_for',return_value=('/dev/sdb',plan['after'])),patch.object(worker,'run') as run:
            with self.assertRaisesRegex(ValueError,'GPT changed'):worker.write_table('/dev/sdb',plan['before'],{'identity':plan['identity'],'table':plan['after']})
            run.assert_not_called()

    def test_completion_requires_exact_generation_and_rejects_duplicate_fields(self):
        plan=self.job()['plan']
        status=dict(profile='apx-portable-WinPE-status-v4',generation=plan['generation'],plan_sha256=plan['sha256'],
                    state='boot-prepared',windows_partuuid=plan['slots'][0]['uuid'],esp_partuuid=plan['slots'][1]['uuid'])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'status.ini'
            payload=''.join(k+'='+v+'\r\n' for k,v in status.items())
            path.write_bytes(payload.encode());self.assertEqual(worker.status_record(path,plan),status)
            path.write_bytes((payload+'generation='+plan['generation']+'\r\n').encode())
            with self.assertRaises(ValueError):worker.status_record(path,plan)
            status['generation']='00000000-0000-4000-8000-000000000000'
            path.write_text(''.join(k+'='+v+'\n' for k,v in status.items()))
            with self.assertRaises(ValueError):worker.status_record(path,plan)

    def test_retry_bound_stops_before_queuing_recovery(self):
        job=self.job();job.update(stage='install-failed',retries=2)
        with patch.object(worker,'trusted',return_value=job),patch.object(worker,'queue') as queue:
            with self.assertRaisesRegex(ValueError,'retry bound'):worker.host_action('retry',job['target'],job['generation'])
            queue.assert_not_called()

    def test_delete_plan_cannot_be_attached_to_another_instance_job(self):
        identity,table=fixture();first=create(identity,table)
        current=first['after'];current_identity=worker.identity_at(current,identity)
        second=create(current_identity,current,name='windows-study')
        current=second['after'];current_identity=worker.identity_at(current,identity)
        retired=dict(schema=4,profile='apx-portable-native-retirement-v4',name=first['name'],generation=first['generation'],
            source_plan_sha256=first['sha256'],state='deleting',layout_sha256=model.digest(current),efi_entries_retired=True)
        deletion=model.plan_delete(current_identity,current,first,retired,serial=identity['serial'],wwn=identity['wwn'])
        job=dict(schema=4,profile='apx-portable-native-job-v4',action='delete',target=second['name'],
                 generation=second['generation'],plan=second,delete_plan=deletion)
        with self.assertRaisesRegex(ValueError,'selected native instance'):worker.validate_job(job)

    def test_header_binds_sector_geometry_hardware_and_every_partition(self):
        plan=self.job()['plan'];capacity=(plan['after']['lastlba']+257)*4096
        header=media.header(plan,capacity,1,{'sources/install.swm':'a'*64})
        self.assertIn('#define APX_SECTOR_SIZE 4096',header)
        self.assertIn(str(capacity)+'ULL',header)
        self.assertIn(plan['identity']['serial'],header)
        for p in plan['after']['partitions']:
            self.assertIn(p['uuid'],header)
            self.assertIn(str(p['start']*4096)+'ULL',header)
            self.assertIn(str(p['size']*4096)+'ULL',header)
        with self.assertRaises(ValueError):media.header(plan,capacity,1,{'../unexpected':'a'*64})

    def test_storage_uses_actual_parent_and_subvolume_paths_beyond_one_tib(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as directory:
            environments=Path(directory)/'environments';environments.mkdir();(environments/'gaming').mkdir()
            def output(*args):
                if args[:4]==('findmnt','-J','-T',environments):
                    return json.dumps({'filesystems':[dict(fstype='btrfs',fsroot='/@apx',target=directory)]})
                if args[:3]==('btrfs','qgroup','show'):return '0/41 1000 1000 - - path\n0/42 2000 2000 - - path\n'
                if args[:3]==('btrfs','subvolume','list'):
                    return 'ID 41 gen 3 top level 5 path <FS_TREE>/@apx/environments/gaming/root\nID 42 gen 3 top level 5 path <FS_TREE>/@apx/environments/gaming/home\n'
                if args[0]=='blockdev':return str(2*1024**4)
                raise AssertionError(args)
            with patch.object(hub.os,'statvfs',return_value=SimpleNamespace(f_blocks=1024**4,f_frsize=1,f_bavail=512*1024**3)), \
                 patch('apx_portable_native_io.run',side_effect=output),patch.object(hub,'records',return_value=[]), \
                 patch.object(hub,'trusted',return_value={'profile':'apx-portable-native-identity-v4'}),patch.object(hub,'disk_for',return_value=('/dev/sdc',{})), \
                 patch.object(hub,'IDENTITY',SimpleNamespace(exists=lambda:True)):
                value=hub.storage_status(lambda name:None,environments)
            self.assertEqual(value['disk_total_bytes'],2*1024**4)
            self.assertEqual(value['sizes'],{'gaming':3000})

    def test_disk_renumbering_keeps_exact_gpt_identity(self):
        identity,table=fixture('/dev/sdb')
        new=worker.remap(table,'/dev/nvme2n1')
        self.assertEqual(model.validate_identity(identity,new,identity['serial'],identity['wwn']),new)
        changed=deepcopy(new);changed['partitions'][2]['size']-=2048
        with self.assertRaises(ValueError):model.validate_identity(identity,changed,identity['serial'],identity['wwn'])


if __name__=='__main__':unittest.main()
