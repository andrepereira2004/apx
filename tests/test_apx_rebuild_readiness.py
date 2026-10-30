import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "rebuild_audit", ROOT / "scripts/portable/audit-rebuild-readiness.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class RebuildReadinessTests(unittest.TestCase):
    def test_reserve_is_not_bypassed_by_sparse_vm_capacity(self):
        result = audit.storage_check(25 * audit.GIB)
        self.assertFalse(result["ready"])
        self.assertEqual(result["protected_reserve_bytes"], 96 * audit.GIB)
        self.assertEqual(result["shortfall_bytes"], 103 * audit.GIB)
        self.assertTrue(audit.storage_check(128 * audit.GIB)["ready"])

    def test_reserve_reading_never_executes_module_code(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime.py"
            path.write_text("raise RuntimeError('must not execute')\nHOST_STORAGE_RESERVE_BYTES = 96 * 1024**3\n")
            self.assertEqual(audit.runtime_reserve(path), 96 * audit.GIB)
            path.write_text("HOST_STORAGE_RESERVE_BYTES = dangerous_call()\n")
            with self.assertRaises(ValueError):
                audit.runtime_reserve(path)

    def test_hash_match_does_not_promote_differing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "service.py"
            path.write_text("installed")
            index = {path.name: [{"source": "scripts/service.py", "sha256": "0" * 64}]}
            result = audit.compare_file(path, index)
            self.assertEqual(result["status"], "differs")
            self.assertEqual(result["matching_sources"], [])
            self.assertEqual(path.read_text(), "installed")

    def test_library_omits_symlinks_backups_and_private_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "service.py").write_text("source")
            (root / "service.py.before-old").write_text("old source")
            (root / "token.json").write_text("must not export")
            (root / "linked.py").symlink_to(root / "token.json")
            rows = audit.inventory_library(root, {})
            self.assertEqual([Path(row["installed"]).name for row in rows], ["service.py"])

    def test_service_report_omits_environment_and_command_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "apx-example.service").write_text(
                "[Service]\nEnvironment=SECRET=hidden\nExecStart=/usr/bin/python --token hidden\n")
            report = audit.service_inventory(root, {})
            self.assertEqual(report[0]["executables"], [{"path": "/usr/bin/python"}])
            self.assertNotIn("hidden", str(report))

    def test_seed_mismatch_and_missing_source_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed = root / "installed"
            seed.mkdir()
            (seed / "only-installed.qml").write_text("installed")
            rows = audit.seed_coverage(root, seed, {"only-installed.qml": "0" * 64})
            self.assertFalse(rows[0]["source_is_pinned"])
            self.assertFalse(rows[0]["seed_matches_source"])


if __name__ == "__main__":
    unittest.main()
