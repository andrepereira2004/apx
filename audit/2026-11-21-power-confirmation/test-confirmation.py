from pathlib import Path
import subprocess
s=(Path(__file__).resolve().parents[2]/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
def body(start):
 pos=s.index('{',s.index(start));depth=1;i=pos+1
 while depth:
  if s[i]=='{':depth+=1
  if s[i]=='}':depth-=1
  i+=1
 return s[pos+1:i-1]
start=s.index('id: powerPrepareProcess')
# Extract the callback specifically from the preparation Process.
sub=s[start:];p=sub.index('{',sub.index('onStreamFinished:',sub.index('stdout:')));depth=1;i=p+1
while depth:
 if sub[i]=='{':depth+=1
 if sub[i]=='}':depth-=1
 i+=1
callback=sub[p+1:i-1]
js='''const assert = require('node:assert/strict');
let powerBusy=false,powerAction='',powerToken='',powerMessage='',powerConfirmOpen=false,powerTransitionActive=false;
let powerPrepareProcess={running:false},powerConfirmProcess={running:false},lockProcess={running:false},suspendLockDelay={restart(){}};
function beginPower(action){'''+body('function beginPower(action)')+'''}
function confirmPower(){'''+body('function confirmPower()')+'''}
for (const action of ['poweroff','reboot']) {
 powerBusy=false;powerConfirmProcess.running=false;
 beginPower(action);
 assert.equal(powerPrepareProcess.running,true);
 assert.equal(powerTransitionActive,false);
 assert.equal(powerConfirmProcess.running,false);
 const root={powerBusy:true,powerAction:action,powerToken:'',powerMessage:'',powerTransitionActive:false,idleSuspendRequested:false,confirmPower(){throw Error('Unapproved power action')}};
 const text=JSON.stringify({prepared:true,token:'test-token',action});
 (function(){'''+callback+'''})();
 assert.equal(root.powerToken,'test-token');
 assert.equal(root.powerBusy,false);
 assert.equal(root.powerTransitionActive,false);
 powerBusy=false;powerToken=root.powerToken;
 confirmPower();
 assert.equal(powerConfirmProcess.running,true);
 assert.equal(powerTransitionActive,true);
}
console.log('PASS: prepare poweroff/reboot waits for confirmation; explicit confirm starts transition');
'''
r=subprocess.run(['chroot','/var/lib/apx/environments/faculdade/root','/usr/bin/node'],input=js,text=True,capture_output=True)
print(r.stdout,r.stderr);raise SystemExit(r.returncode)
