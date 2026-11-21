import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import apx_portable_packages as packages
import apx_portable_provision as provision
from apx_environment_features import PRESETS, OPTIONAL_MODULES

SEED = ROOT / 'config/portable-packages-v2'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class PortablePackagesTests(unittest.TestCase):
    def test_seed_has_public_key_recipes_and_reviewed_offline_application(self):
        values = packages.verify_seed(SEED)
        self.assertIn('chatgpt-release-keyring.gpg', values)
        for name in ('brave-bin', 'localsend-bin', 'deckcraft'):
            self.assertIn(name + '.json', values)
        with tempfile.TemporaryDirectory() as temp:
            artifact = packages.resolve('salvador-de-mundos-apx', Path(temp) / 'packages', SEED)
            self.assertEqual(packages.upstream.package_info(artifact)['pkgname'], 'salvador-de-mundos-apx')
            self.assertEqual(packages.resolve('salvador-de-mundos-apx', artifact.parent, SEED), artifact)

    def test_restrictive_executor_umask_does_not_make_public_packages_unreadable(self):
        import os
        with tempfile.TemporaryDirectory() as temp:
            previous=os.umask(0o077)
            try:
                artifact=packages.resolve('salvador-de-mundos-apx',Path(temp)/'cache',SEED)
                self.assertEqual(artifact.parent.stat().st_mode&0o777,0o755)
                self.assertEqual(artifact.stat().st_mode&0o777,0o644)
            finally:os.umask(previous)

    def test_modified_or_missing_seed_refused_before_network(self):
        for operation in ('change', 'delete', 'link'):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as temp:
                seed = Path(temp) / 'seed'; shutil.copytree(SEED, seed)
                path = seed / 'brave-bin.json'
                if operation == 'change': path.write_text('{}')
                elif operation == 'delete': path.unlink()
                else:
                    path.unlink();path.symlink_to(SEED / 'brave-bin.json')
                with patch.object(packages.upstream, 'latest_release') as network:
                    with self.assertRaises(packages.upstream.FreshnessError):
                        packages.resolve('brave-bin', Path(temp) / 'cache', seed)
                    network.assert_not_called()

    def test_brave_bootstraps_from_verified_upstream_without_pilot_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); vendor = base / 'vendor.zip'
            with zipfile.ZipFile(vendor, 'w') as archive:
                archive.writestr('brave', 'vendor-program')
            release = dict(tag_name='v9.8.7', draft=False, prerelease=False, assets=[{
                'name': 'brave-browser-9.8.7-linux-amd64.zip',
                'browser_download_url': 'https://github.com/brave/brave-browser/releases/download/v9.8.7/brave-browser-9.8.7-linux-amd64.zip',
                'digest': 'sha256:' + hashlib.sha256(vendor.read_bytes()).hexdigest()}])
            def download(url, target, digest):
                self.assertEqual(hashlib.sha256(vendor.read_bytes()).hexdigest(), digest)
                shutil.copyfile(vendor, target)
            with patch.object(packages.upstream, 'latest_release', return_value=release), \
                    patch.object(packages.upstream, 'download', side_effect=download) as fetch:
                artifact = packages.resolve('brave-bin', base / 'cache', SEED)
                self.assertEqual(packages.upstream.package_info(artifact)['pkgver'], '1:9.8.7-1')
                with tarfile.open(artifact) as archive:
                    self.assertEqual(archive.extractfile('opt/brave-bin/brave').read(), b'vendor-program')
                    self.assertIn('usr/bin/brave', archive.getnames())
                    self.assertTrue(any(p.startswith('usr/share/icons/') for p in archive.getnames()))
                self.assertEqual(packages.resolve('brave-bin', base / 'cache', SEED), artifact)
                self.assertEqual(fetch.call_count, 1)
                artifact.write_bytes(b'changed')
                with self.assertRaises(packages.upstream.FreshnessError):
                    packages.resolve('brave-bin', base / 'cache', SEED)

    def test_failed_vendor_verification_never_publishes_or_reuses_old_package(self):
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp) / 'cache'
            with patch.object(packages.upstream, 'latest_release', side_effect=RuntimeError('offline')):
                with self.assertRaisesRegex(RuntimeError, 'offline'):
                    packages.resolve('brave-bin', cache, SEED)
            self.assertFalse((cache / 'brave-bin-v1.json').exists())
            self.assertEqual(list(cache.glob('*.pkg.tar.zst')), [])

    def test_office_bootstraps_without_a_previous_package_template(self):
        for package in ('gridcraft', 'wordcraft', 'deckcraft'):
            with self.subTest(package=package), tempfile.TemporaryDirectory() as temp:
                base = Path(temp); vendor = base / 'vendor.pkg.tar.zst'
                with tarfile.open(vendor, 'w:zst') as archive:
                    for name, data in {'.PKGINFO': ('pkgname = ai.storyteller.' + package + '\npkgver = 9.8.7-1\narch = x86_64\n').encode(),
                                       'usr/bin/' + package: b'vendor-program'}.items():
                        member = tarfile.TarInfo(name); member.size = len(data); member.mode = 0o755
                        archive.addfile(member, io.BytesIO(data))
                release = dict(tag_name='v9.8.7')
                with patch.object(packages.upstream, 'latest_release', return_value=release), \
                        patch.object(packages.upstream, 'github_asset', return_value=('https://vendor/package','0'*64)), \
                        patch.object(packages.upstream, 'download', side_effect=lambda url,path,digest:shutil.copyfile(vendor,path)):
                    artifact = packages.resolve(package, base / 'cache', SEED)
                self.assertEqual(packages.upstream.package_info(artifact)['pkgname'], package)
                self.assertEqual(packages.upstream.package_info(artifact)['pkgver'], '9.8.7-1')
                if package == 'deckcraft':
                    with tarfile.open(artifact) as archive:
                        self.assertEqual(archive.extractfile('usr/lib/deckcraft/deckcraft').read(),b'vendor-program')
                        self.assertIn('usr/bin/deckcraft',archive.getnames())

    def test_chatgpt_signature_failure_never_publishes(self):
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp) / 'cache'
            with patch.object(packages.upstream, 'openai_latest', return_value=('1.0-1','chatgpt-bin-1.0-1-x86_64.pkg.tar.zst','https://vendor/pkg','0'*64)), \
                    patch.object(packages.upstream, 'download', side_effect=lambda url,path,digest:path.write_bytes(b'package')), \
                    patch.object(packages.upstream, 'fetch', return_value=b'signature'), \
                    patch.object(packages.upstream, 'verify_signature', side_effect=RuntimeError('bad signature')):
                with self.assertRaisesRegex(RuntimeError, 'bad signature'):
                    packages.resolve('chatgpt-bin', cache, SEED)
            self.assertFalse((cache / 'chatgpt-bin-v1.json').exists())

    def test_every_selected_local_package_has_a_portable_source(self):
        from apx_environment_features import local_packages_for
        supported = set(packages.upstream.REPOSITORIES) | {'chatgpt-bin','salvador-de-mundos-apx','nvidia-utils'}
        for modules in (*PRESETS.values(), tuple(OPTIONAL_MODULES)):
            self.assertLessEqual(set(local_packages_for(modules)), supported)


