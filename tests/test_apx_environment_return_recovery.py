import fcntl
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
from test_apx_environment_switch_v1 import load_runner, load_switch_service

GEN = '97014bb7-aa82-41fd-aaff-2833e2e41033'

class ReturnRecoveryTests(unittest.TestCase):
    def test_lock_presence_is_not_supervisor_liveness(self):
        service = load_switch_service()
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / 'lock'
            with mock.patch.object(service, 'LOCK', lock):
                self.assertFalse(service.handoff_is_supervised())
                lock.touch()
                self.assertFalse(service.handoff_is_supervised())
                with lock.open('r+') as owner:
                    fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.assertTrue(service.handoff_is_supervised())

    def test_lock_symlink_is_rejected(self):
        service = load_switch_service()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'target').touch()
            (root / 'lock').symlink_to(root / 'target')
            with mock.patch.object(service, 'LOCK', root / 'lock'):
                with self.assertRaises(OSError): service.handoff_is_supervised()

    def test_stale_lock_is_reused_and_live_lock_is_not_replaced(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / 'lock'; lock.touch(); inode = lock.stat().st_ino
            with mock.patch.object(runner, 'LOCK', lock):
                owner = runner.acquire_handoff_lock()
                self.assertEqual(lock.stat().st_ino, inode)
                with self.assertRaises(BlockingIOError): runner.acquire_handoff_lock()
                info = lock.stat()
                runner.release_handoff_lock(owner, info.st_dev, info.st_ino)
                self.assertFalse(lock.exists())

    def test_return_preserves_peer_authorization_and_chooses_correct_supervisor(self):
        service = load_switch_service()
        for name in ('hytale', 'minecraft', 'steam', 'faculdade'):
            for supervised in (False, True):
                with mock.patch.object(service, 'authorize', return_value=name) as auth, \
                     mock.patch.object(service, 'handoff_is_supervised', return_value=supervised), \
                     mock.patch.object(service, 'request_environment_stop', return_value='outer') as stop, \
                     mock.patch.object(service, 'request_recovered_environment_return', return_value='recovery') as recover, \
                     mock.patch.object(service, 'prime_return_screen'):
                    result = service.apply('return.to-hub', {}, 'peer')
                    auth.assert_called_once_with('peer', 'return.to-hub', None)
                    self.assertEqual(result['source'], name)
                    (stop if supervised else recover).assert_called_once_with(name)
                    (recover if supervised else stop).assert_not_called()
        with mock.patch.object(service, 'authorize', side_effect=PermissionError('wrong peer')), \
             mock.patch.object(service, 'request_recovered_environment_return') as recover:
            with self.assertRaises(PermissionError): service.apply('return.to-hub', {}, 'peer')
            recover.assert_not_called()

    def test_failed_supervisor_start_does_not_stop_environment(self):
        service = load_switch_service()
        with mock.patch.object(service, 'trusted_environment', return_value={'state':'running', 'generation':GEN}), \
             mock.patch.object(service.subprocess, 'run', return_value=mock.Mock(returncode=1)) as run, \
             mock.patch.object(service, 'request_environment_stop') as stop:
            with self.assertRaisesRegex(RuntimeError, 'continua aberto'):
                service.request_recovered_environment_return('hytale')
            self.assertIn('--generation', run.call_args.args[0])
            stop.assert_not_called()

    def test_generation_change_is_rejected_before_stopping_session(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as directory:
            active = Path(directory) / 'active'; active.write_text(json.dumps({'generation':'changed'}))
            with mock.patch.object(runner, 'WORKLOAD_ACTIVE', active), \
                 mock.patch.object(runner, 'workload_ready', return_value=True):
                with self.assertRaisesRegex(RuntimeError, 'geração'):
                    runner.validate_return_environment('hytale', GEN)

    def test_recovery_waits_for_cleanup_before_restoring_hub(self):
        runner = load_runner(); events = []
        with tempfile.TemporaryDirectory() as directory, \
             mock.patch.object(runner, 'LOCK', Path(directory) / 'lock'), \
             mock.patch.object(runner, 'validate_return_environment') as validate, \
             mock.patch.object(runner, 'hide_host_getty'), \
             mock.patch.object(runner, 'restore_host_getty'), \
             mock.patch.object(runner, 'transition_screen'), \
             mock.patch.object(runner, 'run', side_effect=lambda args: events.append(args)), \
             mock.patch.object(runner, 'wait_recovered', side_effect=lambda: events.append('clean')), \
             mock.patch.object(runner, 'run_authenticated', side_effect=lambda *a: events.append('hub')), \
             mock.patch.object(sys, 'argv', ['runner','--return-environment','hytale','--generation',GEN]):
            self.assertEqual(runner.main(), 0)
            validate.assert_called_once_with('hytale', GEN)
            self.assertEqual(events, [(runner.GENERAL,'--environment','hytale','--recover'),'clean','hub'])

    def test_invalid_active_identity_never_stops_a_session(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as directory, \
             mock.patch.object(runner, 'LOCK', Path(directory) / 'lock'), \
             mock.patch.object(runner, 'validate_return_environment', side_effect=RuntimeError('changed')), \
             mock.patch.object(runner, 'run') as run, \
             mock.patch.object(runner, 'disarm_failsafe'), \
             mock.patch.object(runner, 'restore_host_getty'), \
             mock.patch.object(sys, 'argv', ['runner','--return-environment','hytale','--generation',GEN]):
            with self.assertRaisesRegex(RuntimeError, 'changed'): runner.main()
            run.assert_not_called()
