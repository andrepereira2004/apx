from pathlib import Path
import sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from apx_environment_desktop_defaults import install_flatpak_defaults

class DesktopDefaultsTests(unittest.TestCase):
    def test_install_is_local_pinned_and_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'root';root.mkdir()
            install_flatpak_defaults(root,ROOT/'config/environment-flatpak-v1')
            install_flatpak_defaults(root,ROOT/'config/environment-flatpak-v1')
            self.assertTrue((root/'usr/local/libexec/apx-flatpak-nesting-v1').stat().st_mode&0o100)
            self.assertTrue((root/'etc/systemd/system/multi-user.target.wants/apx-flatpak-nesting-v1.service').is_symlink())

    def test_tampered_seed_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'root';root.mkdir();seed=Path(d)/'seed';seed.mkdir()
            for p in (ROOT/'config/environment-flatpak-v1').iterdir():(seed/p.name).write_bytes(p.read_bytes())
            (seed/'apx-flatpak-nesting-v1').write_text('bad')
            with self.assertRaises(ValueError):install_flatpak_defaults(root,seed)
            self.assertEqual(list(root.iterdir()),[])

    def test_parent_symlink_cannot_write_outside_root(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'root';root.mkdir();outside=Path(d)/'outside';outside.mkdir()
            (root/'usr').symlink_to(outside)
            with self.assertRaises(ValueError):install_flatpak_defaults(root,ROOT/'config/environment-flatpak-v1')
            self.assertEqual(list(outside.iterdir()),[])

    def test_foreign_activation_link_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'root';root.mkdir();p=root/'etc/systemd/system/multi-user.target.wants/apx-flatpak-nesting-v1.service';p.parent.mkdir(parents=True);p.symlink_to('/tmp/foreign')
            with self.assertRaises(ValueError):install_flatpak_defaults(root,ROOT/'config/environment-flatpak-v1')
            self.assertEqual(p.readlink(),Path('/tmp/foreign'))