class PrivateProvisionTests(unittest.TestCase):
    def runtime(self, nvidia='', failure=None):
        calls=[]
        def run(command, **kwargs):
            calls.append(command)
            if failure and '/usr/bin/pacman' in command: raise RuntimeError(failure)
            return SimpleNamespace(stdout='inactive' if command[:2]==['systemctl','is-active'] else 'running')
        return SimpleNamespace(run=run, NETWORK_ADAPTER='/usr/lib/apx/apx-environment-network-v1.py',
            LOCAL_PACKAGE_ARTIFACTS=Path('/var/lib/apx/package-artifacts'),
            Refusal=RuntimeError, host_nvidia_version=lambda:nvidia), calls

    def test_packages_execute_only_inside_named_private_machine(self):
        runtime,calls=self.runtime()
        provision.install(runtime, Path('/fixture/work/root'), ('thunar',), (Path('brave.pkg.tar.zst'),))
        boot=next(c for c in calls if 'systemd-nspawn' in c)
        for flag in ('--private-users=pick','--network-veth','--private-network','--settings=no'):
            self.assertIn(flag,boot)
        self.assertIn('--bind-ro=/var/lib/apx/package-artifacts:/run/apx-packages:idmap',boot)
        transactions=[c for c in calls if '/usr/bin/pacman' in c]
        self.assertEqual(len(transactions),2)
        for c in transactions:
            self.assertIn('-M',c)
            self.assertNotIn('--root',c)
        self.assertNotIn('--ignore',transactions[0])
        self.assertEqual(calls[-1][1], 'remove')

    def test_failure_stops_machine_and_removes_network(self):
        runtime,calls=self.runtime(failure='transaction failed')
        with self.assertRaisesRegex(RuntimeError,'transaction failed'):
            provision.install(runtime,Path('/fixture/work/root'),('thunar',),())
        self.assertTrue(any(c[:2]==['systemctl','stop'] for c in calls))
        self.assertEqual(calls[-1][1],'remove')

    def test_nvidia_stays_pinned_to_host(self):
        runtime,calls=self.runtime(nvidia='610.43.03')
        provision.install(runtime,Path('/fixture/work/root'),('thunar',),())
        transaction=next(c for c in calls if '/usr/bin/pacman' in c)
        self.assertIn('nvidia-utils,lib32-nvidia-utils,opencl-nvidia',transaction)

    def test_install_refuses_unretired_machine(self):
        runtime,calls=self.runtime()
        original=runtime.run
        def run(c,**kwargs):
            if c[:2]==['systemctl','is-active']:return SimpleNamespace(stdout='active')
            return original(c,**kwargs)
        runtime.run=run
        with self.assertRaisesRegex(RuntimeError,'continua ativo'):
            provision.install(runtime,Path('/fixture/work/root'),(),())
        self.assertFalse(any(c[1:2]==['remove'] for c in calls))


