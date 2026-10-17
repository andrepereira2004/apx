from pathlib import Path
import hashlib
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import apx_face_auth as subject


class FaceIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / "identity"
        self.directory.mkdir(mode=0o700)
        self.data = {
            "config.ini": b"[core]\ndisabled=false\nabort_if_ssh=true\n[snapshots]\nsave_failed=false\nsave_successful=false\n",
            "apx.dat": b"synthetic identity; never a real enrolled face",
            "hyprlock.pam": (Path(__file__).resolve().parents[1] / "config/howdy-v1/pam/hyprlock-workload").read_bytes(),
        }
        self.save()

    def save(self):
        for name, value in self.data.items():
            path = self.directory / name
            path.write_bytes(value)
            path.chmod(0o600)
        record = {"schema": 1, "enabled": True, "files": {
            name: hashlib.sha256(value).hexdigest() for name, value in self.data.items()
        }}
        (self.directory / "manifest.json").write_text(json.dumps(record))

    def test_absent_enrollment_keeps_password_only(self):
        self.assertIsNone(subject.load_identity(self.directory / "absent"))

    def test_owner_can_disable_enrollment_for_future_creation(self):
        path = self.directory / "manifest.json"
        record = json.loads(path.read_text())
        record["enabled"] = False
        path.write_text(json.dumps(record))
        self.assertIsNone(subject.load_identity(self.directory))

    def test_corrupt_model_refuses_before_copy(self):
        (self.directory / "apx.dat").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "digest"):
            subject.load_identity(self.directory)

    def test_linked_model_is_rejected(self):
        target = self.directory / "apx.dat"
        target.rename(self.directory / "real")
        target.symlink_to("real")
        with self.assertRaises(ValueError):
            subject.load_identity(self.directory)

    def test_public_identity_directory_is_rejected(self):
        self.directory.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "private"):
            subject.load_identity(self.directory)

    def test_camera_images_or_remote_auth_are_rejected(self):
        for value in (self.data["config.ini"].replace(b"save_failed=false", b"save_failed=true"),
                      self.data["config.ini"].replace(b"abort_if_ssh=true", b"abort_if_ssh=false")):
            self.data["config.ini"] = value
            self.save()
            with self.assertRaises(ValueError):
                subject.load_identity(self.directory)

    def test_password_fallback_cannot_be_removed(self):
        self.data["hyprlock.pam"] = b"auth sufficient pam_howdy.so\n"
        self.save()
        with self.assertRaisesRegex(ValueError, "fallback"):
            subject.load_identity(self.directory)

    def test_install_is_independent_and_preserves_sudo(self):
        data = subject.load_identity(self.directory)
        roots = []
        for name in ("first", "second"):
            root = self.directory.parent / name
            (root / "etc/pam.d").mkdir(parents=True)
            (root / "etc/group").write_text("root:x:0:\napx:x:1000:\n")
            (root / "etc/pam.d/sudo").write_text("original sudo password policy")
            subject.install_identity(root, data)
            model = root / "etc/howdy/models/apx.dat"
            self.assertEqual(model.stat().st_mode & 0o777, 0o640)
            self.assertEqual(model.stat().st_gid, 1000)
            self.assertEqual((root / "etc/pam.d/sudo").read_text(), "original sudo password policy")
            roots.append(root)
        first = roots[0] / "etc/howdy/models/apx.dat"
        second = roots[1] / "etc/howdy/models/apx.dat"
        self.assertNotEqual(first.stat().st_ino, second.stat().st_ino)
        first.write_bytes(b"independent modification")
        self.assertEqual(second.read_bytes(), self.data["apx.dat"])

    def test_shifted_active_root_ownership(self):
        root = self.directory.parent / "active"
        (root / "etc/pam.d").mkdir(parents=True)
        group = root / "etc/group"
        group.write_text("root:x:0:\napx:x:1000:\n")
        offset = 1238630400
        for path in (root, root / "etc", root / "etc/pam.d", group):
            os.chown(path, offset, offset)
        subject.install_identity(root, subject.load_identity(self.directory))
        metadata = (root / "etc/howdy/models/apx.dat").stat()
        self.assertEqual((metadata.st_uid, metadata.st_gid), (offset, offset + 1000))


if __name__ == "__main__":
    unittest.main()
