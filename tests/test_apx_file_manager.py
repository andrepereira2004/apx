import importlib.machinery
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
LOADER = importlib.machinery.SourceFileLoader('file_actions', str(ROOT/'config/environment-shell-v1/local/bin/apx-laptop-action-v1'))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
ACTIONS = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(ACTIONS)

class FileManagerTests(unittest.TestCase):
    def test_hub_never_launches_files(self):
        with patch.object(Path,'is_socket',return_value=True), patch.object(ACTIONS.subprocess,'run') as run:
            self.assertEqual(ACTIONS.files(),0)
            run.assert_not_called()

    def test_workload_initializes_folders_and_opens_or_focuses(self):
        with patch.object(Path,'is_socket',return_value=False), patch.object(Path,'is_file',return_value=True), patch.object(ACTIONS.shutil,'which',return_value='/usr/bin/xdg-user-dirs-update'), patch.object(ACTIONS.subprocess,'run',return_value=Mock(returncode=0,stdout='ok\n')) as run:
            self.assertEqual(ACTIONS.files(),0)
            self.assertEqual(run.call_args_list[0].args[0],['/usr/bin/xdg-user-dirs-update'])
            code=run.call_args_list[2].args[0][2]
            self.assertIn('hl.dsp.focus',code)
            self.assertIn('/usr/bin/thunar /home/Home',code)
            self.assertIn('USER=apx LOGNAME=apx',code)

    def test_missing_file_manager_reports_failure(self):
        with patch.object(Path,'is_socket',return_value=False), patch.object(Path,'is_file',return_value=False), patch.object(ACTIONS,'feedback') as feedback:
            self.assertEqual(ACTIONS.files(),1)
            feedback.assert_called_once_with('hotkeyFailed')

    def test_compositor_failure_is_reported(self):
        with patch.object(Path,'is_socket',return_value=False), patch.object(Path,'is_file',return_value=True), patch.object(ACTIONS.shutil,'which',return_value=None), patch.object(ACTIONS.subprocess,'run',side_effect=[Mock(returncode=0), OSError()]), patch.object(ACTIONS,'feedback') as feedback:
            self.assertEqual(ACTIONS.files(),1)
            feedback.assert_called_once_with('hotkeyFailed')
