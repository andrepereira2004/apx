"""Model checks independent of GTK; never signal a real process."""
import ast
import os
from pathlib import Path
import signal
import unittest
from unittest.mock import Mock, patch

SOURCE = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-task-manager'


def model():
    tree = ast.parse(SOURCE.read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'process', 'snapshot', 'terminate'}]
    scope = {'Path': Path, 'os': Mock(getpid=lambda: os.getpid(), getuid=lambda: os.getuid(), pidfd_open=Mock(return_value=15), close=Mock()), 'signal': Mock(SIGTERM=signal.SIGTERM, pidfd_send_signal=Mock()),
             'TICKS': 100, 'PAGES': 4096, 'ESSENTIAL': {'Hyprland', 'systemd', 'python3'}}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), scope)
    return scope


class TaskManagerTests(unittest.TestCase):
    def test_safe_close_uses_pinned_process_identity(self):
        m = model(); m['os'].pidfd_open.return_value = 15
        m['process'] = Mock(return_value={'start': 123, 'uid': os.getuid(), 'name': 'brave'})
        m['terminate'](777, 123)
        m['signal'].pidfd_send_signal.assert_called_once_with(15, signal.SIGTERM)
        m['os'].close.assert_called_once_with(15)

    def test_recycled_pid_is_not_signalled(self):
        m = model(); m['process'] = Mock(return_value={'start': 124, 'uid': os.getuid(), 'name': 'brave'})
        with self.assertRaises(ValueError): m['terminate'](777, 123)
        m['signal'].pidfd_send_signal.assert_not_called(); m['os'].close.assert_called_once()

    def test_other_user_and_session_services_are_protected(self):
        for uid, name in [(os.getuid() + 1, 'brave'), (os.getuid(), 'Hyprland')]:
            m = model(); m['process'] = Mock(return_value={'start': 123, 'uid': uid, 'name': name})
            with self.assertRaises(ValueError): m['terminate'](777, 123)
            m['signal'].pidfd_send_signal.assert_not_called()

    def test_self_and_pid_one_are_protected(self):
        for pid in [1, os.getpid()]:
            m = model()
            with self.assertRaises(ValueError): m['terminate'](pid, 123)
            m['os'].pidfd_open.assert_not_called()

    def test_stat_parsing_handles_spaces_and_parentheses_in_names(self):
        m = model(); root = Mock()
        fields = ['0'] * 22
        fields[0], fields[1], fields[11], fields[12], fields[19], fields[21] = 'S', '8', '10', '20', '12345', '4'
        def path(name):
            item = Mock(); item.read_text.return_value = ('77 (a process (worker)) ' + ' '.join(fields)) if name == 'stat' else 'a process (worker)\n'
            return item
        root.joinpath.side_effect = path; root.stat.return_value.st_uid = os.getuid()
        m['Path'] = Mock(return_value=Mock()); m['Path'].return_value.__truediv__ = Mock(return_value=root)
        p = m['process'](77)
        self.assertEqual((p['pid'], p['parent'], p['ticks'], p['start'], p['rss']), (77, 8, 30, 12345, 16384))


if __name__ == '__main__': unittest.main()
