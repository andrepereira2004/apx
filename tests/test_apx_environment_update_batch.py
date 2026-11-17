import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from apx_environment_update_batch import MINIMUM_UPDATE_FREE_BYTES, build_environment_plan
spec = importlib.util.spec_from_file_location('batch_runner', ROOT / 'scripts/physical-pilot/apx-environment-update-batch-v1.py')
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)


def record(name, **kw):
    value = dict(name=name, generation='11111111-1111-4111-8111-111111111111', role='hub' if name == 'hub' else 'graphical-base',
                 state='running' if name == 'hub' else 'stopped', package_database_ready=True, snapshot_ready=True)
    value.update(kw); return value


class EnvironmentBatchTests(unittest.TestCase):
    def test_wrapped_runtime_uses_canonical_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            library = Path(folder)
            (library / 'apx-lab-runtime.py').write_text('# wrapper without a manifest\n')
            core = library / 'apx-lab-runtime-core.py'
            core.write_text("ENVIRONMENT_SHELL_ASSETS = {'shell.qml': 'digest'}\n")
            self.assertEqual(runner.runtime_assets(library), {'shell.qml': 'digest'})
            core.unlink()
            (library / 'apx-lab-runtime.py').write_text("ENVIRONMENT_SHELL_ASSETS = {'legacy': 'digest'}\n")
            self.assertEqual(runner.runtime_assets(library), {'legacy': 'digest'})

    def test_runtime_manifest_rejects_writable_or_linked_source(self):
        with tempfile.TemporaryDirectory() as folder:
            library = Path(folder)
            core = library / 'apx-lab-runtime-core.py'
            core.write_text('ENVIRONMENT_SHELL_ASSETS = {}\n')
            core.chmod(0o666)
            with self.assertRaises(RuntimeError): runner.runtime_assets(library)
            core.unlink()
            core.symlink_to(ROOT / 'scripts/virtual-lab/apx-lab-runtime.py')
            with self.assertRaises(RuntimeError): runner.runtime_assets(library)

    def test_all_environments_even_legacy_excluded_policy_and_no_host(self):
        plan = build_environment_plan([record('work', update_policy='excluded'), record('hub')], 200 * 1024**3)
        self.assertEqual(plan['classification'], 'ready-for-approval')
        self.assertEqual([t['name'] for t in plan['targets']], ['hub', 'work'])
        self.assertEqual(plan['targets'][0]['execution'], 'local-last')

    def test_running_workload_and_insufficient_update_space_block(self):
        plan = build_environment_plan([record('hub'), record('work', state='running')], 10)
        self.assertIn('environment-state:work', plan['blockers'])
        self.assertIn('update-space-below-16-gib', plan['blockers'])

    def test_update_space_is_independent_of_creation_reserve(self):
        self.assertEqual(MINIMUM_UPDATE_FREE_BYTES, 16 * 1024**3)
        self.assertEqual(build_environment_plan([record('hub')], 76 * 1024**3)['classification'], 'ready-for-approval')
        self.assertIn('update-space-below-16-gib', build_environment_plan([record('hub')], 15 * 1024**3)['blockers'])

    def test_runner_rechecks_space_before_each_mutation(self):
        with patch.object(runner.os, 'statvfs', return_value=SimpleNamespace(f_bavail=15, f_frsize=1024**3)):
            with self.assertRaisesRegex(RuntimeError, '16 GiB'):
                runner.require_update_space()
        with patch.object(runner.os, 'statvfs', return_value=SimpleNamespace(f_bavail=16, f_frsize=1024**3)):
            runner.require_update_space()

    def test_generation_changes_approval_digest(self):
        a = build_environment_plan([record('hub'), record('work')], 200 * 1024**3)
        b = build_environment_plan([record('hub'), record('work', generation='22222222-2222-4222-8222-222222222222')], 200 * 1024**3)
        self.assertNotEqual(a['plan_digest'], b['plan_digest'])

    def test_vm_is_explicitly_blocked_not_silently_omitted(self):
        plan = build_environment_plan([record('hub'), record('windows', virtual_machine=True)], 200 * 1024**3)
        self.assertIn('guest-update-required:windows', plan['blockers'])

    def test_maintenance_has_private_users_network_and_only_scoped_binds(self):
        identity, machine, unit, command = runner.maintenance_command(
            dict(name='work', generation='11111111-1111-4111-8111-111111111111'), Path('/var/lib/apx/environment-updates-v1/test'))
        self.assertLessEqual(len(identity), 8)
        self.assertIn('--private-users=pick', command)
        self.assertIn('--network-veth', command)
        self.assertIn('--settings=no', command)
        self.assertIn('--bind=/var/lib/apx/environments/work/home:/home:idmap', command)
        self.assertEqual(len([arg for arg in command if arg.startswith('--bind')]), 3)
        self.assertFalse(any('host-console' in arg or 'executor.sock' in arg or '/dev/dri' in arg for arg in command))
        self.assertEqual(command[-1], 'systemd.unit=multi-user.target')

    def test_stale_plan_fails_before_snapshots_or_container_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); op = '20260913T100000Z-123456789abc'; (base / op).mkdir()
            with patch.object(runner, 'BASE', base), patch.object(runner, 'TRANSITION_LOCK', base / 'lock'), \
                 patch.object(runner, 'POWER_RESERVATION', base / 'power'), \
                 patch.object(runner, 'read_json', return_value={'plan_digest': 'old'}), \
                 patch.object(runner, 'preview', return_value={'plan_digest': 'new'}), \
                 patch.object(runner.subprocess, 'run') as run:
                with self.assertRaisesRegex(RuntimeError, 'plan changed'): runner.execute(op)
                run.assert_not_called()
                self.assertIn('failed', (base / op / 'status.json').read_text())

    def test_resume_refuses_incomplete_workloads_before_recovering_hub(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); op = '20260913T100000Z-123456789abc'; (base / op).mkdir()
            plan = {'targets': [{'name': 'hub', 'execution': 'local-last'},
                                {'name': 'work', 'execution': 'isolated-maintenance'}]}
            (base / op / 'plan.json').write_text(__import__('json').dumps(plan))
            (base / op / 'status.json').write_text(__import__('json').dumps({
                'state': 'queued-hub', 'completed': [], 'operation': op}))
            with patch.object(runner, 'BASE', base), patch.object(runner.subprocess, 'run') as run:
                with self.assertRaisesRegex(RuntimeError, 'not complete'):
                    runner.execute(op, resume_hub=True, host_digest='a' * 64)
                run.assert_not_called()

    def test_menu_selects_hub_batch_and_workload_local_helper(self):
        source = (ROOT / 'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
        block = source.split('Process { id: updateUiProcess;', 1)[1].split('\n    Process', 1)[0]
        self.assertIn('root.isHub', block)
        self.assertIn('"environments-ui"', block)
        self.assertIn('"/home/apx/.local/bin/apx-environment-update-v1"', block)


class EnvironmentBatchClientTests(unittest.TestCase):
    def client(self):
        spec = importlib.util.spec_from_file_location('batch_client', ROOT / 'scripts/physical-pilot/apx-coordinated-update-client-v1.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def test_failed_workload_never_updates_hub(self):
        client = self.client()
        with patch.object(client, 'exchange', side_effect=[{'state': 'running', 'operation': 'one'}, {'state': 'failed', 'operation': 'one', 'error': 'package failed'}]), \
             patch.object(client.time, 'sleep'), patch.object(client.subprocess, 'run') as run:
            self.assertEqual(client.environments_ui('digest'), 2)
            run.assert_not_called()

    def test_resume_hands_hub_to_detached_worker(self):
        client = self.client()
        with patch.object(client, 'exchange', side_effect=[{'state': 'awaiting-hub', 'operation': 'one'}, {'message': 'accepted'}]) as exchange, \
             patch.object(client.subprocess, 'run') as run:
            self.assertEqual(client.environments_ui(), 0)
            run.assert_not_called()
            self.assertEqual(exchange.call_args.args, ('environments.resume', {'operation': 'one'}))

    def test_resume_error_is_reported_without_local_update(self):
        client = self.client()
        with patch.object(client, 'exchange', side_effect=[{'state': 'awaiting-hub', 'operation': 'one'}, RuntimeError('blocked')]), \
             patch.object(client.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'blocked'): client.environments_ui('digest')
            run.assert_not_called()

    def test_host_endpoint_queues_hub_completion_without_host_update(self):
        spec = importlib.util.spec_from_file_location('update_authority', ROOT / 'scripts/physical-pilot/apx-coordinated-update-v1.py')
        authority = importlib.util.module_from_spec(spec); spec.loader.exec_module(authority)
        current = {'state': 'awaiting-hub', 'operation': '20261112T100000Z-123456789abc'}
        targets = [{'name': 'hub', 'execution': 'local-last'}]
        fake = SimpleNamespace(latest_status=lambda: current, read_json=lambda _: {'targets': targets},
                               preview=lambda: {'targets': targets, 'blockers': []}, BASE=Path('/tmp/apx-test'), atomic=Mock())
        with patch.object(authority, 'environment_batch', return_value=fake), \
             patch.object(authority.subprocess, 'run', return_value=Mock(returncode=0)) as run:
            result = authority.apply_environment_batch('environments.resume', {'operation': current['operation']})
        self.assertTrue(result['accepted'])
        command = run.call_args.args[0]
        self.assertIn('--resume-hub', command)
        self.assertNotIn('--host-digest', command)
        self.assertEqual(fake.atomic.call_args.args[1]['state'], 'queued-hub')
