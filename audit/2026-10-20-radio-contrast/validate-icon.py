from pathlib import Path
import json
import os
import shutil
import subprocess
REPO=Path(__file__).resolve().parents[2]
marker=Path('/run/apx/active-graphical-environment-v1.json');marker=marker if marker.exists() else Path('/run/apx/official-hub-graphical-v1.json')
state=json.loads(marker.read_text());home=Path('/var/lib/apx/environments')/state.get('name','hub')/'home/apx';stage=home/'.cache/apx-radio-contrast-20261020';assert not stage.exists();stage.mkdir();meta=home.stat()
try:
 shutil.copytree(home/'.config/quickshell/apx',stage/'apx')
 for name in ['ControlTile.qml','RadioIconButton.qml']:(stage/'apx'/name).write_bytes((REPO/'config/environment-shell-v1/quickshell/apx'/name).read_bytes())
 (stage/'apx/qmldir').write_text('singleton Appearance 1.0 Appearance.qml\nControlTile 1.0 ControlTile.qml\nRadioIconButton 1.0 RadioIconButton.qml\nControlIcon 1.0 ControlIcon.qml\nLucideIcon 1.0 LucideIcon.qml\nBounceMouseArea 1.0 BounceMouseArea.qml\n')
 # Pointer routing uses the real component with a static palette; Quickshell's Io plugin is embedded in its binary.
 (stage/'apx/Appearance.qml').write_text('pragma Singleton\nimport QtQuick\nQtObject { property bool tintButtons:false; property color active:"#353a4a"; property color surface:"#1b1d26"; property color iconColor:"white"; property string fontFamily:"sans-serif"; property int bodySize:12 }')
 (stage/'tst_icon.qml').write_text('''import QtQuick
import QtTest
import "apx" as APX
Item {
 width:340;height:100
 property int iconActions:0
 property int navigationActions:0
 APX.ControlTile {
  id:tile; width:320;height:56;showCaption:true;caption:"Wi-Fi";iconName:"wifi"
  quiet:true;selected:true;iconActionEnabled:true;iconActionLabel:"Desativar Wi-Fi"
  onIconActivated: { iconActions++; selected = !selected; iconName = selected ? "wifi" : "wifi-off" }
  onActivated:navigationActions++
 }
 TestCase {
  name:"WifiIconActions";when:windowShown
  function test_routes_icon_body_and_disabled_icon() {
   var button = tile.children.filter(function(child){return child.powered !== undefined})[0]
   verify(button !== undefined)
   mouseMove(tile,180,28);wait(150)
   verify(button.color.r < tile.color.r)
   mouseMove(tile,20,28);wait(150)
   verify(button.color.r < tile.color.r)
   tile.grabToImage(function(result){result.saveToFile("/home/apx/.cache/apx-radio-contrast-20261020/on.png")});wait(60)
   compare(tile.border.width,0)
   mouseClick(tile,20,28);wait(130)
   tile.grabToImage(function(result){result.saveToFile("/home/apx/.cache/apx-radio-contrast-20261020/off.png")});wait(60)
   compare(iconActions,1);compare(navigationActions,0);compare(tile.border.width,0)
   mouseClick(tile,180,28);wait(130)
   compare(iconActions,1);compare(navigationActions,1)
   tile.iconActionAvailable=false
   mouseClick(tile,20,28);wait(130)
   compare(iconActions,1);compare(navigationActions,1)
  }
 }
}''')
 for path in [stage]+list(stage.rglob('*')):os.chown(path,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(REPO/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=15)
 log=result.stdout+result.stderr;(REPO/'audit/2026-10-20-radio-contrast/icon-test.log').write_text(log);print(log);assert result.returncode==0
finally:
 for name in ['on.png','off.png']:
  if (stage/name).is_file():shutil.copy2(stage/name,REPO/'audit/2026-10-20-radio-contrast'/('icon-'+name))
 shutil.rmtree(stage)
