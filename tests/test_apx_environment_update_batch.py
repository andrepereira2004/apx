import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from apx_environment_update_batch import build_environment_plan
spec = importlib.util.spec_from_file_location('batch_runner', ROOT / 'scripts/physical-pilot/apx-environment-update-batch-v1.py')
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)


def record(name, **kw):
    value = dict(name=name, generation='11111111-1111-4111-8111-111111111111', role='hub' if name == 'hub' else 'graphical-base',
                 state='running' if name == 'hub' else 'stopped', package_database_ready=True, snapshot_ready=True)
    value.update(kw); return value


class EnvironmentBatchTests(unittest.TestCase):
    def test_all_environments_even_legacy_excluded_policy_and_no_host(self):
        plan = build_environment_plan([record('work', update_policy='excluded'), record('hub')], 200 * 1024**3)
        self.assertEqual(plan['classification'], 'ready-for-approval')
        self.assertEqual([t['name'] for t in plan['targets']], ['hub', 'work'])
        self.assertEqual(plan['targets'][0]['execution'], 'local-last')

    def test_running_workload_and_insufficient_reserve_block(self):
        plan = build_environment_plan([record('hub'), record('work', state='running')], 10)
        self.assertIn('environment-state:work', plan['blockers'])
        self.assertIn('host-reserve-unavailable', plan['blockers'])

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
            self.assertEqual(client.environments_ui(), 2)
            run.assert_not_called()

    def test_resume_finishes_hub_only_after_workloads_completed(self):
        client = self.client()
        with patch.object(client, 'exchange', side_effect=[{'state': 'awaiting-hub', 'operation': 'one'}, {'message': 'complete'}]) as exchange, \
             patch.object(client.subprocess, 'run', return_value=Mock(returncode=0)) as run:
            self.assertEqual(client.environments_ui(), 0)
            run.assert_called_once_with(['/home/apx/.local/bin/apx-environment-update-v1'])
            self.assertEqual(exchange.call_args.args, ('environments.finish', {'operation': 'one'}))

    def test_failed_hub_never_reports_batch_complete(self):
        client = self.client()
        with patch.object(client, 'exchange', return_value={'state': 'awaiting-hub', 'operation': 'one'}) as exchange, \
             patch.object(client.subprocess, 'run', return_value=Mock(returncode=1)):
            self.assertEqual(client.environments_ui(), 1)
            self.assertEqual(exchange.call_count, 1)
