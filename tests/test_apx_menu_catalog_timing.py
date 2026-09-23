"""Execute the actual QML catalogue handlers against cold/open/changed states."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()

def function(name):
    start = SOURCE.index('    function '+name+'(')
    end = SOURCE.index('\n    function ', start+1)
    return SOURCE[start:end]

@unittest.skipUnless(shutil.which('node'), 'Node is required for executable QML JS checks')
class MenuCatalogTimingTests(unittest.TestCase):
    def test_unchanged_refresh_preserves_delegates_and_focus(self):
        self.run_js('''const original = root.environmentCatalog;
            applyEnvironmentCatalog([{name:'hytale', generation:'one'}]);
            assert.strictEqual(root.environmentCatalog, original);
            assert.equal(resets, 0);''')

    def test_changed_catalog_clears_missing_selection(self):
        self.run_js('''applyEnvironmentCatalog([{name:'steam', generation:'two'}]);
            assert.equal(root.selectedEnvironmentName, '');
            assert.equal(root.selectedEnvironmentGeneration, '');
            assert.equal(resets, 1);''')

    def test_deferred_catalog_applies_once_and_clears_pending(self):
        self.run_js('''root.pendingEnvironmentCatalog = [{name:'steam'}];
            flushEnvironmentCatalog(); flushEnvironmentCatalog();
            assert.equal(root.environmentCatalog[0].name, 'steam');
            assert.equal(root.pendingEnvironmentCatalog, null);
            assert.equal(resets, 1);''')

    def test_workload_prefetch_never_calls_hub_endpoints(self):
        self.run_js('''root.isHub = false; refreshEnvironmentMenu();
            assert.equal(environmentCatalogProcess.running, false);
            assert.equal(environmentStorageProcess.running, false);
            assert.equal(environmentManagementStatusProcess.running, false);
            root.isHub = true; refreshEnvironmentMenu();
            assert.equal(environmentCatalogProcess.running, true);''')

    def run_js(self, case):
        code = '''const assert = require('node:assert/strict'); let resets = 0;
            const root = {environmentCatalog:[{name:'hytale', generation:'one'}],
                selectedEnvironmentName:'hytale', selectedEnvironmentGeneration:'one',
                pendingEnvironmentCatalog:null,
                resetEnvironmentFocus(){resets++},
                environmentSelection(){return this.environmentCatalog.find(x => x.name === this.selectedEnvironmentName)}};
            const environmentCatalogProcess={running:false}, environmentStorageProcess={running:false}, environmentManagementStatusProcess={running:false};
        ''' + '\n'.join(function(n) for n in ['refreshEnvironmentMenu', 'applyEnvironmentCatalog', 'flushEnvironmentCatalog']) + '''
            root.applyEnvironmentCatalog = applyEnvironmentCatalog;
        ''' + case
        result = subprocess.run(['node', '-e', code], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
