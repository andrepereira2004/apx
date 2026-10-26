from pathlib import Path
import importlib.util
import subprocess
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('coherence',ROOT/'config/environment-package-install-v1/apx-package-coherence-v1.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class CoherenceTests(unittest.TestCase):
    def test_partial_qt_install_is_blocked(self):
        self.assertEqual(m.check_transaction(['python-pyqt6','zapzap'],['qt6-base','qt6-wayland']),['qt6-base','qt6-wayland'])
    def test_complete_upgrade_is_allowed(self):
        self.assertEqual(m.check_transaction(['python-pyqt6','zapzap','qt6-base'],['qt6-base']),[])
    def test_current_system_local_install_is_allowed(self):
        self.assertEqual(m.check_transaction(['zapzap'],[]),[])
    def test_host_gpu_hold_is_retained(self):
        self.assertEqual(m.check_transaction(['qt6-base'],['qt6-base','nvidia-utils','lib32-nvidia-utils','opencl-nvidia']),[])
    def test_unknown_failure_is_not_treated_as_up_to_date(self):
        with patch.object(m.os,'geteuid',return_value=0),patch.object(m.Path,'read_text',return_value='systemd-nspawn'),patch.object(m.sys,'stdin') as stdin,patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','database unreadable')):
            stdin.read.return_value='zapzap\n'
            with self.assertRaisesRegex(RuntimeError,'verificar'):
                m.main()
