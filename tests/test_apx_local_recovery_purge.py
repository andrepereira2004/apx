"""Deletion must not leave restorable local recovery copies or claim success."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('local_purge_runtime', Path(__file__).parents[1] / 'scripts/virtual-lab/apx-lab-runtime.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class LocalRecoveryPurgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.patch = patch.object(runtime, 'LOCAL_RECOVERY', self.root)
        self.patch.start(); self.addCleanup(self.patch.stop)

    def copy(self, name='school', label='home'):
        path = self.root / f'environment-{name}-{label}' / '20260927T161241Z'
        path.mkdir(parents=True)
        (path / 'personal-file').write_text('data')
        return path

    def test_all_target_copies_removed_neighbor_preserved(self):
        targets = {self.copy(), self.copy(label='root')}
        neighbor = self.copy('school-extra')
        with patch.object(runtime, 'run') as run, patch.object(runtime, 'delete_subvolume_tree', side_effect=shutil.rmtree):
            copies = runtime.local_recovery_snapshots('school')
            self.assertEqual(set(copies), targets)
            self.assertEqual(run.call_count, 2)
            runtime.purge_local_recovery('school', copies)
        self.assertFalse(any(p.exists() for p in targets))
        self.assertEqual((neighbor / 'personal-file').read_text(), 'data')

    def test_purge_failure_does_not_silently_succeed(self):
        path = self.copy()
        with patch.object(runtime, 'delete_subvolume_tree'), self.assertRaisesRegex(runtime.Refusal, 'remained'):
            runtime.purge_local_recovery('school', (path,))
        self.assertTrue(path.exists())

    def test_symlink_snapshot_refused(self):
        neighbor = self.copy('other')
        parent = self.root / 'environment-school-home'; parent.mkdir()
        (parent / '20260927T161241Z').symlink_to(neighbor)
        with self.assertRaises(runtime.Refusal):
            runtime.local_recovery_snapshots('school')
        self.assertTrue(neighbor.exists())

    def test_symlink_parent_refused(self):
        self.copy('other')
        (self.root / 'environment-school-home').symlink_to(self.root / 'environment-other-home')
        with self.assertRaises(runtime.Refusal):
            runtime.local_recovery_snapshots('school')

    def test_mixed_system_state_refused_before_mutations(self):
        state = self.root / 'system/20260927T161241Z/var/lib/apx'
        state.mkdir(parents=True); (state / 'backups').mkdir()
        with patch.object(runtime, 'delete_subvolume_tree') as delete, self.assertRaisesRegex(runtime.Refusal, 'mixed APX'):
            runtime.local_recovery_snapshots('school')
        delete.assert_not_called()

    def test_empty_system_mount_stub_is_allowed(self):
        (self.root / 'system/20260927T161241Z/var/lib/apx').mkdir(parents=True)
        self.assertEqual(runtime.local_recovery_snapshots('school'), ())

    def test_plain_directory_not_accepted_as_btrfs_snapshot(self):
        self.copy()
        with patch.object(runtime, 'run', side_effect=runtime.Refusal('not a subvolume')), self.assertRaises(runtime.Refusal):
            runtime.local_recovery_snapshots('school')

    def test_recovery_lock_rejects_symlink(self):
        victim = self.root / 'victim'; victim.write_text('preserve')
        lock = self.root / 'lock'; lock.symlink_to(victim)
        with patch.object(runtime, 'RECOVERY_LOCK', lock), self.assertRaises(OSError):
            with runtime.local_recovery_lock():
                self.fail('symlink lock admitted')
        self.assertEqual(victim.read_text(), 'preserve')
