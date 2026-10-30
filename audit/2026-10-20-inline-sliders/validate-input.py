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
volume=block('                        Rectangle {\n                            id: combinedVolumeCard')
brightness=block('                        Rectangle {\n                            id: combinedBrightnessCard')
slider=block('    component MenuSlider: Slider {')
marker=Path('/run/apx/active-graphical-environment-v1.json');marker=marker if marker.exists() else Path('/run/apx/official-hub-graphical-v1.json')
state=json.loads(marker.read_text());home=Path('/var/lib/apx/environments')/state.get('name','hub')/'home/apx';stage=home/'.cache/apx-inline-slider-test-20261020';assert not stage.exists();stage.mkdir();meta=home.stat()
try:
 shutil.copytree(home/'.config/quickshell/apx',stage/'apx')
 for name in ['RadioIconButton.qml','MenuHover.qml','BounceMouseArea.qml']:
  shutil.copy2(REPO/'config/environment-shell-v1/quickshell/apx'/name,stage/'apx'/name)
 (stage/'apx/qmldir').write_text('MenuHover 1.0 MenuHover.qml\nsingleton Appearance 1.0 Appearance.qml\nRadioIconButton 1.0 RadioIconButton.qml\nControlIcon 1.0 ControlIcon.qml\nLucideIcon 1.0 LucideIcon.qml\nBounceMouseArea 1.0 BounceMouseArea.qml\n')
 (stage/'apx/Appearance.qml').write_text('pragma Singleton\nimport QtQuick\nQtObject {property bool tintButtons:false;property color hover:"#292d3a";property color iconColor:"white";property color surface:"#1b1d26";property string fontFamily:"sans-serif"}')
 qml='''import QtQuick
import QtQuick.Controls
import QtTest
import "apx"
Item {
 id:root;width:340;height:160
 property color controlButtonSurface:"#1b1d26"
 property color controlButtonOutline:"#343947"
 property color textDim:"#939baa"
 property color textMain:"white"
 property color cyan:"white"
 property int menuBodySize:12
 property bool menuKeyboardNavigation:false
 property Item editingMenuSlider:null
 property bool volumeMuted:false
 property int volumeValue:55
 property int displayBrightness:80
 property int muteActions:0
 property int openActions:0
 property int dimActions:0
 property int volumeCommits:0
 property int brightnessCommits:0
 function openControlSection(section){openActions++}
 function toggleVolumeMute(){muteActions++}
 function toggleDisplayDim(){dimActions++}
 function previewVolume(value){volumeValue=value}
 function commitVolume(value){volumeValue=value;volumeCommits++}
 function previewDisplayBrightness(value){displayBrightness=value}
 function commitDisplayBrightness(value){displayBrightness=value;brightnessCommits++}
 function navigateGenericMenu(event){}
 QtObject {id:localActionProcess;property bool running:false}
 QtObject {id:displayBrightnessProcess;property bool running:false}
 SLIDER
 Column {id:cards;width:320;spacing:8
 VOLUME
 BRIGHTNESS
 }
 TestCase {
  name:"InlineSliders";when:windowShown
  function test_input_regions_and_alignment() {
   verify(combinedVolumeSlider.width>150)
   compare(combinedVolumeSlider.y+combinedVolumeSlider.height/2,combinedVolumeCard.height/2)
   compare(displayBrightnessSlider.y+displayBrightnessSlider.height/2,combinedBrightnessCard.height/2)
   cards.grabToImage(function(result){result.saveToFile("/home/apx/.cache/apx-inline-slider-test-20261020/cards.png")});wait(80)
   mouseClick(combinedVolumeCard,25,28);wait(120)
   compare(muteActions,1);compare(openActions,0)
   mouseClick(combinedVolumeSlider,combinedVolumeSlider.width*.7,combinedVolumeSlider.height/2);wait(120)
   verify(volumeCommits>0);compare(openActions,0);compare(muteActions,1)
   mouseClick(combinedVolumeCard,combinedVolumeCard.width-20,28);wait(120)
   compare(openActions,1)
   mouseClick(combinedBrightnessCard,25,28);wait(120)
   compare(dimActions,1)
   mouseClick(displayBrightnessSlider,displayBrightnessSlider.width*.6,displayBrightnessSlider.height/2);wait(120)
   verify(brightnessCommits>0);compare(dimActions,1)
   mouseClick(combinedBrightnessCard,combinedBrightnessCard.width-20,28);wait(120)
   compare(dimActions,2)
   var soundBefore=volumeCommits
   var brightnessBefore=brightnessCommits
   var openedBefore=openActions
   mouseClick(combinedVolumeCard,150,combinedVolumeSlider.y-3);wait(120)
   mouseClick(combinedVolumeCard,150,combinedVolumeSlider.y+combinedVolumeSlider.height+3);wait(120)
   compare(openActions,openedBefore+2);compare(volumeCommits,soundBefore)
   var dimBefore=dimActions
   mouseClick(combinedBrightnessCard,150,displayBrightnessSlider.y-3);wait(120)
   mouseClick(combinedBrightnessCard,150,displayBrightnessSlider.y+displayBrightnessSlider.height+3);wait(120)
   compare(dimActions,dimBefore+2);compare(brightnessCommits,brightnessBefore)
   root.menuKeyboardNavigation=true
   combinedVolumeSlider.forceActiveFocus()
   keyClick(Qt.Key_Return)
   var before=volumeCommits
   keyClick(Qt.Key_Right)
   verify(volumeCommits>before)
  }
 }
}'''.replace('SLIDER',slider).replace('VOLUME',volume).replace('BRIGHTNESS',brightness)
 (stage/'tst_inline.qml').write_text(qml)
 for path in [stage]+list(stage.rglob('*')):os.chown(path,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(REPO/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=15)
 log=result.stdout+result.stderr;(REPO/'audit/2026-10-20-inline-sliders/input-test.log').write_text(log);print(log);assert result.returncode==0
 if (stage/'cards.png').exists():shutil.copy2(stage/'cards.png',REPO/'audit/2026-10-20-inline-sliders/cards.png')
finally:shutil.rmtree(stage)
