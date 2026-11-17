import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch, MagicMock
import stat
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/physical-pilot/apx-removable-media-v1.py"
SPEC = importlib.util.spec_from_file_location("apx_removable_media_v1", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RemovableMediaTests(unittest.TestCase):
    def test_safe_unmount_is_not_remounted_until_reconnection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            device = root / 'device'; device.touch()
            lock = root / 'lock'
            with patch.object(MODULE, 'ROOT', root), patch.object(MODULE, 'LOCK', lock), \
                    patch.object(MODULE, 'trusted_device', return_value=device), \
                    patch.object(MODULE, 'device_generation', return_value='6'), \
                    patch.object(MODULE, 'mounted_source', return_value=str(device)), \
                    patch.object(MODULE, 'run', return_value=subprocess.CompletedProcess([], 0)) as command:
                MODULE.unmount_volume('4079-3F8D')
                self.assertEqual(command.call_args.args[0], '/usr/bin/umount')
                self.assertEqual(MODULE.suppression_path('4079-3F8D').read_text(), '6\n')
            with patch.object(MODULE, 'ROOT', root), \
                    patch.object(MODULE, 'trusted_device', return_value=device), \
                    patch.object(MODULE, 'mounted_source', return_value=None), \
                    patch.object(MODULE, 'device_generation', return_value='6'), \
                    patch.object(MODULE, 'run') as command:
                MODULE.refresh_volume('4079-3F8D', 'vfat', root/'USB', '77EA21C2')
                command.assert_not_called()
                with patch.object(MODULE, 'device_generation', return_value='7'):
                    MODULE.refresh_volume('4079-3F8D', 'vfat', root/'USB', '77EA21C2')
                self.assertEqual(command.call_args.args[0], '/usr/bin/mount')
                self.assertFalse(MODULE.suppression_path('4079-3F8D').exists())

    def test_busy_device_is_never_force_unmounted_or_marked_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            device = root / 'device'; device.touch()
            with patch.object(MODULE, 'ROOT', root), patch.object(MODULE, 'LOCK', root/'lock'), \
                    patch.object(MODULE, 'trusted_device', return_value=device), \
                    patch.object(MODULE, 'device_generation', return_value='6'), \
                    patch.object(MODULE, 'mounted_source', return_value=str(device)), \
                    patch.object(MODULE, 'run', return_value=subprocess.CompletedProcess([], 1)) as command:
                with self.assertRaisesRegex(RuntimeError, 'utilização'):
                    MODULE.unmount_volume('4079-3F8D')
                self.assertNotIn('--force', command.call_args.args)
                self.assertFalse(MODULE.suppression_path('4079-3F8D').exists())

    def test_wrong_usb_serial_is_refused(self):
        device = MagicMock()
        device.__str__.return_value = '/dev/sda1'
        device.stat.return_value.st_mode = stat.S_IFBLK
        properties = 'ID_BUS=usb\nID_FS_UUID=4079-3F8D\nID_FS_TYPE=vfat\nID_SERIAL_SHORT=other\n'
        result = subprocess.CompletedProcess([], 0, properties, '')
        with patch.object(MODULE.Path, 'resolve', return_value=device), \
                patch.object(MODULE, 'run', return_value=result):
            with self.assertRaisesRegex(RuntimeError, 'serial identity differs'):
                MODULE.trusted_device('4079-3F8D', 'vfat', '77EA21C2')

    def test_missing_admitted_device_never_mounts(self):
        with patch.object(MODULE, 'trusted_device', return_value=None), \
                patch.object(MODULE, 'mounted_source', return_value=None), \
                patch.object(MODULE, 'run') as command:
            MODULE.refresh_volume('4079-3F8D', 'vfat', Path('/bridge/usb'), '77EA21C2')
            command.assert_not_called()

    def test_covered_mount_does_not_block_recovery(self):
        with patch.object(MODULE.os.path, "ismount", return_value=False), \
                patch.object(MODULE, "run") as command:
            self.assertIsNone(MODULE.mounted_source(MODULE.VOLUME))
            command.assert_not_called()

    def test_repeated_same_source_is_one_identity(self):
        result = subprocess.CompletedProcess([], 0, "/dev/sda1\n/dev/sda1\n", "")
        with patch.object(MODULE.os.path, "ismount", return_value=True), \
                patch.object(MODULE, "run", return_value=result):
            self.assertEqual(MODULE.mounted_source(MODULE.VOLUME), "/dev/sda1")

    def test_conflicting_sources_are_refused(self):
        result = subprocess.CompletedProcess([], 0, "/dev/sda1\n/dev/sdb1\n", "")
        with patch.object(MODULE.os.path, "ismount", return_value=True), \
                patch.object(MODULE, "run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "ambiguous"):
                MODULE.mounted_source(MODULE.VOLUME)


if __name__ == "__main__":
    unittest.main()
