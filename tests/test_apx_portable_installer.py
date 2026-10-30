"""Portable installation admission and fail-closed Btrfs accounting checks."""
import importlib.util
from pathlib import Path
import tempfile
import subprocess
import shutil
from types import SimpleNamespace
import contextlib
import io
import unittest
from unittest.mock import patch

PATH = Path(__file__).parents[1] / 'scripts/portable/install_apx_arch.py'
spec = importlib.util.spec_from_file_location('portable_installer', PATH)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class PortableInstallerTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('findmnt'), 'Linux findmnt required')
    def test_status_accepts_state_directory_without_its_own_mount(self):
        spec = importlib.util.spec_from_file_location(
            'portable_runtime_status', PATH.parents[1] / 'virtual-lab/apx-lab-runtime.py')
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / 'plain-state'; state.mkdir()
            expected = subprocess.check_output(
                ['findmnt', '-n', '-T', str(state), '-o', 'FSTYPE'], text=True).strip()
            real_run = runtime.run
            def run(command, **kwargs):
                if command[0] == 'systemctl':
                    return SimpleNamespace(stdout='', returncode=0)
                return real_run(command, **kwargs)
            output = io.StringIO()
            with patch.object(runtime, 'STATE', state), patch.object(runtime, 'ENVIRONMENTS', state / 'environments'), \
                 patch.object(runtime, 'run', side_effect=run), contextlib.redirect_stdout(output):
                runtime.status()
            self.assertIn('filesystem=' + expected, output.getvalue())

    def test_quota_state_refuses_partial_inconsistent_or_simple_accounting(self):
        healthy = 'Enabled: yes\nMode: qgroup (full accounting)\nInconsistent: no\nOverride limits: no\n'
        self.assertEqual(installer.quota_state(healthy), 'healthy')
        self.assertEqual(installer.quota_state('Enabled: no\n'), 'disabled')
        for text in ('', 'Enabled: yes', healthy + 'Enabled: yes\n',
                     healthy.replace('Inconsistent: no', 'Inconsistent: yes'),
                     healthy.replace('qgroup (full accounting)', 'squota'),
                     healthy + 'Rescan status: running\n', healthy + 'Status: enabled\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                installer.quota_state(text)

    def test_non_root_refused_before_commands(self):
        with patch.object(installer.os, 'geteuid', return_value=1000), patch.object(installer, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'root'):
                installer.preflight()
            run.assert_not_called()

    def test_checkpoint_keeps_failed_phase_and_private_permissions(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(installer, 'STATE', Path(directory)):
            record = {'schema': 1, 'profile': 'portable-headless-v1'}
            installer.checkpoint(record, 'started')
            installer.checkpoint(record, 'runtime-installed')
            path = Path(directory) / 'portable-install.json'
            self.assertIn('runtime-installed', path.read_text())
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertFalse(path.with_suffix('.tmp').exists())

    def test_releases_never_use_live_hub_as_source(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory, patch.object(installer, 'STATE', Path(directory)):
            (Path(directory) / 'releases').mkdir()
            def fake_run(*args, **kwargs):
                calls.append(args)
                if args[:3] == ('btrfs', 'subvolume', 'create'):
                    root = Path(args[3]); (root / 'etc').mkdir(parents=True)
                return ''
            with patch.object(installer, 'run', side_effect=fake_run):
                installer.release('minimal')
            self.assertTrue(any(c[0] == 'pacstrap' and '-K' in c for c in calls))
            trust = next(i for i,c in enumerate(calls) if '--populate' in c)
            package_install = next(i for i,c in enumerate(calls) if c[0] == 'pacstrap')
            self.assertLess(trust, package_install)
            self.assertFalse(any('snapshot' in c for c in calls))
            self.assertEqual(calls[-1][-2:], ('ro', 'true'))

    def test_preflight_refuses_existing_install_before_package_transaction(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / 'apx'; state.mkdir(); (state / 'registration.json').write_text('{}')
            real_is_dir = Path.is_dir
            with patch.object(installer, 'STATE', state), patch.object(installer.os, 'geteuid', return_value=0), \
                 patch.object(Path, 'read_text', return_value='ID=arch\n'), \
                 patch.object(Path, 'is_dir', autospec=True, side_effect=lambda p: True if str(p) == '/run/systemd/system' else real_is_dir(p)), \
                 patch.object(installer.os, 'uname', return_value=SimpleNamespace(machine='x86_64')), \
                 patch.object(installer.subprocess, 'run') as subprocess_run, patch.object(installer, 'run') as run:
                subprocess_run.return_value.returncode = 1
                with self.assertRaisesRegex(ValueError, 'existing APX'):
                    installer.preflight()
                run.assert_not_called()

    def test_runtime_entrypoint_resolves_its_usr_bin_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); library = root / 'lib'; library.mkdir()
            wrapper = library / 'apx-lab-runtime.py'
            shutil.copy2(PATH.with_name('apx-portable-runtime.py'), wrapper)
            (library / 'apx-lab-runtime-core.py').write_text('import subprocess\nclass Refusal(RuntimeError): pass\nROLES = set()\ndef main(): return 0\n')
            entrypoint = root / 'apx'; entrypoint.symlink_to(wrapper)
            result = subprocess.run(['python', str(entrypoint)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
