import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/physical-pilot/apx-removable-media-v1.py"
SPEC = importlib.util.spec_from_file_location("apx_removable_media_v1", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RemovableMediaTests(unittest.TestCase):
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
