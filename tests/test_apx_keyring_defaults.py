import os
from pathlib import Path
import runpy
import tempfile
import unittest

PREPARE = runpy.run_path(str(Path(__file__).resolve().parents[1] / "config/environment-shell-v1/local/bin/apx-keyring-prepare-v1"))["prepare"]


class KeyringDefaultsTests(unittest.TestCase):
    def test_empty_home_gets_private_default_and_second_run_preserves_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            self.assertTrue(PREPARE(home))
            directory = home / ".local/share/keyrings"
            self.assertEqual((directory / "default").read_text(), "login\n")
            self.assertEqual((directory / "login.keyring").stat().st_mode & 0o777, 0o600)
            self.assertFalse(PREPARE(home))

    def test_existing_credentials_are_never_overwritten_or_reselected(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            directory = home / ".local/share/keyrings"
            directory.mkdir(parents=True)
            existing = directory / "custom.keyring"
            existing.write_bytes(b"existing-encrypted-data")
            self.assertFalse(PREPARE(home))
            self.assertEqual(existing.read_bytes(), b"existing-encrypted-data")
            self.assertEqual(list(directory.iterdir()), [existing])

    def test_symlinked_keyring_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / ".local/share").mkdir(parents=True)
            (home / "elsewhere").mkdir()
            (home / ".local/share/keyrings").symlink_to(home / "elsewhere")
            with self.assertRaises(RuntimeError):
                PREPARE(home)

