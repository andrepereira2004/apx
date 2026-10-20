from pathlib import Path
import json,os,shutil,subprocess
REPO=Path(__file__).resolve().parents[2]
source=(REPO/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
def block(start):
 begin=source.index(start);level=0
 for pos in range(source.index('{',begin),len(source)):
  if source[pos]=='{':level+=1
  elif source[pos]=='}':
   level-=1
   if level==0:return source[begin:pos+1]
card=block('                        Rectangle {\n                            id: wifiPasswordCard')
button=block('    component MenuButton: Rectangle {')
marker=Path('/run/apx/active-graphical-environment-v1.json');marker=marker if marker.exists() else Path('/run/apx/official-hub-graphical-v1.json')
state=json.loads(marker.read_text());home=Path('/var/lib/apx/environments')/state.get('name','hub')/'home/apx';stage=home/'.cache/apx-wifi-form-test-20261020';assert not stage.exists();stage.mkdir();meta=home.stat()
try:
 shutil.copytree(home/'.config/quickshell/apx',stage/'apx')
 # The real form/inline button is tested with fictional network records and no broker process.
 template='''import QtQuick
import QtQuick.Controls
import Quickshell
import "apx"
ShellRoot {
 id:root
 property bool wifiPasswordVisible:true
 property bool menuKeyboardNavigation:false
 property bool wifiShowPassword:false
 property string wifiSelectedSsid:"NETWORK"
 property string wifiPassword:""
 property string wifiUsername:""
 property string wifiDomain:""
 property string wifiCaCert:"/etc/ssl/certs/ca-certificates.crt"
 property string wifiEnterpriseMethod:"PEAP"
 property string wifiMessage:""
 property var hostState:({network_name:""})
 property var focusedMenuItem:null
 property color textMain:"#e6e8ec"
 property color textDim:"#9299a6"
 property color cyan:"#55e6ff"
 property color controlButtonSurface:"#1b1d26"
 property color controlButtonActive:"#252a32"
 property color controlButtonHover:"#303640"
 property color controlButtonOutline:"#343947"
 property int menuBodySize:12
 property int menuSmallSize:11
 property int menuMetaSize:10
 function wifiIsKnown(name){return KNOWN}
 function wifiIsOpen(name){return false}
 function wifiIsEnterprise(name){return ENTERPRISE}
 function navigateGenericMenu(event){}
 function clearPendingMenuFocus(){}
 function submitWifiPassword(){throw new Error("No connection should be submitted")}
 function cancelWifiPassword(){}
 QtObject{id:wifiCredentialProcess;property bool running:false}
 QtObject{id:hostActionProcess;property bool running:false}
 component SelectionIndicator: Item {}
 BUTTON
 FloatingWindow {
  id:window;visible:true;implicitWidth:340;implicitHeight:Math.min(700,wifiPasswordCard.height+24);color:"#101117"
  Column {x:12;y:12;width:parent.width-24;CARD}
 }
 Timer {interval:2000;running:true;onTriggered:{console.error("FORM_TIMEOUT");Qt.exit(1)}}
 Timer {interval:300;running:true;onTriggered:{
  if(wifiPasswordCard.height<90 || wifiPasswordCard.width<280)throw new Error("Invalid form geometry")
  if(ENTERPRISE && (wifiCaInput.width<120 || !wifiUsernameInput.visible))throw new Error("Enterprise fields clipped")
  if(!KNOWN && (wifiPasswordInput.width<120 || wifiPasswordField.height<40))throw new Error("Password field too narrow")
  root.wifiShowPassword=true
  if(wifiPasswordInput.echoMode!==TextInput.Normal)throw new Error("Show password did not update")
  root.wifiShowPassword=false
  if(wifiPasswordInput.echoMode!==TextInput.Password)throw new Error("Password was not masked again")
  wifiPasswordCard.grabToImage(function(result){
   if(!result.saveToFile("/home/apx/.cache/apx-wifi-form-test-20261020/MODE.png"))throw new Error("Capture failed")
   console.log("FORM_PASS MODE",wifiPasswordCard.height)
   Qt.quit()
  })
 }}
}'''
 for mode,enterprise,known in [('personal',False,False),('enterprise',True,False),('saved',False,True)]:
  qml=template.replace('BUTTON',button).replace('CARD',card).replace('ENTERPRISE',str(enterprise).lower()).replace('KNOWN',str(known).lower()).replace('NETWORK','Universidade' if enterprise else 'Rede de exemplo').replace('MODE',mode)
  (stage/(mode+'.qml')).write_text(qml)
 for path in [stage]+list(stage.rglob('*')):os.chown(path,meta.st_uid,meta.st_gid)
 for mode in ['personal','enterprise','saved']:
  result=subprocess.run(['python',str(REPO/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','quickshell','--path','/home/apx/.cache/'+stage.name+'/'+mode+'.qml','--no-color'],capture_output=True,text=True,timeout=12)
  log=result.stdout+result.stderr;(REPO/'audit/2026-10-20-wifi-form'/(mode+'.log')).write_text(log);print(log[-1500:]);assert result.returncode==0 and 'FORM_PASS' in log
  shutil.copy2(stage/(mode+'.png'),REPO/'audit/2026-10-20-wifi-form'/(mode+'.png'))
finally:shutil.rmtree(stage)
