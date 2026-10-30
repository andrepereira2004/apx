import json
import shutil
import subprocess
import unittest
from pathlib import Path


GROUPS = Path(__file__).resolve().parents[1] / "config/environment-shell-v1/quickshell/apx/NotificationGroups.js"


class NotificationGroupsTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node.js is unavailable")
    def test_desktop_entry_suffix_does_not_split_same_app(self):
        script = """
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync(process.argv[2],'utf8').replace('.pragma library','');
const context={};vm.createContext(context);vm.runInContext(source,context);
const notes=[
  {app:'Thunderbird',desktop_entry:'org.mozilla.Thunderbird',id:1},
  {app:'Thunderbird',desktop_entry:'org.mozilla.Thunderbird.desktop',id:2}
];
process.stdout.write(JSON.stringify(context.build(notes).map(g=>g.notes.map(n=>n.id))));
"""
        result = subprocess.run(["node", "-", str(GROUPS)], input=script, text=True,
                                capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout), [[1, 2]])


if __name__ == "__main__":
    unittest.main()
