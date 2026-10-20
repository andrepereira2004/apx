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
volume=block('                    Rectangle {\n                        id: mouseSensitivityCard')
brightness=block('                    Rectangle {\n                        id: trackpadSensitivityCard')
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
 property var pointerDevices:({mouse:{enabled:true,available:true},trackpad:{enabled:true,available:true}})
 property int pointerToggles:0
 function togglePointer(kind){pointerToggles++}
 QtObject {id:pointerPowerProcess;property bool running:false}
 property int mouseSensitivity:0
 property int trackpadSensitivity:-30
 function setMouseSensitivity(value){mouseSensitivity=value;volumeCommits++}
 function setTrackpadSensitivity(value){trackpadSensitivity=value;brightnessCommits++}
 QtObject {id:mouseSensitivityProcess;property bool running:false}
 QtObject {id:trackpadSensitivityProcess;property bool running:false}
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
   compare(mouseSensitivityCard.height,56);compare(trackpadSensitivityCard.height,56)
   for(var slider of [mouseSensitivitySlider,trackpadSensitivitySlider]) {
    verify(slider.width>150);compare(slider.x,54)
    compare(slider.y+slider.height/2,28)
   }
   cards.grabToImage(function(result){result.saveToFile("/home/apx/.cache/apx-inline-slider-test-20261020/cards.png")});wait(80)
   mouseClick(mouseSensitivityCard,26,28);wait(100)
   compare(pointerToggles,1)
   mouseClick(mouseSensitivitySlider,mouseSensitivitySlider.width*.7,mouseSensitivitySlider.height/2);wait(100)
   verify(volumeCommits>0)
   mouseClick(trackpadSensitivitySlider,trackpadSensitivitySlider.width*.6,trackpadSensitivitySlider.height/2);wait(100)
   verify(brightnessCommits>0)
   var mouseBefore=volumeCommits;var touchBefore=brightnessCommits
   for(var pair of [[mouseSensitivityCard,mouseSensitivitySlider],[trackpadSensitivityCard,trackpadSensitivitySlider]]) {
    var card=pair[0];var slider=pair[1]
    compare(slider.height,16)
    slider.focus=false
    mouseClick(card,150,slider.y-3);wait(100);verify(slider.activeFocus)
    slider.focus=false
    mouseClick(card,150,slider.y+slider.height+3);wait(100);verify(slider.activeFocus)
   }
   compare(volumeCommits,mouseBefore);compare(brightnessCommits,touchBefore)
   root.menuKeyboardNavigation=true
   trackpadSensitivitySlider.forceActiveFocus();keyClick(Qt.Key_Return)
   var before=brightnessCommits;keyClick(Qt.Key_Right);verify(brightnessCommits>before)

  }
 }
}'''.replace('SLIDER',slider).replace('VOLUME',volume).replace('BRIGHTNESS',brightness)
 (stage/'tst_inline.qml').write_text(qml)
 for path in [stage]+list(stage.rglob('*')):os.chown(path,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(REPO/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=15)
 log=result.stdout+result.stderr;(REPO/'audit/2026-10-20-input-sliders/input-test.log').write_text(log);print(log);assert result.returncode==0
 if (stage/'cards.png').exists():shutil.copy2(stage/'cards.png',REPO/'audit/2026-10-20-input-sliders/cards.png')
finally:shutil.rmtree(stage)
