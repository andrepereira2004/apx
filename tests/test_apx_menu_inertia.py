from pathlib import Path
import shutil
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml'
class MenuInertiaTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_continuous_retargeting_clamping_and_stop(self):
        s=SOURCE.read_text();functions=s[s.index('                function stopWheel()'):s.index('                onEnabledChanged:',s.index('                function stopWheel()'))]
        script='''const assert=require('node:assert/strict');
let contentY=300,contentHeight=1000,height=300,wheelPosition=0,wheelDestination=0,wheelAnimating=false;
function cancelFlick(){}
const menuWheelAnimation={running:false,stop(){this.running=false}};
'''+functions+'''
scrollWheel(-10);assert.equal(wheelDestination,325);assert.equal(wheelPosition,325);
menuWheelAnimation.running=true;
scrollWheel(-10);assert.equal(wheelDestination,350);
scrollWheel(10);assert.equal(wheelDestination,325);
scrollWheel(-10000);assert.equal(wheelDestination,700);
scrollWheel(10000);assert.equal(wheelDestination,0);
stopWheel();assert.equal(menuWheelAnimation.running,false);assert.equal(wheelAnimating,false);
contentY=200;scrollWheel(-10);assert.equal(wheelDestination,225);
'''
        result=subprocess.run(['node','-e',script],capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)
    def test_only_trackpad_adjustment_remains(self):
        self.assertNotIn('menuScrollSensitivity',SOURCE.read_text());self.assertIn('id: trackpadSensitivitySlider',SOURCE.read_text())
