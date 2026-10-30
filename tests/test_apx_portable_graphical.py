import importlib.util
import os
import tempfile
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from apx_portable_hardware import admitted_input, select_display, validate_node


class GenericHardwareTests(unittest.TestCase):
    def test_single_gpu_does_not_require_a_vendor_or_model(self):
        for driver in ("i915", "xe", "amdgpu", "virtio_gpu", "nouveau", "nvidia"):
            gpu = {"driver": driver, "connected": ["Virtual-1"], "boot_vga": False}
            self.assertEqual(select_display([gpu]), gpu)

    def test_connected_gpu_wins_over_disconnected_firmware_default(self):
        unplugged = {"driver": "i915", "connected": [], "boot_vga": True}
        display = {"driver": "amdgpu", "connected": ["DP-3"], "boot_vga": False}
        self.assertEqual(select_display([unplugged, display]), display)

    def test_multiple_eligible_gpus_fail_closed(self):
        with self.assertRaises(ValueError):
            select_display([{"connected": ["DP-1"], "boot_vga": False},
                            {"connected": ["HDMI-A-2"], "boot_vga": False}])
        with self.assertRaises(ValueError):
            select_display([])

    def test_other_seat_and_non_input_nodes_are_not_admitted(self):
        props = {"DEVNAME": "/dev/input/event5", "ID_INPUT": "1", "ID_INPUT_KEYBOARD": "1"}
        self.assertTrue(admitted_input(props, "/dev/input/event5"))
        self.assertFalse(admitted_input({**props, "ID_SEAT": "seat1"}, "/dev/input/event5"))
        self.assertFalse(admitted_input(props, "/dev/nvme0n1"))
        self.assertFalse(admitted_input({**props, "ID_INPUT_KEYBOARD": "0"}, "/dev/input/event5"))

    def test_device_alias_or_wrong_major_is_rejected(self):
        import stat
        from types import SimpleNamespace
        import os
        fake = SimpleNamespace(st_mode=stat.S_IFCHR | 0o660, st_rdev=os.makedev(13, 4))
        with patch.object(Path, "lstat", return_value=fake):
            with self.assertRaises(ValueError): validate_node("/dev/dri/card0", "drm")
            with self.assertRaises(ValueError): validate_node("/dev/nvme0n1", "input")


class FullSourceTests(unittest.TestCase):
    def test_large_private_root_can_register_after_ten_seconds(self):
        spec = importlib.util.spec_from_file_location('portable_registration_test', ROOT / 'scripts/portable/apx-portable-graphical.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        elapsed = [0.0]
        def tick(seconds): elapsed[0] += seconds
        with patch.object(module, 'translated_user', side_effect=[RuntimeError('not yet')]*60+[101000]), \
             patch.object(module, 'run', return_value=SimpleNamespace(returncode=0)), \
             patch.object(module.time, 'monotonic', side_effect=lambda: elapsed[0]), \
             patch.object(module.time, 'sleep', side_effect=tick):
            self.assertEqual(module.wait_translated_user('test-machine','test.service'),101000)
        self.assertGreater(elapsed[0],10)

    def test_registration_wait_is_bounded_and_stopped_units_fail_immediately(self):
        spec = importlib.util.spec_from_file_location('portable_registration_limit_test', ROOT / 'scripts/portable/apx-portable-graphical.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with patch.object(module, 'translated_user', side_effect=RuntimeError('not yet')), \
             patch.object(module, 'run', return_value=SimpleNamespace(returncode=3)), \
             patch.object(module.time, 'sleep') as sleep:
            with self.assertRaisesRegex(RuntimeError,'ended before'): module.wait_translated_user('m','u')
            sleep.assert_not_called()
        elapsed = [0.0]
        def tick(seconds): elapsed[0] += seconds
        with patch.object(module, 'translated_user', side_effect=RuntimeError('not yet')), \
             patch.object(module, 'run', return_value=SimpleNamespace(returncode=0)), \
             patch.object(module.time, 'monotonic', side_effect=lambda: elapsed[0]), \
             patch.object(module.time, 'sleep', side_effect=tick):
            with self.assertRaisesRegex(RuntimeError,'timed out'): module.wait_translated_user('m','u',timeout=1)
        self.assertLessEqual(elapsed[0],1.2)

    @unittest.skipUnless(os.geteuid() == 0, 'udev metadata must be root-owned')
    def test_private_udev_view_excludes_other_devices_and_tags(self):
        spec = importlib.util.spec_from_file_location('portable_graphical_udev', ROOT / 'scripts/portable/apx-portable-graphical.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); source = base / 'udev'
            (source / 'data').mkdir(parents=True); (source / 'tags/seat').mkdir(parents=True)
            for identifier in ('c13:65', 'c13:66'):
                (source / 'data' / identifier).write_text('E:ID_INPUT_KEYBOARD=1\n')
                (source / 'tags/seat' / identifier).touch()
            selected = base / 'selected'
            module.selected_udev_view([{'node': '/dev/input/event1', 'kind': 'input', 'major': 13, 'minor': 65}],
                                      selected, source, base / 'sys-input')
            self.assertEqual({p.name for p in (selected / 'data').iterdir()}, {'c13:65'})
            self.assertEqual({p.name for p in (selected / 'tags/seat').iterdir()}, {'c13:65'})
            self.assertEqual((source / 'data/c13:66').read_text(), 'E:ID_INPUT_KEYBOARD=1\n')

    def test_packaged_shell_is_complete_and_digest_pinned(self):
        path = ROOT / "scripts/portable/install_apx_full.py"
        spec = importlib.util.spec_from_file_location("full_installer_test", path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        hashes = module.verify_sources()
        self.assertIn("config/environment-shell-v1/quickshell/apx/shell.qml", hashes)
        self.assertIn("src/apx_portable_hardware.py", hashes)
        self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in hashes))
        self.assertFalse(any(name.startswith(("/", "audit/", "tmp/")) for name in hashes))

    def test_workload_cannot_satisfy_portable_hub_authority(self):
        path = ROOT / "scripts/portable/apx-portable-services.py"
        spec = importlib.util.spec_from_file_location("portable_services_test", path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        import apx_host_services_peer as peer
        official, shared = peer.authorize_official_hub_peer, peer.authorize_shared_service_peer
        try:
            module.configure_peer()
            identity = peer.ActiveEnvironmentPeer("work", "graphical-base", "generation")
            with patch.object(peer, "authorize_active_environment_peer", return_value=identity):
                with self.assertRaises(peer.HostServicesPeerError):
                    peer.authorize_official_hub_peer(peer.HostServicesPeer(123, 1000, 1000))
            identity = peer.ActiveEnvironmentPeer("hub", "hub", "fresh-generation")
            with patch.object(peer, "authorize_active_environment_peer", return_value=identity):
                peer.authorize_official_hub_peer(peer.HostServicesPeer(123, 1000, 1000))
        finally:
            peer.authorize_official_hub_peer, peer.authorize_shared_service_peer = official, shared


if __name__ == "__main__":
    unittest.main()
