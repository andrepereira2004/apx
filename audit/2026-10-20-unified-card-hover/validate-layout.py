from pathlib import Path
import json,os,shutil,subprocess
REPO=Path(__file__).resolve().parents[2]
source=(REPO/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
def block(needle):
 a=source.index(needle);depth=0
 for i in range(source.index('{',a),len(source)):
  if source[i]=='{':depth+=1
  elif source[i]=='}':
   depth-=1
   if depth==0:return source[a:i+1]
button=block('    component MenuButton: Rectangle {')
row=block('    component BluetoothDeviceRow: Rectangle {')
wifi=block('                        Rectangle {\n                            visible: !root.wifiPasswordVisible')
networks=block('                        Repeater {\n                            model: root.wifiDisplayPowered()').replace('Repeater {','Repeater { id:sampleWifiNetworks',1)
pair=block('                            Rectangle {\n                                id: bluetoothPairCard')
marker=Path('/run/apx/active-graphical-environment-v1.json');marker=marker if marker.exists() else Path('/run/apx/official-hub-graphical-v1.json')
state=json.loads(marker.read_text());home=Path('/var/lib/apx/environments')/state.get('name','hub')/'home/apx';stage=home/'.cache/apx-bt-layout-20261020';assert not stage.exists();stage.mkdir();meta=home.stat()
try:
 shutil.copytree(home/'.config/quickshell/apx',stage/'apx')
 for name in ['BounceMouseArea.qml','RadioIconButton.qml','MenuHover.qml','ControlTile.qml']:
  shutil.copy2(REPO/'config/environment-shell-v1/quickshell/apx'/name,stage/'apx'/name)
 (stage/'apx/qmldir').write_text('ControlTile 1.0 ControlTile.qml\nMenuHover 1.0 MenuHover.qml\nsingleton Appearance 1.0 Appearance.qml\nRadioIconButton 1.0 RadioIconButton.qml\nControlIcon 1.0 ControlIcon.qml\nLucideIcon 1.0 LucideIcon.qml\nBounceMouseArea 1.0 BounceMouseArea.qml\n')
 (stage/'apx/Appearance.qml').write_text('pragma Singleton\nimport QtQuick\nQtObject {property int bodySize:12;property color active:"#353a4a";property bool tintButtons:false;property color hover:"#292d3a";property color iconColor:"white";property color surface:"#1b1d26";property string fontFamily:"sans-serif"}')
 qml='''import QtQuick
import QtQuick.Controls
import QtTest
import "apx"
Item {
 id:root;width:340;height:800
 property color controlButtonSurface:"#1b1d26"
 property color controlButtonActive:"#252a32"
 property color controlButtonHover:"#303640"
 property color controlButtonOutline:"#343947"
 property color textMain:"white"
 property color textDim:"#939baa"
 property color cyan:"white"
 property int menuBodySize:12
 property int menuSmallSize:11
 property int menuMetaSize:10
 property bool wifiPasswordVisible:false
 property string wifiTogglePhase:""
 property string wifiSelectedSsid:""
 property bool wifiSelectionTap:false
 property bool menuKeyboardNavigation:false
 property var focusedMenuItem:null
 property var hostState:({network_name:"Rede ativa"})
 property string bluetoothDevicePendingAddress:""
 property string bluetoothPairPhase:"needs-response"
 property string bluetoothPairChallenge:"pin"
 property string bluetoothPairPasskey:""
 property string bluetoothPairName:"Auscultadores"
 property string bluetoothMessage:""
 property string bluetoothPairPin:""
 property bool bluetoothShowPin:false
 property int deviceActions:0
 property int forgetActions:0
 property int acceptedPins:0
 function wifiDisplayPowered(){return true}
 function wifiDisplayActive(){return true}
 function wifiCurrentSignal(){return 75}
 function wifiAvailableNetworks(){return ["Outra rede"]}
 function wifiDetails(name){return {signal:60}}
 function wifiIsOpen(name){return false}
 function cancelWifiPassword(){}
 function toggleWifiConnection(){throw new Error("No real connection action")}
 function toggleWifiPower(){throw new Error("No real radio action")}
 function beginWifiConnect(name){}
 function clearPendingMenuFocus(){}
 function navigateGenericMenu(event){}
 function respondBluetoothPair(accept,pin){if(accept&&pin==="123456")acceptedPins++}
 function cancelBluetoothPairing(){}
 function dismissBluetoothPairing(){}
 QtObject {id:wifiPowerProcess;property bool running:false}
 QtObject {id:bluetoothPairBeginProcess;property bool running:false}
 QtObject {id:bluetoothPairRespondProcess;property bool running:false}
 component SelectionIndicator: Item {}
 BUTTON
 ROW
 Column {id:sample;width:316;spacing:8
 WIFI
 NETWORKS
 BluetoothDeviceRow {id:connected;device:({address:"A",name:"Dispositivo ligado"});connected:true;paired:true;onActivated:root.deviceActions++}
 BluetoothDeviceRow {id:known;device:({address:"B",name:"Dispositivo guardado"});paired:true;onActivated:root.deviceActions++;onForgetRequested:root.forgetActions++}
 BluetoothDeviceRow {id:available;device:({address:"C",name:"Dispositivo disponível"});onActivated:root.deviceActions++}
 PAIR
 }
 TestCase {
  name:"WirelessLayouts";when:windowShown
  function primary(row,label){for(var i=0;i<row.children.length;i++){var child=row.children[i];for(var j=0;j<child.children.length;j++){var candidate=child.children[j];if(candidate.label===label)return candidate}}return null}
  function test_whole_card_across_both_actions(){
   var tile=Qt.createQmlObject('import QtQuick; import "apx"; ControlTile { z:1000; width:316; height:48; quiet:true; showCaption:true; caption:"Wi-Fi"; iconName:"wifi"; iconActionEnabled:true }',root)
   var base=tile.color.toString()
   mouseMove(tile,220,24);wait(150);compare(tile.color.toString(),"#292d3a")
   var decoration=tile.children.filter(function(c){return c.hovered!==undefined})[0]
   compare(decoration.x,0);compare(decoration.width,tile.width)
   var icon=tile.children.filter(function(c){return c.powered!==undefined})[0]
   var bodyHoverIconColor=icon.color.r
   mouseMove(tile,24,24);wait(150);compare(tile.color.toString(),"#292d3a")
   compare(decoration.width,tile.width)
   verify(icon.color.r>bodyHoverIconColor)
   compare(icon.border.width,2)
   compare(icon.border.color.toString(),"#69728a")
   mouseMove(tile,220,24);wait(150)
   compare(icon.color.r,bodyHoverIconColor)
   compare(icon.border.width,0)
   mouseMove(root,335,795);wait(150);compare(tile.color.toString(),base)
   tile.destroy()
  }
  function test_alignment_actions_and_pairing_fields(){
   var activeCard=sample.children[0]
   var activeIcon=activeCard.children.filter(function(child){return child.powered!==undefined})[0]
   var nearby=sampleWifiNetworks.itemAt(0)
   var nearbyIcon=nearby.children.filter(function(child){return child.name!==undefined})[0]
   compare(activeIcon.x+activeIcon.width/2,nearbyIcon.x+nearbyIcon.width/2)
   compare(nearbyIcon.width,16)
   var wifiDisconnect=activeCard.children.filter(function(c){return c.label==="Desconectar"})[0]
   mouseMove(root,335,795);wait(150)
   var idleDisconnect=wifiDisconnect.color.r
   mouseMove(activeCard,70,28);wait(150)
   verify(wifiDisconnect.color.r>idleDisconnect)
   compare(wifiDisconnect.color.toString(),activeIcon.color.toString())
   mouseMove(wifiDisconnect,50,16);wait(150)
   verify(wifiDisconnect.color.r>activeIcon.color.r)
   mouseMove(root,335,795);wait(150)
   compare(wifiDisconnect.color.r,idleDisconnect)
   var cardFill=activeCard.color.toString()
   mouseMove(activeIcon,18,18);wait(150)
   compare(activeCard.color.toString(),"#292d3a")
   var cardFeedback=activeCard.children.filter(function(c){return c.hovered!==undefined})[0]
   verify(cardFeedback.hovered)
   compare(cardFeedback.width,activeCard.width)
   compare(cardFeedback.height,activeCard.height)
   mouseMove(root,335,795);wait(150)
   compare(activeCard.color.toString(),cardFill)
   for(var row of [connected,known,available]){
    var glyph=row.children.filter(function(child){return child.name!==undefined})[0]
    compare(glyph.x+glyph.width/2,activeIcon.x+activeIcon.width/2)
    compare(glyph.width,16)
   }
   var disconnect=primary(connected,"Desconectar");verify(disconnect!==null)
   var normalColor=disconnect.color.toString()
   mouseMove(disconnect,disconnect.width/2,16);wait(150)
   compare(disconnect.color.toString(),Qt.lighter("#292d3a",1.95).toString())
   compare(disconnect.border.width,2)
   compare(disconnect.radius,10)
   var feedback=disconnect.children.filter(function(c){return c.hovered!==undefined})[0]
   verify(feedback.hovered)
   compare(feedback.width,disconnect.width)
   compare(feedback.children.filter(function(c){return c.border!==undefined})[0].border.color.toString(),"#69728a")
   mouseMove(root,335,795);wait(150)
   compare(disconnect.color.toString(),normalColor)
   mouseClick(disconnect,disconnect.width/2,16);wait(100);compare(root.deviceActions,1)
   var forget=primary(known,"…");verify(forget!==null)
   mouseClick(forget,15,16);wait(100);compare(root.forgetActions,1)
   compare(bluetoothPinField.height,40)
   root.bluetoothPairPin="123456";root.bluetoothShowPin=true
   compare(bluetoothPinInput.echoMode,TextInput.Normal)
   root.bluetoothShowPin=false;compare(bluetoothPinInput.echoMode,TextInput.Password)
   bluetoothPairCard.grabToImage(function(result){result.saveToFile("/home/apx/.cache/apx-bt-layout-20261020/pin.png")});wait(80)
   bluetoothPinInput.forceActiveFocus();keyClick(Qt.Key_Return);compare(root.acceptedPins,1)
   root.bluetoothPairChallenge="confirm";root.bluetoothPairPasskey="123456";wait(80)
   bluetoothPairCard.grabToImage(function(result){result.saveToFile("/home/apx/.cache/apx-bt-layout-20261020/confirm.png")});wait(80)
   sample.grabToImage(function(result){result.saveToFile("/home/apx/.cache/apx-bt-layout-20261020/layout.png")});wait(80)
  }
 }
}'''.replace('BUTTON',button).replace('ROW',row).replace('WIFI',wifi).replace('NETWORKS',networks).replace('PAIR',pair)
 (stage/'tst_layout.qml').write_text(qml)
 for path in [stage]+list(stage.rglob('*')):os.chown(path,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(REPO/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=15)
 log=result.stdout+result.stderr;(REPO/'audit/2026-10-20-unified-card-hover/layout-test.log').write_text(log);print(log);assert result.returncode==0
 for name in ['pin.png','confirm.png','layout.png']:
  if(stage/name).exists():shutil.copy2(stage/name,REPO/'audit/2026-10-20-unified-card-hover'/name)
finally:shutil.rmtree(stage)
