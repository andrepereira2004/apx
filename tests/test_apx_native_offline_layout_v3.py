from copy import deepcopy
from pathlib import Path
import importlib.util
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from apx_native_instances_v3 import plan_second_windows
from test_apx_native_instances_v3 import fixture

SPEC = importlib.util.spec_from_file_location('offline_layout', ROOT / 'scripts/physical-pilot/apx-native-offline-layout-v3.py')
offline_layout = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(offline_layout)


class OfflineLayoutTests(unittest.TestCase):
    def test_each_action_requires_its_own_starting_layout(self):
        table, legacy, args = fixture()
        plan = plan_second_windows(table, legacy, **args)
        self.assertTrue(offline_layout.validate(deepcopy(plan['before']), plan, 'relocate'))
        self.assertTrue(offline_layout.validate(deepcopy(plan['after']), plan, 'rollback'))
        self.assertTrue(offline_layout.validate(deepcopy(plan['after']), plan, 'relocate', 'result'))
        self.assertTrue(offline_layout.validate(deepcopy(plan['before']), plan, 'rollback', 'result'))
        with self.assertRaisesRegex(ValueError, 'starting layout'):
            offline_layout.validate(plan['after'], plan, 'relocate')
        with self.assertRaisesRegex(ValueError, 'starting layout'):
            offline_layout.validate(plan['before'], plan, 'rollback')
        with self.assertRaisesRegex(ValueError, 'result layout'):
            offline_layout.validate(plan['before'], plan, 'relocate', 'result')
        with self.assertRaisesRegex(ValueError, 'result layout'):
            offline_layout.validate(plan['after'], plan, 'rollback', 'result')
