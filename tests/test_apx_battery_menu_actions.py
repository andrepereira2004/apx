"""Execute hardware operations against temporary files and popup click logic in JS."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SHELL = ROOT / 'config/environment-shell-v1/quickshell/apx/shell.qml'


def load_service():
    spec = importlib.util.spec_from_file_location('battery_power_service', ROOT / 'scripts/physical-pilot/apx-system-power-v1.py')
    module = importlib.util.module_from_spec(spec)
    with patch.object(sys, 'path', [str(ROOT / 'src'), *sys.path]):
        spec.loader.exec_module(module)
    return module


class BatteryActionTests(unittest.TestCase):
    def setUp(self):
        self.service = load_service()
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        self.service.PLATFORM_CHOICES = root / 'choices'
        self.service.PLATFORM_PROFILE = root / 'profile'
        self.service.PLATFORM_CHOICES.write_text('low-power balanced performance\n')
        self.service.PLATFORM_PROFILE.write_text('balanced\n')
        self.service.GPU_BRIDGE = root / 'missing-gpu'

    def test_energy_modes_write_and_verify_without_gpu_or_backlight(self):
        with patch.object(self.service, 'hardware_control_status', side_effect=OSError('no backlight')):
            for profile in ('low-power', 'performance', 'balanced'):
                result = self.service.set_platform_profile(profile)
                self.assertEqual(result['platform_profile'], profile)
                self.assertEqual(self.service.PLATFORM_PROFILE.read_text().strip(), profile)
            status = self.service.hardware_profile_status()
            self.assertEqual(status['platform_profile'], 'balanced')
            self.assertEqual(status['gpu_profiles'], [])
            self.assertIn('gpu_error', status)
            self.assertIn('controls_error', status)
            self.assertNotIn('gpu_profile', status)

    def test_invalid_profile_never_writes(self):
        with self.assertRaises(ValueError):
            self.service.set_platform_profile('turbo')
        self.assertEqual(self.service.PLATFORM_PROFILE.read_text(), 'balanced\n')

    def test_firmware_refusal_is_reported(self):
        real_reader = self.service._read_bounded
        def firmware_ignores_write(path, choices):
            if path == self.service.PLATFORM_PROFILE:
                return 'balanced'
            return real_reader(path, choices)
        with patch.object(self.service, '_read_bounded', side_effect=firmware_ignores_write):
            with self.assertRaisesRegex(RuntimeError, 'did not apply'):
                self.service.set_platform_profile('performance')

    def test_gpu_write_still_requires_bridge(self):
        with self.assertRaises(OSError):
            self.service.set_gpu_profile('nvidia')

    @unittest.skipUnless(shutil.which('node'), 'Node required for QML JavaScript behavior checks')
    def test_popup_click_switches_menu_and_same_button_closes(self):
        source = SHELL.read_text()
        hit_test = source.split('    function popupBarTargetAt', 1)[1].split('    function togglePopup', 1)[0]
        handler = source.split('property var pressedBarTarget: null', 1)[1].split('onClicked: (mouse) => {', 1)[1].split('\n            }', 1)[0]
        js = '''const assert = require('node:assert/strict');
const bar = {screen: 1, implicitHeight: 46, contentItem: {}, margins: {left: 5}};
const popup = {screen: 1};
let current = 'calendar';
function button(kind, x) {return {visible: true, enabled: true, width: 80, height: 32,
mapToItem: () => ({x, y: 7}), activated: () => {current = current === kind ? '' : kind;}};}
const calendarButton = button('calendar', 0), environmentButton = button('environments', 100),
modelStoreButton = button('model', 200), batteryButton = button('battery', 300), controlCenterButton = button('controls', 400);
''' + 'function popupBarTargetAt' + hit_test + '''
const root = {popupBarTargetAt, closePopup: () => {current = '';}};
const Qt = {LeftButton: 1};
let pressedBarTarget = null;
function click(x, y, button = 1) {pressedBarTarget = popupBarTargetAt(x, y); dispatch({x,y,button});}
function dispatch(mouse) {''' + handler + '''}
click(320, 20); assert.equal(current, 'battery');
click(420, 20); assert.equal(current, 'controls');
click(420, 20); assert.equal(current, '');
current = 'calendar'; click(320, 60); assert.equal(current, '');
current = 'calendar'; modelStoreButton.visible = false; click(220, 20); assert.equal(current, '');
current = 'calendar'; click(320, 20, 2); assert.equal(current, '');
current = 'calendar'; pressedBarTarget = calendarButton; dispatch({x:320,y:20,button:1}); assert.equal(current, '');
assert.equal(popupBarTargetAt(304,20), null);
popup.screen = 2; assert.equal(popupBarTargetAt(320,20), null);
'''
        subprocess.run(['node', '-e', js], check=True, capture_output=True, text=True)

    @unittest.skipUnless(shutil.which('node'), 'Node required for QML JavaScript behavior checks')
    def test_first_navigation_key_starts_at_first_control(self):
        source = SHELL.read_text()
        body = source.split('    function navigateGenericMenu(event) {', 1)[1].split('\n    }', 1)[0]
        js = """
const assert = require('node:assert/strict');
const Qt = {Key_Backtab:1, Key_Up:2, Key_Left:3, Key_Tab:4, Key_Down:5, Key_Right:6};
let popupKind = 'battery', menuKeyboardNavigation = false, chosen = -1;
const items = [{activeFocus:false},{activeFocus:false},{activeFocus:false}];
function genericMenuItems() {return items;}
function focusMenuItem(item) {chosen=items.indexOf(item);}
function menuNavigationRect(item) {return {x:0,y:items.indexOf(item)*30,w:100,h:20};}
function spatialMenuIndex(rects,current,key) {return current+1;}
function navigateGenericMenu(event) {""" + body + """}
navigateGenericMenu({key:99}); assert.equal(chosen,-1); assert.equal(menuKeyboardNavigation,false);
navigateGenericMenu({key:Qt.Key_Down}); assert.equal(chosen,0); assert.equal(menuKeyboardNavigation,true);
navigateGenericMenu({key:Qt.Key_Backtab}); assert.equal(chosen,0);
items[0].activeFocus=true; navigateGenericMenu({key:Qt.Key_Down}); assert.equal(chosen,1);
"""
        subprocess.run(['node', '-e', js], check=True, capture_output=True, text=True)
