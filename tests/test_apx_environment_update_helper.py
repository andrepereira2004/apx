import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch, Mock

PATH = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-environment-update-v1'
loader = importlib.machinery.SourceFileLoader('environment_update', str(PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
subject = importlib.util.module_from_spec(spec)
loader.exec_module(subject)


class EnvironmentUpdateTests(unittest.TestCase):
    def test_host_root_cannot_run_updates(self):
        with patch.object(subject.os, 'geteuid', return_value=0), patch.object(subject, 'run') as run:
            with self.assertRaises(RuntimeError): subject.update()
            run.assert_not_called()

    def test_full_upgrade_and_both_flatpak_installations(self):
        with patch.object(subject.os, 'geteuid', return_value=1000), \
             patch.object(subject.Path, 'read_text', return_value='systemd-nspawn'), \
             patch.object(subject.shutil, 'which', return_value='/usr/bin/flatpak'), \
             patch.object(subject.subprocess, 'run', return_value=Mock(returncode=1, stdout='', stderr='')), \
             patch.object(subject, 'run') as run:
            subject.update()
            self.assertEqual([call.args for call in run.call_args_list], [
                ('/usr/bin/sudo', '/usr/bin/pacman', '-Syu', '--ignore',
                 'nvidia-utils,lib32-nvidia-utils,opencl-nvidia'),
                ('/usr/bin/flatpak', '--user', 'update'),
                ('/usr/bin/sudo', '/usr/bin/flatpak', '--system', 'update')])

    def test_failed_system_upgrade_stops_before_other_managers(self):
        with patch.object(subject.os, 'geteuid', return_value=1000), \
             patch.object(subject.Path, 'read_text', return_value='systemd-nspawn'), \
             patch.object(subject, 'run', side_effect=subprocess.CalledProcessError(1, 'pacman')) as run:
            with self.assertRaises(subprocess.CalledProcessError): subject.update()
            self.assertEqual(run.call_count, 1)

    def test_foreign_packages_use_unprivileged_aur_helper(self):
        with patch.object(subject.os, 'geteuid', return_value=1000), \
             patch.object(subject.Path, 'read_text', return_value='systemd-nspawn'), \
             patch.object(subject.shutil, 'which', side_effect=lambda n: '/usr/bin/paru' if n == 'paru' else None), \
             patch.object(subject.subprocess, 'run', return_value=Mock(returncode=0, stdout='brave-bin 1.0', stderr='')), \
             patch.object(subject, 'run') as run:
            subject.update()
            self.assertEqual(run.call_args_list[1].args, ('/usr/bin/paru', '-Sua'))
