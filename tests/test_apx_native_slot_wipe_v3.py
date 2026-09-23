import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import apx_native_slot_wipe_v3 as wipe


class SlotWipeTests(unittest.TestCase):
    def test_exact_regular_file_wipe_preserves_neighbor_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'disk'
            path.write_bytes(b'L' * 4096 + b'S' * 8192 + b'R' * 4096)
            fd = os.open(path, os.O_RDWR)
            try:
                # A partition fd starts at its own byte zero. This small
                # laboratory file models that exact p5 or p6 extent.
                partition = Path(directory) / 'partition'
                partition.write_bytes(b'S' * 8192)
                part_fd = os.open(partition, os.O_RDWR)
                try:
                    wipe.zero_exact_fd(part_fd, 8192)
                finally:
                    os.close(part_fd)
                self.assertEqual(partition.read_bytes(), b'\0' * 8192)
                self.assertEqual(path.read_bytes(), b'L' * 4096 + b'S' * 8192 + b'R' * 4096)
            finally:
                os.close(fd)

    def test_interrupted_wipe_remains_retryable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'partition'
            path.write_bytes(b'X' * 16384)
            fd = os.open(path, os.O_RDWR)
            try:
                real = wipe.os.pwrite
                def interrupted(handle, data, offset):
                    real(handle, data[:4096], offset)
                    raise OSError('simulated interruption')
                with mock.patch.object(wipe.os, 'pwrite', side_effect=interrupted):
                    with self.assertRaises(OSError):wipe.zero_exact_fd(fd, 16384)
                self.assertNotEqual(path.read_bytes(), b'\0' * 16384)
                wipe.zero_exact_fd(fd, 16384)
                self.assertEqual(path.read_bytes(), b'\0' * 16384)
            finally:
                os.close(fd)

    def test_physical_wrapper_rejects_wrong_target_before_open(self):
        with mock.patch.object(wipe.os, 'open') as opened:
            with self.assertRaises(ValueError):
                wipe.wipe_block_partition('/dev/nvme0n1p3', 8192,
                    '11111111-2222-4333-8444-555555555555', 3)
            opened.assert_not_called()
