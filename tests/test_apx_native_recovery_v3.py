from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from apx_native_instances_v3 import plan_second_windows
from apx_native_recovery_v3 import assess, hash_extent
import hashlib
import tempfile
import importlib.util
import json
import subprocess
from unittest import mock
from test_apx_native_instances_v3 import fixture

INSPECT_PATH = Path(__file__).resolve().parents[1] / 'scripts/physical-pilot/inspect-native-recovery-v3.py'
SPEC = importlib.util.spec_from_file_location('inspect_native_recovery_v3', INSPECT_PATH)
INSPECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECTOR)


class NativeRecoveryTests(unittest.TestCase):
    def test_hash_extent_reads_only_selected_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / 'image'
            image.write_bytes(b'A' * 4096 + b'B' * 4096 + b'C' * 4096)
            before = image.read_bytes()
            self.assertEqual(hash_extent(image, 4096, 4096), hashlib.sha256(b'B' * 4096).hexdigest())
            self.assertEqual(image.read_bytes(), before)
            with self.assertRaises(ValueError):hash_extent(image, 8192, 8192)

    def setUp(self):
        table, legacy, args = fixture()
        self.plan = plan_second_windows(table, legacy, **args)
        self.manifest = {'profile': 'apx-native-image-backup-v3', 'state': 'verified-images',
                         'plan_sha256': self.plan['plan_sha256'],
                         'original': {'file': 'original.ntfs.raw', 'bytes': table['partitions'][2]['size'] * 512, 'sha256': 'a' * 64},
                         'prepared': {'file': 'prepared.ntfs.raw', 'bytes': 120 * 1024**3, 'sha256': 'b' * 64}}
        prefix = f"{self.plan['new']['generation']}:{self.plan['plan_sha256']}:relocate:"
        self.marker = prefix + 'copy-verified:verify-windows'
        self.complete = prefix + 'complete:write-gpt'

    def test_exact_result_with_verified_copy_is_reviewable(self):
        result = assess(self.plan, self.manifest, 'relocate', self.plan['after'],
                        status=self.complete, copy_marker=self.marker, destination_sha256='b' * 64)
        self.assertEqual(result['decision'], 'ready-for-finalizer-review')
        self.assertEqual(result['layout'], 'result')

    def test_partial_or_unverified_disk_never_recommends_finalization(self):
        changed = deepcopy(self.plan['after'])
        changed['partitions'][2]['uuid'] = self.plan['before']['partitions'][2]['uuid']
        changed['partitions'][2]['size'] -= 2048
        cases = [(self.plan['after'], self.complete, self.marker, 'c' * 64),
                 (self.plan['after'], self.complete, None, 'b' * 64),
                 (None, self.complete, self.marker, 'c' * 64)]
        for layout, status, marker, digest in cases:
            with self.subTest(layout=layout, marker=marker, digest=digest):
                result = assess(self.plan, self.manifest, 'relocate', layout,
                                status=status, copy_marker=marker, destination_sha256=digest)
                self.assertEqual(result['decision'], 'stop-no-write')
        self.assertEqual(assess(self.plan, self.manifest, 'relocate', changed,
                                status=self.complete, copy_marker=self.marker,
                                destination_sha256='b' * 64)['decision'], 'manual-gpt-repair-review')

    def test_verified_copy_with_starting_layout_still_needs_manual_review(self):
        result = assess(self.plan, self.manifest, 'relocate', self.plan['before'],
                        status=self.marker, copy_marker=self.marker, destination_sha256='b' * 64)
        self.assertEqual(result['decision'], 'manual-recovery-review')

    def test_interrupted_copy_with_intact_original_backup_is_restore_review(self):
        result = assess(self.plan, self.manifest, 'relocate', self.plan['before'],
                        status=f"{self.plan['new']['generation']}:{self.plan['plan_sha256']}:relocate:failed:copy-windows",
                        destination_sha256='c' * 64, original_destination_sha256='d' * 64,
                        original_backup_sha256='a' * 64)
        self.assertEqual(result['decision'], 'manual-original-restore-review')
        self.assertTrue(result['original_backup_matches_image'])
        for backup, old in [('d' * 64, 'd' * 64), (None, 'd' * 64), ('a' * 64, 'a' * 64)]:
            with self.subTest(backup=backup, old=old):
                result = assess(self.plan, self.manifest, 'relocate', self.plan['before'],
                                status=f"{self.plan['new']['generation']}:{self.plan['plan_sha256']}:relocate:started:preflight",
                                original_destination_sha256=old, original_backup_sha256=backup)
                self.assertNotEqual(result['decision'], 'manual-original-restore-review')

    def test_rollback_uses_original_image_and_original_result_layout(self):
        prefix = f"{self.plan['new']['generation']}:{self.plan['plan_sha256']}:rollback:"
        result = assess(self.plan, self.manifest, 'rollback', self.plan['before'],
                        status=prefix + 'complete:write-gpt',
                        copy_marker=prefix + 'copy-verified:verify-windows', destination_sha256='a' * 64)
        self.assertEqual(result['decision'], 'ready-for-finalizer-review')

    def test_image_from_a_different_plan_is_rejected(self):
        manifest = deepcopy(self.manifest)
        manifest['plan_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'manifest'):
            assess(self.plan, manifest, 'relocate', self.plan['after'])

    def test_inspector_reports_verified_result_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan_path, manifest_path = root / 'plan.json', root / 'manifest.json'
            plan_path.write_text(json.dumps(self.plan))
            manifest_path.write_text(json.dumps(self.manifest))
            (root / ('native-v3-' + self.plan['new']['generation'] + '.status')).write_text(self.complete)
            (root / ('native-v3-' + self.plan['new']['generation'] + '.copy-verified')).write_text(self.marker)
            original = Path.read_text
            def identity_text(path, *args, **kwargs):
                name = str(path)
                if name == '/etc/hostname':return 'apx-host\n'
                if name == '/sys/class/dmi/id/product_name':return '82JU\n'
                if name == '/sys/class/block/nvme0n1/device/serial':return self.plan['disk_serial'] + '\n'
                return original(path, *args, **kwargs)
            observed = subprocess.CompletedProcess(['sfdisk'], 0, json.dumps({'partitiontable': self.plan['after']}), '')
            with mock.patch.object(Path, 'read_text', identity_text), \
                 mock.patch.object(INSPECTOR.subprocess, 'run', return_value=observed) as run, \
                 mock.patch.object(INSPECTOR, 'hash_extent', return_value='b' * 64) as hashed:
                report = INSPECTOR.inspect(plan_path, manifest_path, 'relocate', root)
            self.assertEqual(report['decision'], 'ready-for-finalizer-review')
            self.assertEqual(run.call_args.args[0], ['/usr/bin/sfdisk', '--json', '/dev/nvme0n1'])
            self.assertEqual(hashed.call_args.args[2], 120 * 1024**3)

    def test_inspector_checks_original_backup_only_for_started_interrupted_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan_path, manifest_path = root / 'plan.json', root / 'manifest.json'
            plan_path.write_text(json.dumps(self.plan))
            manifest_path.write_text(json.dumps(self.manifest))
            (root / ('native-v3-' + self.plan['new']['generation'] + '.status')).write_text(
                f"{self.plan['new']['generation']}:{self.plan['plan_sha256']}:relocate:failed:copy-windows")
            backup = root / 'original.ntfs.raw'
            with backup.open('wb') as stream:
                stream.truncate(self.manifest['original']['bytes'] - 4096)
            original_read_text = Path.read_text
            def identity_text(path, *args, **kwargs):
                values = {'/etc/hostname': 'apx-host\n', '/sys/class/dmi/id/product_name': '82JU\n',
                          '/sys/class/block/nvme0n1/device/serial': self.plan['disk_serial'] + '\n'}
                if str(path) in values:return values[str(path)]
                return original_read_text(path, *args, **kwargs)
            observed = subprocess.CompletedProcess(['sfdisk'], 0,
                         json.dumps({'partitiontable': self.plan['before']}), '')
            with mock.patch.object(Path, 'read_text', identity_text), \
                 mock.patch.object(INSPECTOR.subprocess, 'run', return_value=observed), \
                 mock.patch.object(INSPECTOR, 'hash_extent', side_effect=['c' * 64, 'd' * 64, 'c' * 64, 'd' * 64, 'a' * 64]) as hashed:
                with self.assertRaisesRegex(ValueError, 'backup file identity'):
                    INSPECTOR.inspect(plan_path, manifest_path, 'relocate', root)
                with backup.open('r+b') as stream:
                    stream.truncate(self.manifest['original']['bytes'])
                report = INSPECTOR.inspect(plan_path, manifest_path, 'relocate', root)
            self.assertEqual(report['decision'], 'manual-original-restore-review')
            self.assertEqual(hashed.call_count, 5)
            self.assertEqual(hashed.call_args.args[0], root / 'original.ntfs.raw')
