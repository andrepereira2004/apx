from pathlib import Path
import unittest
import importlib.util
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


class CoordinatedUpdatePhysicalTests(unittest.TestCase):
    def test_requires_preview_digest_and_literal_confirmation(self):
        source = (ROOT / "scripts/physical-pilot/apx-coordinated-update-v1.py").read_text()
        self.assertIn('"confirmation": "CONFIRMAR"', source)
        self.assertIn('current["plan_digest"]', source)
        self.assertIn("authorize_official_hub_peer", source)
        self.assertIn("os.chmod(base, 0o711)", source)
        self.assertIn("os.chmod(operations, 0o711)", source)
        self.assertIn("directory.mkdir(mode=0o711)", source)

    def test_runner_stages_before_snapshots_and_stops_on_failure(self):
        source = (ROOT / "scripts/physical-pilot/apx-coordinated-update-runner-v1.py").read_text()
        self.assertLess(source.index("prepare_repository(directory)"), source.index("snapshots(directory, names)"))
        self.assertIn('"state": "failed"', source)
        self.assertIn('"-r", str(source_path)', source)
        self.assertIn("os.chmod(database, 0o711)", source)
        self.assertNotIn("rollback", source[source.index("except Exception as error:"):])

    def test_hub_return_is_detached_and_delayed(self):
        spec = importlib.util.spec_from_file_location('update_runner', ROOT / 'scripts/physical-pilot/apx-coordinated-update-runner-v1.py')
        runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
        with patch.object(runner, 'run') as run:
            runner.schedule_hub_return('20261112T100000Z-123456789abc')
        command = run.call_args.args[0]
        self.assertIn('--on-active=5s', command)
        self.assertIn('--property=Restart=on-failure', command)
        self.assertEqual(command[-2:], ('/var/lib/apx/official-hub-v1/apx-official-hub-graphical-v1.py', '--interactive'))
