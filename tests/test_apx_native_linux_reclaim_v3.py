from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from apx_native_instances_v3 import free_slot_record, digest
from apx_native_linux_reclaim_v3 import plan_reclaim, validate_reclaim, kernel_cmdline, crypttab, validate_storage_health
from test_apx_native_slot_checkpoint_v3 import reconciled_fixture


def fixture():
    source, table, checkpoint, original = reconciled_fixture()
    marker = free_slot_record(source, table, [original], source['new']['generation'], checkpoint=checkpoint)
    parts = {p['node']: p for p in table['partitions']}
    retired = dict(original, name='windows-testes', generation=source['new']['generation'], state='deleting',
                   windows_partuuid=parts['/dev/nvme0n1p5']['uuid'],
                   esp_partuuid=parts['/dev/nvme0n1p6']['uuid'],
                   start_sector=parts['/dev/nvme0n1p5']['start'],
                   size_sectors=parts['/dev/nvme0n1p5']['size'])
    return table, marker, retired, original, str(uuid4())


class ReclaimTests(unittest.TestCase):
    def test_section_inspection_never_rewrites_the_signed_input(self):
        path = Path(__file__).resolve().parents[1]/'scripts/physical-pilot/apx-reclaim-windows-linux-v3.py'
        spec = importlib.util.spec_from_file_location('extract_test',path)
        module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            image=Path(directory)/'signed.efi';image.write_bytes(b'signed PE fixture')
            destination=Path(directory)/'cmdline'
            def objcopy(*args,**kwargs):
                destination.write_bytes(b'rootflags=subvol=@\0')
                if len(args)==4:
                    image.write_bytes(b'PE with invalidated signature')
                else:
                    self.assertNotEqual(Path(args[4]),image)
                    Path(args[4]).write_bytes(b'disposable output')
            with mock.patch.object(module,'run',side_effect=objcopy):
                self.assertEqual(module.extract(image,'.cmdline',destination),b'rootflags=subvol=@')
            self.assertEqual(image.read_bytes(),b'signed PE fixture')

    def health_fixture(self):
        counters=dict(write_io_errs=0,read_io_errs=0,flush_io_errs=0,corruption_errs=79,generation_errs=0)
        stats={'device-stats':[dict(device='/dev/mapper/cryptroot',devid=1,**counters)]}
        proof=dict(profile='apx-clean-readonly-scrub-v3',filesystem_uuid='root',
                   clean_readonly_scrub=True,verified_at=100,
                   historical_counters={'/dev/mapper/cryptroot':counters.copy()})
        return stats,proof

    def test_historical_counter_requires_recent_clean_readonly_evidence(self):
        stats,proof=self.health_fixture()
        with self.assertRaises(ValueError):validate_storage_health(stats,None,'root',101)
        validate_storage_health(stats,proof,'root',101)
        self.assertEqual(stats['device-stats'][0]['corruption_errs'],79)

    def test_scrub_proof_never_allows_new_errors_or_stale_evidence(self):
        for key,value in [('corruption_errs',80),('write_io_errs',1),('generation_errs',1)]:
            stats,proof=self.health_fixture();stats['device-stats'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate_storage_health(stats,proof,'root',101)
        stats,proof=self.health_fixture()
        with self.assertRaises(ValueError):validate_storage_health(stats,proof,'root',100+86401)
        with self.assertRaises(ValueError):validate_storage_health(stats,proof,'other-root',101)
        with self.assertRaises(ValueError):validate_storage_health(stats,proof,'root',99)

    def test_clean_device_counters_do_not_need_historical_exception(self):
        stats,proof=self.health_fixture();stats['device-stats'][0]['corruption_errs']=0
        validate_storage_health(stats,None,'root',101)

    def test_reclaims_only_secondary_slot_and_preserves_personal_and_recovery(self):
        args = fixture(); plan = plan_reclaim(*args)
        self.assertEqual(validate_reclaim(plan), plan)
        before = {p['node']: p for p in plan['before']['partitions']}
        after = {p['node']: p for p in plan['after']['partitions']}
        for number in (1, 2, 3, 4, 8):
            self.assertEqual(before['/dev/nvme0n1p'+str(number)], after['/dev/nvme0n1p'+str(number)])
        self.assertEqual(plan['bytes'], (77*1024**3)+(512+16)*1024**2)
        self.assertEqual(plan['reclaimed']['start'], before['/dev/nvme0n1p6']['start'])
        self.assertEqual(plan['reclaimed']['uuid'], before['/dev/nvme0n1p5']['uuid'].lower())

    def test_rejects_stale_marker_before_any_write(self):
        args = list(fixture()); args[0]['partitions'][1]['size'] -= 2048
        with self.assertRaises(ValueError): plan_reclaim(*args)

    def test_rejects_wrong_generation_or_personal_windows(self):
        for key, value in [('generation',str(uuid4())),('name','windows'),('state','ready')]:
            args = list(fixture()); args[2][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): plan_reclaim(*args)

    def test_rejects_aliases_and_extent_drift(self):
        for key in ('windows_partuuid','esp_partuuid','msr_partuuid'):
            args = list(fixture()); args[1][key] = str(uuid4())
            with self.subTest(key=key), self.assertRaises(ValueError): plan_reclaim(*args)

    def test_rehashing_does_not_authorize_changes_to_protected_partition(self):
        plan = plan_reclaim(*fixture())
        plan['after']['partitions'][2]['size'] -= 2048
        plan['sha256'] = digest({k:v for k,v in plan.items() if k != 'sha256'})
        with self.assertRaisesRegex(ValueError, 'protected'): validate_reclaim(plan)

    def test_rehashing_does_not_authorize_reclaimed_extent_expansion(self):
        plan = plan_reclaim(*fixture())
        plan['after']['partitions'][4]['size'] += 2048
        plan['sha256'] = digest({k:v for k,v in plan.items() if k != 'sha256'})
        with self.assertRaises(ValueError): validate_reclaim(plan)

    def test_boot_requires_explicit_secondary_mapper_without_losing_existing_flags(self):
        uuid = str(uuid4())
        result = kernel_cmdline('root=/dev/mapper/cryptroot rootflags=subvol=@ rw iommu=pt\n',uuid)
        self.assertIn('rootflags=subvol=@,device=/dev/mapper/cryptreclaimed',result)
        self.assertIn('iommu=pt',result)
        self.assertIn('rd.luks.name='+uuid+'=cryptreclaimed',result)
        with self.assertRaises(ValueError): kernel_cmdline(result,uuid)

    def test_boot_crypttab_has_no_plaintext_secret_and_rejects_overwrite(self):
        root, new = str(uuid4()), str(uuid4())
        result = crypttab('# initial\n',root,new)
        self.assertIn('cryptroot UUID='+root+' none luks,x-initrd.attach', result)
        self.assertIn('cryptreclaimed UUID='+new+' none luks,x-initrd.attach',result)
        with self.assertRaises(ValueError): crypttab('other UUID=x /key luks',root,new)

    def test_console_executor_does_not_report_success_before_membership(self):
        path = Path(__file__).resolve().parents[1]/'scripts/physical-pilot/apx-reclaim-windows-linux-v3.py'
        spec = importlib.util.spec_from_file_location('reclaim_console_test', path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        plan = plan_reclaim(*fixture())
        script = module.gpt_script(plan['after']).decode()
        self.assertNotIn('/dev/nvme0n1p6 :',script)
        self.assertNotIn('/dev/nvme0n1p7 :',script)
        self.assertIn('/dev/nvme0n1p3 :',script)
        with mock.patch.object(module,'run',return_value=b' devid 1 size 20 used 5 path /dev/mapper/cryptroot\n'):
            self.assertFalse(module.is_member())
        with mock.patch.object(module,'run',return_value=b' devid 2 size 20 used 5 path /dev/mapper/cryptreclaimed\n'):
            self.assertTrue(module.is_member())


if __name__ == '__main__': unittest.main()
