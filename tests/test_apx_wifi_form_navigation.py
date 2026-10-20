from pathlib import Path
import re
import shutil
import subprocess
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "config/environment-shell-v1/quickshell/apx/shell.qml"


class WifiFormNavigationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is required to exercise QML JavaScript")
    def test_tab_order_pointer_focus_and_cursor_keys(self):
        source = SOURCE.read_text()
        functions = source[source.index("    function genericMenuItems()"):source.index("    Timer {", source.index("    function navigateGenericMenu"))]
        fields = ("wifiUsernameInput", "wifiPasswordInput", "wifiDomainInput", "wifiCaInput")
        flags = []
        for field in fields:
            section = source[source.index("id: " + field):]
            section = section[:section.index("text: root.wifi")]
            flags.append("activeFocusOnTab: true" in section)
        self.assertEqual(flags, [True] * 4)
        script = r'''const assert = require("node:assert/strict");
const Qt = {Key_Tab: 1, Key_Backtab: 2, Key_Up: 3, Key_Down: 4, Key_Left: 5, Key_Right: 6, TabFocusReason: 7};
const controlPageAnimation = {running:false};
const controlPageCapturing = false;
let focusedMenuItem = null, menuKeyboardNavigation = true, popupKind = "controls", isHub = false;
const items = Array.from({length: 7}, (_, i) => ({visible:true, enabled:true, activeFocusOnTab:true, width:100, height:28, activeFocus:false, children:[],
 forceActiveFocus() { items.forEach(x => x.activeFocus = false); this.activeFocus = true; },
 mapToItem() { return {x:0, y:i * 30}; }}));
const [back, wifiUsernameInput, wifiPasswordInput, wifiDomainInput, wifiCaInput, submit, cancel] = items;
const menuContent = {visible:true, enabled:true, activeFocusOnTab:false, children:items};
const menuFlick = {stopWheel() {}, contentItem:{}, contentY:0, height:400, contentHeight:400};
const root = {wifiPasswordVisible:true};
''' + functions + r'''
function key(key) { const event = {key, accepted:false}; navigateGenericMenu(event); return event; }
wifiUsernameInput.forceActiveFocus();
for (const expected of [wifiPasswordInput, wifiDomainInput, wifiCaInput, submit]) {
 assert.equal(key(Qt.Key_Tab).accepted, true);
 assert.equal(expected.activeFocus, true);
}
key(Qt.Key_Backtab); assert.equal(wifiCaInput.activeFocus, true);
// A pointer-selected domain is registered, so the focus-recovery timer leaves it alone.
wifiDomainInput.forceActiveFocus();
assert.equal(genericMenuItems().some(item => item.activeFocus), true);
assert.equal(key(Qt.Key_Right).accepted, false);
assert.equal(wifiDomainInput.activeFocus, true);
key(Qt.Key_Tab); assert.equal(wifiCaInput.activeFocus, true);
'''
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node is required to exercise QML JavaScript")
    def test_open_enterprise_focuses_username_and_personal_focuses_password(self):
        source = SOURCE.read_text()
        function = source[source.index("    function beginWifiConnect(name)"):source.index("    function wifiAvailableNetworks()")]
        script = r'''const assert = require("node:assert/strict");
let wifiMessage, wifiSelectedSsid, wifiUsername, wifiDomain, wifiPassword, wifiPasswordVisible;
let enterprise = true, focused = null, queued = null;
const menuFlick = {contentY: 500, stopWheel() {}, cancelFlick() {}};
const Qt = {callLater(fn) { fn(); queued = fn; }};
const wifiUsernameInput = {forceActiveFocus() { focused = "username"; }};
const wifiPasswordInput = {forceActiveFocus() { focused = "password"; }};
const hostState = {network_name:""};
const wifiIsKnown = () => false, wifiIsOpen = () => false;
const root = {get wifiPasswordVisible() { return wifiPasswordVisible; }, get wifiSelectedSsid() { return wifiSelectedSsid; }, wifiIsEnterprise() { return enterprise; }};
''' + function + r'''
beginWifiConnect("eduroam"); queued(); assert.equal(focused, "username"); assert.equal(menuFlick.contentY, 0);
enterprise = false; beginWifiConnect("personal"); queued(); assert.equal(focused, "password");
beginWifiConnect("eduroam"); focused = null; wifiPasswordVisible = false; queued(); assert.equal(focused, null);
'''
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node is required to exercise QML JavaScript")
    def test_uporto_profile_keeps_other_institutions_and_custom_ca(self):
        source = SOURCE.read_text()
        function = source[source.index("    function submitWifiPassword()"):source.index("    function toggleWifiConnection()")]
        script = r'''const assert = require("node:assert/strict");
let wifiSelectedSsid = "eduroam", wifiUsername = "up123@fe.up.pt", wifiDomain = "up.pt";
let wifiPassword = "dummy", wifiCaCert = "/etc/ssl/certs/ca-certificates.crt", wifiMessage;
const wifiIsKnown = () => false, wifiIsOpen = () => false, wifiIsEnterprise = () => true;
const wifiCredentialProcess = {running:false};
const hostActionProcess = {running:false};
''' + function + r'''
submitWifiPassword();
assert.equal(wifiDomain, "*.up.pt"); assert.equal(wifiCaCert, "/etc/ssl/certs/apx-uporto-eduroam.pem");
assert.equal(wifiCredentialProcess.running, true);
wifiCredentialProcess.running = false;
wifiUsername = "someone@other.edu"; wifiDomain = "other.edu"; wifiCaCert = "/etc/ssl/certs/custom.pem";
submitWifiPassword(); assert.equal(wifiDomain, "other.edu"); assert.equal(wifiCaCert, "/etc/ssl/certs/custom.pem");
wifiCredentialProcess.running = false;
wifiUsername = "up123@fe.up.pt"; wifiDomain = "up.pt";
submitWifiPassword(); assert.equal(wifiCaCert, "/etc/ssl/certs/custom.pem");
'''
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node required")
    def test_complete_connection_removes_active_duplicate_and_clears_secrets(self):
        source = SOURCE.read_text()
        functions = source[source.index('    function wifiAvailableNetworks()'):source.index('    function submitWifiPassword()')]
        script = '''const assert=require('node:assert/strict');
let hostState={network_name:'old',available_networks:['old','new','new','other']};
let wifiSelectedSsid='new',wifiPassword='fictional',wifiUsername='test',wifiDomain='example.org';
let wifiPasswordVisible=true,wifiShowPassword=true,wifiMessage='A ligar';
'''+functions+'''
assert.deepEqual(wifiAvailableNetworks(),['new','other']);
completeWifiConnection();
assert.equal(hostState.network_name,'new');
assert.deepEqual(wifiAvailableNetworks(),['old','other']);
assert.equal(wifiPassword,'');assert.equal(wifiUsername,'');assert.equal(wifiDomain,'');
assert.equal(wifiShowPassword,false);assert.equal(wifiPasswordVisible,false);assert.equal(wifiMessage,'');
'''
        result=subprocess.run(['node','-e',script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node required")
    def test_brightness_icon_restores_previous_level_and_respects_busy_state(self):
        source = SOURCE.read_text()
        function=source[source.index('    function toggleDisplayDim()'):source.index('    function stepDisplayBrightness(')]
        script='''const assert=require('node:assert/strict');
let displayBrightness=62,displayBrightnessBeforeDim=70;
const displayBrightnessProcess={running:false},commits=[];
function commitDisplayBrightness(value){commits.push(value);displayBrightness=value}
'''+function+'''
toggleDisplayDim();assert.equal(displayBrightness,5);assert.equal(displayBrightnessBeforeDim,62);
toggleDisplayDim();assert.equal(displayBrightness,62);
displayBrightnessProcess.running=true;toggleDisplayDim();assert.deepEqual(commits,[5,62]);
'''
        result=subprocess.run(['node','-e',script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
