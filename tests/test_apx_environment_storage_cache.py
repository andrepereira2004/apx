import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location('storage', ROOT / 'scripts/physical-pilot/apx-environment-storage-runner-v1.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StorageCacheTests(unittest.TestCase):
    def test_unchanged_environment_never_reads_qgroups_or_rewrites_cache(self):
        m = load()
        version = {'root': '1:2:abc', 'home': '2:3:def'}
        old = {'work': {'version': version, 'bytes': 100}}
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'CACHE', Path(tmp) / 'cache.json'), patch.object(m, 'cached_measurements', return_value=old), patch.object(m, 'registered_names', return_value={'work'}), patch.object(m, 'subvolume_versions', return_value={'work': version}), patch.object(m, 'checked', return_value='') as command:
            m.refresh_cache()
            self.assertEqual(command.call_count, 1)
            self.assertEqual(command.call_args.args[0][1:3], ('subvolume', 'list'))
            self.assertFalse(m.CACHE.exists())

    def test_changed_environment_refreshes_and_deleted_entry_is_removed(self):
        m = load()
        old = {'work': {'version': {'root': '1:1:abc', 'home': '2:3:def'}, 'bytes': 100}, 'deleted': {'bytes': 10}}
        version = {'root': '1:2:abc', 'home': '2:3:def'}
        quota = 'Enabled:                 yes\nMode:                    qgroup (full accounting)\nInconsistent:            no\nOverride limits:         no'
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'CACHE', Path(tmp) / 'cache.json'), patch.object(m, 'cached_measurements', return_value=old), patch.object(m, 'registered_names', return_value={'work'}), patch.object(m, 'subvolume_versions', return_value={'work': version}), patch.object(m, 'parse_qgroups', return_value={'work': 200}), patch.object(m, 'checked', side_effect=['', quota, '', '']):
            m.refresh_cache()
            self.assertEqual(json.loads(m.CACHE.read_text())['entries'], {'work': {'version': version, 'bytes': 200}})
            self.assertEqual(m.CACHE.stat().st_mode & 0o777, 0o600)

    def test_bad_quota_does_not_replace_previous_cache(self):
        m = load()
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'CACHE', Path(tmp) / 'cache.json'), patch.object(m, 'cached_measurements', return_value={}), patch.object(m, 'registered_names', return_value={'work'}), patch.object(m, 'subvolume_versions', return_value={}), patch.object(m, 'checked', return_value=''):
            m.CACHE.write_text('previous')
            with self.assertRaises(RuntimeError):
                m.refresh_cache()
            self.assertEqual(m.CACHE.read_text(), 'previous')

    def test_ui_read_does_not_execute_btrfs(self):
        m = load()
        with patch.object(m, 'trusted_json', side_effect=FileNotFoundError), patch.object(m, 'cached_measurements', return_value={'work': {'bytes': 200}}), patch.object(m, 'registered_names', return_value={'work'}), patch.object(m, 'checked', side_effect=AssertionError('must not measure')), patch.object(m.os, 'geteuid', return_value=0), patch.object(m.os, 'statvfs') as fs:
            fs.return_value.f_blocks = 512 * 1024**3
            fs.return_value.f_frsize = 1
            fs.return_value.f_bavail = 200 * 1024**3
            self.assertEqual(m.storage_status()['sizes'], {'work': 200})

    def test_versions_bind_identity_and_changes_exclude_snapshots(self):
        m = load()
        output = 'ID 1 gen 2 top level 261 uuid abc path @apx/environments/work/root\nID 2 gen 3 top level 261 uuid def path @apx/environments/work/home\nID 3 gen 4 top level 261 uuid aaa path @apx/backups/work/root'
        self.assertEqual(m.subvolume_versions(output), {'work': {'root': '1:2:abc', 'home': '2:3:def'}})
