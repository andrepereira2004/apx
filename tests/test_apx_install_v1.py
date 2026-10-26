from pathlib import Path
import importlib.machinery
import importlib.util
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]

def load():
    loader=importlib.machinery.SourceFileLoader('installer',str(ROOT/'config/environment-shell-v1/local/bin/apx-install-v1'))
    spec=importlib.util.spec_from_loader(loader.name,loader);module=importlib.util.module_from_spec(spec);loader.exec_module(module);return module

class InstallationTests(unittest.TestCase):
    def test_host_root_is_refused(self):
        m=load()
        with patch.object(m.os,'geteuid',return_value=0):
            with self.assertRaises(RuntimeError):m.require_environment()

    def test_failed_installer_keeps_error_and_does_not_verify(self):
        m=load()
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp, patch.object(m,'verify') as verify:
            with self.assertRaises(RuntimeError):m.install(['/usr/bin/bash','-c','echo simulated-error; exit 4'],['example'],Path(tmp))
            verify.assert_not_called();report=json.loads(next(Path(tmp).glob('*.json')).read_text())
            self.assertEqual(report['status'],'failed');self.assertEqual(report['exit_code'],4)
            self.assertIn('simulated-error',Path(report['log']).read_text())

    def test_exit_zero_is_not_success_without_installed_package(self):
        m=load()
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp, patch.object(m,'verify',side_effect=RuntimeError('missing package')):
            with self.assertRaises(RuntimeError):m.install(['/usr/bin/true'],['example'],Path(tmp))
            self.assertEqual(json.loads(next(Path(tmp).glob('*.json')).read_text())['status'],'failed')

    def test_success_requires_verification_and_catalogue(self):
        m=load()
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp, patch.object(m,'query',side_effect=['example 1','/usr/share/applications/missing.desktop\n']):
            with self.assertRaises(RuntimeError):m.verify(['example'])
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp, patch.object(m,'verify',return_value=[{'package':'example'}]):
            m.install([],['example'],Path(tmp))
            self.assertEqual(json.loads(next(Path(tmp).glob('*.json')).read_text())['status'],'verified')

    def test_runtime_import_failure_is_not_verified(self):
        m=load()
        result=subprocess.CompletedProcess([],1,'','ImportError: Qt_6.12 not found')
        with patch.object(m.subprocess,'run',return_value=result):
            with self.assertRaisesRegex(RuntimeError,'Qt_6.12'):
                m.verify_runtime()

    def test_new_environment_hook_refuses_unmanaged_files(self):
        import ast
        source=(ROOT/'scripts/virtual-lab/apx-lab-runtime.py').read_text()
        tree=ast.parse(source)
        nodes=[n for n in tree.body if (isinstance(n,ast.FunctionDef) and n.name=='configure_environment_application_hook') or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('ENVIRONMENT_APPLICATION_CATALOG_HOOK','ENVIRONMENT_PACKAGE_COHERENCE_HOOK','ENVIRONMENT_PACKAGE_COHERENCE_HELPER') for t in n.targets))]
        scope={'Path':Path,'os':__import__('os'),'Refusal':RuntimeError}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<hook>','exec'),scope)
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            root=Path(tmp);(root/'etc/pacman.d').mkdir(parents=True)
            scope['configure_environment_application_hook'](root)
            target=root/'etc/pacman.d/hooks/99-apx-application-catalog.hook'
            self.assertEqual(target.read_text(),(ROOT/'config/environment-package-install-v1/99-apx-application-catalog.hook').read_text())
            self.assertEqual((root/'etc/pacman.d/hooks/05-apx-package-coherence.hook').read_text(),(ROOT/'config/environment-package-install-v1/05-apx-package-coherence.hook').read_text())
            self.assertEqual((root/'usr/lib/apx/apx-package-coherence-v1.py').read_text(),(ROOT/'config/environment-package-install-v1/apx-package-coherence-v1.py').read_text())
            target.write_text('owner configuration')
            with self.assertRaises(RuntimeError):scope['configure_environment_application_hook'](root)
            self.assertEqual(target.read_text(),'owner configuration')
        with self.assertRaises(RuntimeError):scope['configure_environment_application_hook'](Path('/'))
