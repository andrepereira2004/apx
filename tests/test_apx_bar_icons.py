"""Exercise state-driven bar icons and overflow paging without a compositor."""
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
QML = ROOT / 'config/environment-shell-v1/quickshell/apx'


@unittest.skipUnless(shutil.which('node'), 'Node is required for QML JavaScript checks')
class BarIconTests(unittest.TestCase):
    def expression(self, name):
        source = (QML / 'shell.qml').read_text()
        return re.search(r'readonly property string ' + name + r': \{(.*?)\n    \}', source, re.S)[1]

    def javascript(self, source):
        subprocess.run(['node', '-e', 'const assert = require("node:assert/strict");\n' + source],
                       check=True, capture_output=True, text=True)

    def test_battery_states_and_charging_override(self):
        self.javascript('function icon(batteryText, batteryStatus) {' + self.expression('batteryIconName') + '''}
for (const [text, status, expected] of [
    ['--', 'Desconhecido', 'battery'],
    ['100%', 'Carga completa', 'battery-full'],
    ['80%', 'A utilizar bateria', 'battery-full'],
    ['50%', 'A utilizar bateria', 'battery-medium'],
    ['20%', 'A utilizar bateria', 'battery-low'],
    ['5%', 'A utilizar bateria', 'battery-warning'],
    ['5%', 'A carregar', 'battery-charging'],
    ['98%', 'A carregar', 'battery-charging'],
]) assert.equal(icon(text, status), expected);
''')

    def test_launcher_uses_layout_grid_in_every_environment(self):
        self.javascript('function icon(environmentIdentity) {' + self.expression('appsIconName') + '''}
for (const [name, expected] of [
    ['minecraft', 'layout-grid'], ['faculdade', 'layout-grid'], ['hytale', 'layout-grid'],
    ['steam', 'layout-grid'], ['new-environment', 'layout-grid']
]) assert.equal(icon({name}), expected);
assert.equal(icon({}), 'layout-grid');
''')

    def test_overflow_keeps_five_slots_and_wraps(self):
        source = (QML / 'WorkspacePager.js').read_text().replace('.pragma library', '')
        self.javascript(source + '''
const items = [1,2,3,4,5,6,7];
assert.deepEqual(page(items, 0), [1,2,3,4,5]);
assert.deepEqual(page(items, 6), [7,1,2,3,4]);
assert.equal(nextOffset(items, 6), 0);
assert.equal(nextOffset([1,2,3,4,5], 0), 0);
assert.deepEqual(page([], 0), []);
''')
