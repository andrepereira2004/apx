from pathlib import Path
import json,shutil
import subprocess,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from apx_native_instances_v3 import canonical_layout,plan_second_windows
from apx_native_offline_v3 import partition_script,render
from test_apx_native_instances_v3 import fixture

class OfflineTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('sfdisk'), 'sfdisk unavailable')
    def test_partition_script_round_trips_on_disposable_disk_file(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            disk=Path(directory)/'disk.img'
            with disk.open('wb') as stream:stream.truncate(64*1024**2)
            initial='label: gpt\nunit: sectors\nstart=2048, size=8192, type=uefi, name="APX_EFI"\nstart=10240, size=16384, type=linux, name="APX_CRYPT"\n'
            subprocess.run(['sfdisk','--no-reread',str(disk)],input=initial,text=True,check=True,capture_output=True)
            table=json.loads(subprocess.run(['sfdisk','--json',str(disk)],text=True,check=True,capture_output=True).stdout)['partitiontable']
            subprocess.run(['sfdisk','--no-reread','--wipe','never','--wipe-partitions','never',str(disk)],
                           input=partition_script(table),text=True,check=True,capture_output=True)
            observed=json.loads(subprocess.run(['sfdisk','--json',str(disk)],text=True,check=True,capture_output=True).stdout)['partitiontable']
            self.assertEqual(canonical_layout(observed),canonical_layout(table))

    def test_relocation_and_rollback_have_exact_opposite_extents(self):
        table,legacy,args=fixture();plan=plan_second_windows(table,legacy,**args)
        manifest=dict(profile='apx-native-image-backup-v3',state='verified-images',plan_sha256=plan['plan_sha256'],
            original=dict(file='original.ntfs.raw',sha256='a'*64,bytes=151*1024**3),
            prepared=dict(file='prepared.ntfs.raw',sha256='b'*64,bytes=120*1024**3))
        for rollback in (False,True):
            script=render(plan,manifest,rollback=rollback)
            self.assertIn('action='+('rollback' if rollback else 'relocate'),script)
            self.assertIn('original.ntfs.raw' if rollback else 'prepared.ntfs.raw',script)
            self.assertIn('native-v3-$generation.status',script)
            self.assertIn('stage=preflight-power\n[[ $(cat /sys/class/power_supply/ADP0/online) == 1 ]]',script)
            self.assertIn('stage=preflight-sysroot\nif mountpoint -q /sysroot; then false; fi',script)
            self.assertIn('stage=preflight-image-hash',script)
            self.assertIn('stage=preflight\nrecord started',script)
            self.assertEqual('btrfs filesystem resize' in script,not rollback)
            self.assertLess(script.index('stage=verify-windows'),script.index('stage=write-gpt'))
            self.assertLess(script.index('sfdisk --verify'),script.index('record complete'))
            self.assertIn('"$action" --result',script)
            self.assertIn('$stage == copy-windows || $stage == verify-windows || $stage == write-gpt',script)
            self.assertLess(script.index('disco pode estar em transição'),script.index('systemctl --no-block --force reboot || true'))
            self.assertLess(script.index('record copy-verified'),script.index('stage=write-gpt'))
            self.assertNotIn('blkdiscard',script)
            self.assertNotIn('mkfs',script)
            result=subprocess.run(['bash','-n'],input=script,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
        manifest['prepared']['bytes']-=4096
        with self.assertRaises(ValueError):render(plan,manifest)
