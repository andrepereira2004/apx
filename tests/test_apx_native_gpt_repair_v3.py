from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from apx_native_gpt_repair_v3 import repair_regular_file
from apx_native_instances_v3 import plan_second_windows, canonical_layout
from apx_native_offline_v3 import partition_script
from apx_native_recovery_v3 import assess
from test_apx_native_instances_v3 import fixture


class GPTRepairLabTests(unittest.TestCase):
    def test_repair_only_disposable_disk_file_after_verified_copy(self):
        table, legacy, args = fixture()
        plan = plan_second_windows(table, legacy, **args)
        manifest = {'profile': 'apx-native-image-backup-v3', 'state': 'verified-images',
                    'plan_sha256': plan['plan_sha256'],
                    'original': {'file': 'original.ntfs.raw', 'bytes': table['partitions'][2]['size'] * 512, 'sha256': 'a' * 64},
                    'prepared': {'bytes': 120 * 1024**3, 'sha256': 'b' * 64}}
        prefix = f"{plan['new']['generation']}:{plan['plan_sha256']}:relocate:"
        assessment = assess(plan, manifest, 'relocate', None,
                            copy_marker=prefix + 'copy-verified:verify-windows',
                            destination_sha256='b' * 64)
        self.assertEqual(assessment['decision'], 'manual-gpt-repair-review')
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            disk = Path(directory) / 'disposable.img'
            with disk.open('wb') as stream:
                stream.truncate((plan['after']['lastlba'] + 34) * 512)
            subprocess.run(['/usr/bin/sfdisk', '--no-reread', str(disk)],
                           input=partition_script(plan['before']), text=True,
                           check=True, capture_output=True)
            with disk.open('r+b') as stream:
                stream.seek(512)
                stream.write(b'\0' * 512)
            self.assertEqual(canonical_layout(repair_regular_file(disk, plan, 'relocate', assessment)),
                             canonical_layout(plan['after']))
            assessed = dict(assessment, destination_matches_image=False)
            with self.assertRaises(ValueError):repair_regular_file(disk, plan, 'relocate', assessed)
            with self.assertRaises(ValueError):repair_regular_file(Path('/dev/null'), plan, 'relocate', assessment)
