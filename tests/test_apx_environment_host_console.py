import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from apx_host_services_peer import HostServicesPeer,ActiveEnvironmentPeer

class EnvironmentConsoleTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('environment_console',ROOT/'scripts/physical-pilot/apx-environment-host-console-v1.py')
        self.daemon=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.daemon)
        self.peer=HostServicesPeer(200,1001000,1001000)
        self.identity=ActiveEnvironmentPeer('hytale','graphical-base','generation-a')

    def test_ticket_single_use_and_generation_bound(self):
        d=self.daemon
        with patch.object(d,'authorize',return_value=self.identity),patch.object(d,'ancestry'):
            token=d.issue_ticket(self.peer);d.consume_ticket(token,self.peer)
            with self.assertRaises(PermissionError):d.consume_ticket(token,self.peer)
            token=d.issue_ticket(self.peer)
        with patch.object(d,'authorize',return_value=ActiveEnvironmentPeer('hytale','graphical-base','generation-b')):
            with self.assertRaises(PermissionError):d.consume_ticket(token,self.peer)

    def test_ticket_wrong_uid_and_expiry(self):
        d=self.daemon
        with patch.object(d,'authorize',return_value=self.identity),patch.object(d,'ancestry'):
            token=d.issue_ticket(self.peer)
            with self.assertRaises(PermissionError):d.consume_ticket(token,HostServicesPeer(201,1001001,1001001))
            token=d.issue_ticket(self.peer)
            with patch.object(d.time,'monotonic',return_value=1e20):
                with self.assertRaises(PermissionError):d.consume_ticket(token,self.peer)

    def test_hub_and_inactive_session_rejected(self):
        d=self.daemon
        with patch.object(d,'authorize_active_environment_peer',return_value=ActiveEnvironmentPeer('hub','hub','g')):
            with self.assertRaises(PermissionError):d.authorize(self.peer)
        with patch.object(d,'authorize_active_environment_peer',side_effect=RuntimeError('stopped')):
            with self.assertRaises(RuntimeError):d.authorize(self.peer)

    def test_ancestry_requires_same_service_and_executable(self):
        d=self.daemon
        with tempfile.TemporaryDirectory() as directory:
            proc=Path(directory)
            for pid in (200,123):(proc/str(pid)).mkdir()
            (proc/'200/cgroup').write_text('0::/system.slice/apx-graphical-hytale-abcd.service/user.slice\n')
            (proc/'200/status').write_text('PPid:\t123\n')
            (proc/'123/comm').write_text('quickshell\n')
            (proc/'123/exe').symlink_to('/usr/bin/quickshell')
            path=proc/'123/cgroup';path.write_text('0::/system.slice/apx-graphical-hytale-abcd.service/user.slice\n')
            self.assertEqual(d.ancestry(self.peer,proc),123)
            path.write_text('0::/system.slice/apx-graphical-hytale-abcd.service-evil/user.slice\n')
            with self.assertRaises(PermissionError):d.ancestry(self.peer,proc)

    def test_bridge_closes_root_pty_after_active_session_changes(self):
        d=self.daemon
        from unittest.mock import Mock
        session=Mock();session.condition=__import__('threading').Condition();session.alive=True;session.output=b''
        with patch.object(d,'authorize',side_effect=[self.identity,PermissionError('inactive')]),patch.object(d.base,'RootConsole',return_value=session),patch.object(d.base,'response'),patch.object(d.time,'monotonic',side_effect=[0,1]):
            with self.assertRaises(PermissionError):d.bridge(Mock(),self.peer,24,80)
        session.terminate.assert_called_once()

if __name__=='__main__':unittest.main()
