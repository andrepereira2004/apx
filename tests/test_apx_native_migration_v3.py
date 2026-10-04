import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import apx_native_migration_v3 as migration

class RelocationTests(unittest.TestCase):
    def test_interrupted_copy_can_restore_original_from_verified_image(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            disk, original, prepared = root/'disk', root/'original', root/'prepared'
            original.write_bytes(b'O' * 8192)
            prepared.write_bytes(b'N' * 8192)
            disk.write_bytes(b'L' * 4096 + original.read_bytes() + b'R' * 4096)
            before = disk.read_bytes()
            real_write = migration.os.pwrite
            def interrupted(fd, data, offset):
                real_write(fd, data[:4096], offset)
                raise OSError('simulated power loss')
            with mock.patch.object(migration.os, 'pwrite', side_effect=interrupted):
                with self.assertRaises(OSError):
                    migration.relocate_image(disk, prepared, start_bytes=4096,
                        image_bytes=8192, image_sha256=hashlib.sha256(prepared.read_bytes()).hexdigest(),
                        journal=root/'new-copy.json', plan_sha256='plan-a')
            self.assertNotEqual(disk.read_bytes(), before)
            migration.relocate_image(disk, original, start_bytes=4096,
                image_bytes=8192, image_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                journal=root/'restore-original.json', plan_sha256='plan-a')
            self.assertEqual(disk.read_bytes(), before)
            self.assertEqual(json.loads((root/'restore-original.json').read_text())['state'], 'verified')

    def test_interrupted_copy_resumes_without_touching_neighbor_extents(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);disk=root/'disk';image=root/'prepared';journal=root/'journal.json'
            disk.write_bytes(b'A'*4096+b'B'*8192+b'C'*4096)
            image.write_bytes(b'W'*8192)
            args=dict(start_bytes=4096,image_bytes=8192,image_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),journal=journal,plan_sha256='plan-a')
            real_write=migration.os.pwrite
            def interrupted(fd,data,offset):
                real_write(fd,data[:4096],offset)
                raise OSError('simulated power loss')
            with mock.patch.object(migration.os,'pwrite',side_effect=interrupted):
                with self.assertRaises(OSError):migration.relocate_image(disk,image,**args)
            self.assertEqual(json.loads(journal.read_text())['state'],'copying')
            migration.relocate_image(disk,image,**args)
            self.assertEqual(disk.read_bytes(),b'A'*4096+b'W'*8192+b'C'*4096)
            with mock.patch.object(migration,'copy_range') as copy:
                migration.relocate_image(disk,image,**args)
                copy.assert_not_called()
            self.assertEqual(json.loads(journal.read_text())['state'],'verified')
            with self.assertRaises(ValueError):migration.relocate_image(disk,image,**(args|{'plan_sha256':'different-plan'}))

    def test_corrupt_backup_never_changes_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);disk=root/'disk';image=root/'image';journal=root/'journal'
            disk.write_bytes(b'A'*8192);image.write_bytes(b'W'*4096)
            with self.assertRaises(ValueError):
                migration.relocate_image(disk,image,start_bytes=4096,image_bytes=4096,image_sha256='bad',journal=journal,plan_sha256='p')
            self.assertEqual(disk.read_bytes(),b'A'*8192)
            self.assertFalse(journal.exists())

    def test_nonregular_and_symlink_disks_are_rejected(self):
        with self.assertRaises(ValueError):migration.open_regular('/dev/null',migration.os.O_RDWR)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'link';path.symlink_to('/dev/null')
            with self.assertRaises(OSError):migration.open_regular(path,migration.os.O_RDWR)
