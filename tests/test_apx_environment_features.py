from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import apx_environment_features as subject


class EnvironmentFeaturesTests(unittest.TestCase):
    @staticmethod
    def runtime():
        path = Path(__file__).resolve().parents[1] / "scripts/virtual-lab/apx-lab-runtime.py"
        spec = importlib.util.spec_from_file_location("feature_runtime", path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def test_catalogue_has_three_presets_and_twenty_modules(self):
        self.assertEqual(tuple(subject.PRESETS), ("basic", "intermediate", "complete"))
        self.assertEqual(len(subject.MODULES), 20)
        self.assertEqual(subject.PRESETS["basic"], ("system", "cli-aur"))
        self.assertEqual(len(subject.PRESETS["intermediate"]), 17)
        for module in ("multimedia", "communication", "printing-scanning"):
            self.assertIn(module, subject.PRESETS["intermediate"])
        for module in ("office", "development"):
            self.assertNotIn(module, subject.PRESETS["intermediate"])
        self.assertEqual(subject.PRESETS["complete"], tuple(m for m in subject.MODULES if m != "iphone-integration"))
        self.assertIn("files", subject.PRESETS["intermediate"])
        self.assertIn("files", subject.PRESETS["complete"])
        self.assertEqual(set(subject.local_packages_for(["office"])), {"brave-bin", "gridcraft", "wordcraft", "deckcraft"})

    def test_iphone_integration_is_opt_in_and_does_not_grant_lan_authority(self):
        for preset in subject.PRESETS.values():
            self.assertNotIn('iphone-integration', preset)
            self.assertNotIn('localsend-bin', subject.local_packages_for(preset))
        modules = subject.normalize_modules(['iphone-integration'])
        self.assertIn('desktop-integration', modules)
        self.assertIn('network', modules)
        self.assertIn('localsend-bin', subject.local_packages_for(modules))
        self.assertTrue({'libayatana-appindicator', 'libayatana-indicator', 'ayatana-ido'} <= set(subject.packages_for(modules)))
        self.assertFalse(any(x in subject.packages_for(modules) for x in ['networkmanager', 'kdeconnect', 'plasma-desktop']))

    def test_dependencies_are_closed_and_package_plan_is_fixed(self):
        modules = subject.normalize_modules(["printing-scanning"])
        for required in ("system", "graphical", "desktop-integration", "network",
                         "devices-storage", "printing-scanning"):
            self.assertIn(required, modules)
        packages = subject.packages_for(subject.PRESETS["complete"])
        for required in ("evince", "cups", "podman", "rust"):
            self.assertIn(required, packages)
        for required in ("thunar-archive-plugin", "xarchiver", "7zip", "unzip", "zip",
                         "unrar", "ffmpegthumbnailer", "poppler-glib", "catfish"):
            self.assertIn(required, subject.packages_for(["files"]))
        self.assertNotIn("firefox", packages)
        self.assertFalse(any(p.startswith("libreoffice") for p in subject.packages_for(subject.MODULES)))
        self.assertEqual(subject.packages_for(subject.PRESETS["basic"]), ("xfce4-taskmanager",))
        self.assertIn("pipewire-alsa", subject.packages_for(["audio"]))
        self.assertIn("noto-fonts-emoji", subject.packages_for(["locale-input"]))
        self.assertEqual(subject.local_packages_for(["web-documents"]), ("brave-bin",))
        for preset in subject.PRESETS.values():
            self.assertIn("xfce4-taskmanager", subject.packages_for(preset))
            self.assertIn("brave-bin", subject.local_packages_for(preset))
        self.assertIn("egl-wayland", subject.packages_for(["graphics"]))
        self.assertIn("nvidia-utils", subject.local_packages_for(["graphics"]))
        self.assertGreater(subject.estimated_mib(subject.PRESETS["complete"]), 4000)

    def test_unknown_and_empty_selections_fail_closed(self):
        for values in ([], ["unknown"], "system"):
            with self.assertRaises(ValueError):
                subject.normalize_modules(values)

    def test_graphical_creation_never_restores_retired_face_auth(self):
        runtime = self.runtime()
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary)
            hub = state / "environments/hub/root/etc"; hub.mkdir(parents=True)
            target = state / "target"; (target / "etc").mkdir(parents=True)
            (hub / "shadow").write_text("apx:$6$hub-hash:1:2:3:4:5:6:7\n")
            (target / "etc/shadow").write_text("apx:!:8:9:10:11:12:13:14\n")
            for path in (hub / "shadow", target / "etc/shadow"):
                path.chmod(0o600)
            (state / "face-auth-v1").mkdir()
            (state / "face-auth-v1/manifest.json").write_text('{"enabled":true}')
            calls = []
            with mock.patch.object(runtime, "ENVIRONMENTS", state / "environments"), \
                    mock.patch.object(runtime, "packages_for", return_value=()), \
                    mock.patch.object(runtime, "local_packages_for", return_value=()), \
                    mock.patch.object(runtime, "host_nvidia_version", return_value="610.43.03"), \
                    mock.patch.object(runtime, "validated_local_package_artifact",
                                      side_effect=lambda package: state / (package + "-610.43.03-3-x86_64.pkg.tar.zst")), \
                    mock.patch.object(runtime, "run", side_effect=lambda command: calls.append(command)):
                runtime.configure_environment_features(target, {
                    "desktop_preset": "intermediate", "desktop_modules": list(subject.PRESETS["intermediate"]),
                })
            serialized = json.dumps(calls)
            for removed in ("howdy", "python-dlib", "python-opencv", "cblas", "lapack"):
                self.assertNotIn(removed, serialized)
            self.assertNotIn("howdy-apx", runtime.LOCAL_PACKAGE_MANIFESTS)
            self.assertNotIn("python-dlib", runtime.LOCAL_PACKAGE_MANIFESTS)
            self.assertFalse((target / "etc/howdy").exists())
            self.assertIn("$6$hub-hash", (target / "etc/shadow").read_text())

    def test_alternate_private_root_uses_a_complete_arch_upgrade(self):
        source = (Path(__file__).resolve().parents[1]
                  / "scripts/virtual-lab/apx-lab-runtime.py").read_text()
        self.assertIn('"--ignore", "nvidia-utils,lib32-nvidia-utils",\n             "-Syu", "--needed", "--noconfirm"', source)
        self.assertNotIn('"--disable-sandbox", "-Sy", "--needed", "--noconfirm"', source)
        self.assertIn('"--root", str(root)', source)
        self.assertIn('"--dbpath", str(root / "var/lib/pacman")', source)
        self.assertIn('disabled = "#[multilib]\\n#Include = /etc/pacman.d/mirrorlist\\n"', source)

    def test_brave_artifact_is_host_owned_and_digest_pinned(self):
        runtime = self.runtime()
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            artifact = directory / "brave-bin-1-1-x86_64.pkg.tar.zst"
            artifact.write_bytes(b"reviewed-brave-package")
            manifest = {
                "schema": 1,
                "package": "brave-bin",
                "filename": artifact.name,
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            }
            (directory / "brave-bin-v1.json").write_text(json.dumps(manifest))
            with mock.patch.object(runtime, "LOCAL_PACKAGE_ARTIFACTS", directory):
                self.assertEqual(runtime.validated_local_package_artifact("brave-bin"), artifact)
                manifest["sha256"] = "0" * 64
                (directory / "brave-bin-v1.json").write_text(json.dumps(manifest))
                with self.assertRaises(runtime.Refusal):
                    runtime.validated_local_package_artifact("brave-bin")

    def test_creation_inherits_only_hub_password_hash_and_records_features(self):
        runtime = self.runtime()
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary)
            hub = state / "environments/hub/root/etc"; hub.mkdir(parents=True)
            target = state / "target"; (target / "etc").mkdir(parents=True)
            (hub / "shadow").write_text("apx:$6$hub-hash:1:2:3:4:5:6:7\n")
            (target / "etc/shadow").write_text("apx:!:8:9:10:11:12:13:14\n")
            (hub / "shadow").chmod(0o600)
            (target / "etc/shadow").chmod(0o600)
            with mock.patch.object(runtime, "ENVIRONMENTS", state / "environments"), \
                    mock.patch.object(runtime, "packages_for", return_value=()), \
                    mock.patch.object(runtime, "local_packages_for", return_value=()), \
                    mock.patch.object(runtime, "host_nvidia_version", return_value="610.43.03"), \
                    mock.patch.object(runtime, "validated_local_package_artifact",
                                      return_value=state / "nvidia-utils-610.43.03-3-x86_64.pkg.tar.zst"), \
                    mock.patch.object(runtime, "run") as run:
                runtime.configure_environment_features(target, {
                    "desktop_preset": "basic", "desktop_modules": ["system", "cli-aur"],
                })
            commands = [call.args[0] for call in run.call_args_list]
            self.assertIn("egl-wayland", commands[0])
            self.assertIn("--ignore", commands[0])
            self.assertIn("nvidia-utils,lib32-nvidia-utils", commands[0])
            self.assertIn(str(state / "nvidia-utils-610.43.03-3-x86_64.pkg.tar.zst"), commands[1])
            fields = (target / "etc/shadow").read_text().strip().split(":")
            self.assertEqual(fields[1], "$6$hub-hash")
            self.assertEqual(fields[2:], ["8", "9", "10", "11", "12", "13", "14"])
            feature = (target / "etc/apx/environment-features.json").read_text()
            self.assertIn('"preset":"basic"', feature)

    @unittest.skipUnless(os.geteuid() == 0, "shifted-owner fixture requires root")
    def test_running_private_user_hub_shadow_owner_is_admitted(self):
        runtime = self.runtime()
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary)
            hub_root = state / "environments/hub/root"
            hub_etc = hub_root / "etc"; hub_etc.mkdir(parents=True)
            target = state / "target"; (target / "etc").mkdir(parents=True)
            (hub_etc / "shadow").write_text("apx:$6$shifted-hash:1:2:3:4:5:6:7\n")
            (target / "etc/shadow").write_text("apx:!:8:9:10:11:12:13:14\n")
            (hub_etc / "shadow").chmod(0o600)
            (target / "etc/shadow").chmod(0o600)
            for path in (hub_root, hub_etc, hub_etc / "shadow"):
                os.chown(path, 1278869504, 1278869504)
            with mock.patch.object(runtime, "ENVIRONMENTS", state / "environments"), \
                    mock.patch.object(runtime, "packages_for", return_value=()), \
                    mock.patch.object(runtime, "local_packages_for", return_value=()), \
                    mock.patch.object(runtime, "host_nvidia_version", return_value="610.43.03"), \
                    mock.patch.object(runtime, "validated_local_package_artifact",
                                      return_value=state / "nvidia-utils-610.43.03-3-x86_64.pkg.tar.zst"), \
                    mock.patch.object(runtime, "run"):
                runtime.configure_environment_features(target, {
                    "desktop_preset": "basic", "desktop_modules": ["system", "cli-aur"],
                })
            self.assertIn("$6$shifted-hash", (target / "etc/shadow").read_text())


if __name__ == "__main__":
    unittest.main()
