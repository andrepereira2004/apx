import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("rollback_runtime", Path(__file__).resolve().parents[1] / "scripts/virtual-lab/apx-lab-runtime.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class RollbackPurgeTests(unittest.TestCase):
    def test_numbered_configuration_backups_are_removed_by_exact_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary); backup = state / "backups/deployment"; backup.mkdir(parents=True)
            for identity in ("0", "1"): (backup / identity).write_text("saved settings")
            entries = [{"target": str(state / "environments/school/home/apx/.config/settings"), "backup": str(backup / "0")},
                       {"target": str(state / "environments/school-extra/home/apx/.config/settings"), "backup": str(backup / "1")}]
            (backup / "manifest.json").write_text(json.dumps(entries))
            with patch.object(runtime, "BACKUPS", state / "backups"), patch.object(runtime, "ENVIRONMENTS", state / "environments"):
                self.assertEqual(runtime.purge_environment_backups("school"), 1)
            self.assertFalse((backup / "0").exists()); self.assertTrue((backup / "1").exists())
            self.assertEqual(json.loads((backup / "manifest.json").read_text()), entries[1:])

    def fixture(self, state, coordinated=False, status="complete"):
        op = "20261004T100000Z-0123456789ab"
        base = state / ("coordinated-updates-v1" if coordinated else "environment-updates-v1")
        directory = base / "operations" / op if coordinated else base / op
        directory.mkdir(parents=True)
        target = {"name": "school", "generation": "old-generation", "kind": "environment"}
        (directory / ("approved-plan.json" if coordinated else "plan.json")).write_text(json.dumps({"targets": [target]}))
        (directory / "status.json").write_text(json.dumps({"state": status}))
        rollback = base / "rollbacks" / op if coordinated else directory / "rollback"
        rollback.mkdir(parents=True)
        for name in ("school-root", "school-home", "school-extra-root", "host-root"):
            (rollback / name).mkdir()
        return rollback

    def test_exact_snapshots_in_both_layouts_leave_neighbors_out(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary)
            one = self.fixture(state)
            two = self.fixture(state, coordinated=True)
            with patch.object(runtime, "STATE", state):
                paths = runtime.environment_update_rollbacks("school")
            self.assertEqual(set(paths), {one / "school-root", one / "school-home", two / "school-root", two / "school-home"})

    def test_running_operation_refuses_and_keeps_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary); rollback = self.fixture(state, status="running")
            with patch.object(runtime, "STATE", state), self.assertRaises(runtime.Refusal):
                runtime.environment_update_rollbacks("school")
            self.assertTrue((rollback / "school-root").exists())

    def test_symlink_snapshot_refuses_without_following_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary); rollback = self.fixture(state)
            (rollback / "school-root").rmdir()
            (rollback / "school-root").symlink_to(rollback / "host-root")
            with patch.object(runtime, "STATE", state), self.assertRaises(runtime.Refusal):
                runtime.environment_update_rollbacks("school")
            self.assertTrue((rollback / "host-root").is_dir())

    def test_missing_plan_identity_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary); rollback = self.fixture(state)
            (rollback.parent / "plan.json").write_text('{"targets": [{"name": "other"}]}')
            with patch.object(runtime, "STATE", state), self.assertRaises(runtime.Refusal):
                runtime.environment_update_rollbacks("school")
