import re
import subprocess
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
class MouseScaleTests(unittest.TestCase):
    def test_ui_percentage_maps_to_existing_raw_range(self):
        source=(ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
        body=re.search(r'function setMouseSensitivity\(value\) \{(.*?)\n    \}',source,re.S)[1]
        script='''const assert=require('node:assert/strict');let mouseSensitivity=0,pendingMouseSensitivity=NaN,mouseSensitivityError='';function flushMouseSensitivity(){};function apply(value){'''+body+'''};
for(const [value,raw] of [[0,-100],[25,-50],[50,0],[75,50],[100,100],[-5,-100],[120,100]]) {apply(value);assert.equal(mouseSensitivity,raw);assert.equal(pendingMouseSensitivity,raw);}
'''
        subprocess.run(['node','-e',script],check=True,capture_output=True,text=True)
        slider=source.split('id: mouseSensitivitySlider',1)[1].split('background: Rectangle',1)[0]
        self.assertIn('from: 0; to: 100;',slider)
        self.assertIn('value: (root.mouseSensitivity + 100) / 2;',slider)
