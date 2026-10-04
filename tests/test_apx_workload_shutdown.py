import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
class WorkloadShutdownTests(unittest.TestCase):
 def test_recovery_is_generation_bound(self):
  spec=importlib.util.spec_from_file_location('shutdown_runner',ROOT/'scripts/physical-pilot/apx-system-power-runner-v1.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);active=root/'run/apx/active-graphical-environment-v1.json';active.parent.mkdir(parents=True)
   reg=root/'var/lib/apx/environments/codex-test-power/registration.json';reg.parent.mkdir(parents=True)
   a={'name':'codex-test-power','role':'graphical-base','generation':'12345678-1234-1234-1234-123456789012','unit':'apx-graphical-codex-test-power-12345678.service'}
   active.write_text(json.dumps(a));reg.write_text(json.dumps(dict(role='graphical-base',generation='stale')))
   with patch.object(d,'Path',side_effect=lambda p:root/str(p).lstrip('/')),patch.object(d,'run') as run:
    with self.assertRaises(RuntimeError):d.recover_active_workload()
    run.assert_not_called()
    reg.write_text(json.dumps(dict(role='graphical-base',generation=a['generation'])))
    d.recover_active_workload()
    run.assert_called_once_with(('/usr/lib/apx/apx-graphical-environment-v1.py','--environment','codex-test-power','--recover'))