class PortableRuntimeIntegrationTests(unittest.TestCase):
    def test_selected_native_applications_reach_the_private_installer(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            shutil.copyfile(ROOT / 'scripts/virtual-lab/apx-lab-runtime.py', base / 'apx-lab-runtime-core.py')
            shutil.copyfile(ROOT / 'scripts/portable/apx-portable-full-runtime.py', base / 'runtime.py')
            module = load(base / 'runtime.py', 'portable_runtime_integration')
            root = base / 'work/root'; root.mkdir(parents=True)
            modules = list(PRESETS['complete']) + list(OPTIONAL_MODULES)
            with patch.object(module.runtime, 'read_trusted_shadow', return_value='apx:$fixture:1:0:99999:7:::\n'), \
                    patch.object(module.runtime, 'write_trusted_shadow') as password, \
                    patch.object(packages, 'resolve', side_effect=lambda name,directory:base/(name+'.pkg.tar.zst')) as resolve, \
                    patch.object(provision, 'install') as install:
                module.configure_features(root,dict(desktop_preset='complete',desktop_modules=modules))
            selected = {call.args[0] for call in resolve.call_args_list}
            self.assertEqual(selected,{'brave-bin','localsend-bin','gridcraft','wordcraft','deckcraft','chatgpt-bin','salvador-de-mundos-apx'})
            password.assert_called_once()
            self.assertEqual(len(install.call_args.args[3]),7)
            self.assertIn('thunar',install.call_args.args[2])
            self.assertEqual(json.loads((root/'etc/apx/portable-application-policy.json').read_text())['schema'],2)

    def test_user_flatpak_setup_works_without_nvidia(self):
        core = load(ROOT / 'scripts/virtual-lab/apx-lab-runtime.py', 'portable_no_nvidia_apps')
        calls=[]
        def run(command, **kwargs):
            calls.append(command)
            return SimpleNamespace(stdout='inactive' if command[:2]==['systemctl','is-active'] else 'running')
        with tempfile.TemporaryDirectory() as temp, patch.object(core,'run',side_effect=run), \
                patch.object(core,'host_nvidia_version',return_value=''):
            core.install_environment_applications(Path(temp)/'root',Path(temp)/'home/apx',['steam'])
        command=next(c for c in calls if core.APPLICATION_INSTALL_SCRIPT in c)
        self.assertIn('--setenv=FLATPAK_GL_DRIVERS=default',command)
        self.assertFalse(any('nvidia-' in x for x in command if x.startswith('--setenv=')))

    def test_installer_manifest_reports_enabled_features_separately_from_source_files(self):
        module = load(ROOT/'scripts/portable/install_apx_full.py','portable_manifest_test')
        manifest=module.feature_manifest()
        self.assertIn('transfer',manifest['services'])
        self.assertIn('passkeys',manifest['services'])
        self.assertIn('media',manifest['services'])
        self.assertIn('chatgpt-bin',manifest['native_applications'])
        self.assertFalse(manifest['native_windows'])
        self.assertIn('config/portable-packages-v2/SHA256SUMS.json',module.verify_sources())


if __name__ == '__main__':unittest.main()
