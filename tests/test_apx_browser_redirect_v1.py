import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch, Mock

SCRIPT = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-browser-redirect-v1'


def load():
    loader = SourceFileLoader('browser_redirect', str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class BrowserRedirectTests(unittest.TestCase):
    def test_auth_url_is_one_argument_and_secrets_are_absent_from_notification(self):
        m = load()
        url = 'https://login.example.org/oauth?code=private&state=a;b#secret'
        data = {'name': 'Brave', 'exec': '/usr/bin/brave %U', 'startupwmclass': 'brave-browser'}
        command = m.browser_command(data, url)
        self.assertEqual(command, ['/usr/bin/brave', '--new-window', url])
        notice = m.notification_command('Minecraft <Launcher>', 'Brave', url)
        self.assertIn('--expire-time=5000', notice)
        self.assertIn('--action=default=Ir para a página', notice)
        self.assertIn('Minecraft &lt;Launcher&gt; → Brave', notice[-1])
        self.assertIn('login.example.org', notice[-1])
        self.assertNotIn('private', notice[-1])
        self.assertNotIn('secret', notice[-1])

    def test_invalid_urls_and_recursive_handler_are_rejected(self):
        m = load()
        for url in ('file:///etc/passwd', 'javascript:alert(1)', 'https://', 'https://example.org/\n'):
            with self.assertRaises(ValueError):
                m.browser_command({'exec': 'brave %U'}, url)
        with self.assertRaises(ValueError):
            m.desktop(m.HANDLER)

    def test_window_target_is_new_matching_browser_and_ambiguous_targets_are_rejected(self):
        m = load()
        data = {'name': 'Brave', 'startupwmclass': 'brave-browser'}
        old = {'address': '0x1', 'class': 'brave-browser'}
        new = {'address': '0x2', 'class': 'brave-browser'}
        other = {'address': '0x3', 'class': 'kitty'}
        self.assertEqual(m.new_window([old], [old, new, other], data), new)
        self.assertIsNone(m.new_window([old], [old, other], data))
        self.assertIsNone(m.new_window([old], [old, new, dict(new, address='0x4')], data))

    def test_click_focuses_exact_window_with_workspace_capable_dispatch(self):
        m = load()
        result = subprocess.CompletedProcess([], 0, 'ok', '')
        with patch.object(m, 'windows', return_value=[{'address': '0xabc'}]), \
             patch.object(m.subprocess, 'run', return_value=result) as run:
            self.assertTrue(m.focus_window('0xabc'))
            self.assertIn('hl.dsp.focus', run.call_args.args[0][-1])
            self.assertIn('address:0xabc', run.call_args.args[0][-1])
        with patch.object(m, 'windows', return_value=[]), patch.object(m.subprocess, 'run') as run:
            self.assertFalse(m.focus_window('0xabc'))
            run.assert_not_called()

    def test_browser_change_retains_handoff_and_real_browser_preference(self):
        m = load()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'prefs.json'
            with patch.object(m, 'PREFERENCE', path), patch.object(m, 'desktop', return_value={'exec': 'firefox %u'}), \
                 patch.object(m.subprocess, 'run') as run:
                m.set_browser('firefox.desktop')
                self.assertEqual(m.preferred_browser(), 'firefox.desktop')
                self.assertEqual(json.loads(path.read_text())['desktop'], 'firefox.desktop')
                self.assertEqual(run.call_args_list[1].args[0][-2:], [m.HANDLER, 'x-scheme-handler/http'])
                self.assertEqual(run.call_args_list[2].args[0][-2:], [m.HANDLER, 'x-scheme-handler/https'])

    def test_source_ancestor_window_precedes_current_focused_window(self):
        m = load()
        with patch.object(m.os, 'getppid', return_value=1), \
             patch.object(m, 'application_name', side_effect=lambda s: s), \
             patch.object(m.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '{"class":"Minecraft Launcher"}', '')):
            self.assertEqual(m.request_source([]), 'Minecraft Launcher')

    def test_early_click_shows_feedback_then_focuses_delayed_window_and_dismisses(self):
        m = load()
        browser = Mock()
        browser.poll.return_value = 0
        target = {'address': '0xnew', 'class': 'brave-browser'}
        with patch.object(m, 'waiting_feedback', return_value='42') as feedback, \
             patch.object(m, 'dismiss_feedback') as dismiss, \
             patch.object(m, 'windows', side_effect=[[], [], [target]]), \
             patch.object(m, 'focus_window', return_value=True) as focus, \
             patch.object(m.time, 'sleep'):
            self.assertTrue(m.wait_and_redirect([], {'name': 'Brave'}, browser))
        feedback.assert_called_once_with('Brave')
        focus.assert_called_once_with('0xnew')
        dismiss.assert_called_once_with('42')

    def test_waiting_feedback_is_removed_on_actual_launch_failure_and_timeout(self):
        m = load()
        browser = Mock()
        browser.poll.return_value = 1
        with patch.object(m, 'waiting_feedback', return_value='42'), \
             patch.object(m, 'dismiss_feedback') as dismiss, \
             patch.object(m, 'windows', return_value=[]):
            self.assertFalse(m.wait_and_redirect([], {'name': 'Brave'}, browser))
        dismiss.assert_called_once_with('42')
        with patch.object(m, 'waiting_feedback', return_value='43'), \
             patch.object(m, 'dismiss_feedback') as dismiss, \
             patch.object(m.time, 'monotonic', side_effect=[100, 221]):
            self.assertFalse(m.wait_and_redirect([], {'name': 'Brave'}, browser))
        dismiss.assert_called_once_with('43')

    def test_early_click_is_queued_without_emitting_an_unavailable_window_error(self):
        m = load()
        browser, notification = Mock(), Mock()
        notification.poll.return_value = 0
        notification.communicate.return_value = ('default', '')
        with tempfile.TemporaryDirectory() as directory, \
             patch.dict(m.os.environ, {'XDG_RUNTIME_DIR': directory}), \
             patch.object(m, 'desktop', return_value={'name': 'Brave', 'exec': 'brave %U'}), \
             patch.object(m, 'preferred_browser', return_value='brave-browser.desktop'), \
             patch.object(m, 'request_source', return_value='Thunderbird'), \
             patch.object(m, 'windows', return_value=[]), \
             patch.object(m.subprocess, 'Popen', side_effect=[browser, notification]), \
             patch.object(m.subprocess, 'run') as run, \
             patch.object(m, 'wait_and_redirect', return_value=True) as wait:
            m.open_url('https://login.example.org/')
        wait.assert_called_once_with([], {'name': 'Brave', 'exec': 'brave %U'}, browser)
        run.assert_not_called()

    def test_mako_policy_keeps_click_action_corner_and_timeout(self):
        text = (SCRIPT.parents[2] / 'mako/config').read_text()
        section = text.split('[app-name="APX Browser"]', 1)[1]
        for option in ('anchor=top-right', 'default-timeout=5000', 'ignore-timeout=1',
                       'on-button-left=invoke-default-action', 'history=0'):
            self.assertIn(option, section)
