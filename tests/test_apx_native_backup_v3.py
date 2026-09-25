import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import apx_native_backup_v3 as backup


class NativeBackupTests(unittest.TestCase):
    def test_source_fingerprint_detects_changes_outside_ntfs_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source'
            source.write_bytes(b'A' * 8192)
            before = backup.source_fingerprint(source)
            with source.open('r+b') as stream:
                stream.seek(4096)
                stream.write(b'B')
            self.assertEqual(before['bytes'], 8192)
            self.assertNotEqual(backup.source_fingerprint(source), before)

    def test_invalid_size_and_symlink_source_rejected_before_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.write_bytes(b'not-a-filesystem')
            link = root / 'link'
            link.symlink_to(source)
            with mock.patch.object(backup, 'run') as run:
                for value in (True, -4096, 4097):
                    with self.assertRaises(ValueError):
                        backup.prepare_images(source, root / 'output', value)
                with self.assertRaises(ValueError):
                    backup.prepare_images(link, root / 'output', 4096)
                run.assert_not_called()

    def test_failure_preserves_partial_backup_and_records_stage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.write_bytes(b'original')
            def run(*args):
                if args[0].endswith('ntfsresize'):
                    return subprocess.CompletedProcess(args, 0, 'You might resize at 4096 bytes')
                (root / 'output' / 'original.ntfs.raw').write_bytes(b'partial')
                raise subprocess.CalledProcessError(1, args)
            with mock.patch.object(backup, 'run', side_effect=run):
                with self.assertRaises(subprocess.CalledProcessError):
                    backup.prepare_images(source, root / 'output', 8192)
            self.assertEqual(source.read_bytes(), b'original')
            self.assertEqual((root / 'output' / 'original.ntfs.raw').read_bytes(), b'partial')
            self.assertIn('clone-original', (root / 'output' / 'failed.json').read_text())

    @unittest.skipUnless(all(shutil.which(tool) for tool in ('mkntfs', 'ntfscp', 'ntfscat', 'ntfsclone', 'ntfsresize')), 'NTFS image tools unavailable')
    def test_real_image_resize_preserves_source_backup_and_file_contents(self):
        # Repository storage permits Btrfs reflink; never touches a block device.
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            root = Path(directory)
            probe = root / 'probe'; probe.write_bytes(b'probe')
            result = subprocess.run(['cp', '--reflink=always', str(probe), str(root / 'copy')], capture_output=True)
            if result.returncode:
                self.skipTest('test filesystem has no reflink support')
            source = root / 'source.ntfs'
            with source.open('wb') as stream:
                stream.truncate(128 * 1024**2)
            backup.run('mkntfs', '-F', '-Q', str(source))
            payload = root / 'payload'; payload.write_bytes(bytes(range(256)) * 4096)
            backup.run('ntfscp', str(source), str(payload), '/payload.bin')
            before = backup.image_hash(source)
            original_fingerprint = backup.source_fingerprint(source)
            metadata_name = 'APX-12345678-1234-1234-1234-123456789abc.ini'
            manifest = backup.prepare_images(source, root / 'output', 96 * 1024**2, prepared_metadata=(metadata_name, b'generation=test\n'), plan_sha256='a' * 64)
            metadata = subprocess.run(['ntfscat', '--force', str(root / 'output' / 'prepared.ntfs.raw'), '/' + metadata_name], check=True, capture_output=True).stdout
            self.assertEqual(metadata, b'generation=test\n')
            self.assertEqual(backup.image_hash(source), before)
            self.assertEqual(manifest['state'], 'verified-images')
            self.assertEqual(manifest['source_fingerprint'], original_fingerprint)
            self.assertEqual(manifest['plan_sha256'], 'a' * 64)
            self.assertEqual(manifest['prepared']['bytes'], 96 * 1024**2)
            for name in ('original.ntfs.raw', 'prepared.ntfs.raw'):
                content = subprocess.run(['ntfscat', '--force', str(root / 'output' / name), '/payload.bin'], check=True, capture_output=True).stdout
                self.assertEqual(hashlib.sha256(content).digest(), hashlib.sha256(payload.read_bytes()).digest())
