from pathlib import Path
import shutil
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('node'),'Node required for QML JavaScript')
class GhostLinesTests(unittest.TestCase):
    def check(self,code):
        source=(ROOT/'config/environment-shell-v1/quickshell/apx/GhostLines.js').read_text().replace('.pragma library','')
        subprocess.run(['node','-e','const assert=require("node:assert/strict");\n'+source+'\n'+code],check=True,capture_output=True,text=True)
    def test_3000_distinct_local_compositions(self):
        self.check('''assert.equal(count(),3000); const seen=new Set();
for(const key of Object.keys(groups))for(let a=0;a<10;a++)for(let b=0;b<10;b++)seen.add(line(key,a,b).text);
assert.equal(seen.size,3000);''')
    def test_date_hour_environment_and_application_filters(self):
        self.check('''const keys=c=>eligible(c).map(v=>v.key);
const ordinary=keys({now:new Date(2026,2,11,9),environment:'faculdade',apps:['kitty','brave'],count:3});
for(const value of ['morning','faculdade','terminal','browser'])assert(ordinary.includes(value));
for(const value of ['halloween','christmas','video','music'])assert(!ordinary.includes(value));
assert(keys({now:new Date(2026,9,31,23),environment:'minecraft'}).includes('halloween'));
assert(keys({now:new Date(2026,3,25,15)}).includes('freedom_day'));
assert(keys({now:new Date(2026,5,10,15)}).includes('portugal_day'));
assert(keys({now:new Date(2026,11,25,15)}).includes('christmas'));
assert(keys({now:new Date(2026,2,11,15),media:'video'}).includes('video'));''')
    def test_recent_200_messages_do_not_repeat(self):
        self.check('''let seed=103;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
const context={now:new Date(2026,9,16,21),environment:'minecraft',apps:['kitty','brave','thunar'],count:7};
let recent=[];for(let i=0;i<600;i++){const result=pick(context,recent,random);assert(!recent.includes(result.id));assert(result.text.length<300);recent=recent.concat(result.id).slice(-200)}''')
