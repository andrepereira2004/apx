"""Exercise the real creation controls with fake submission, never creating an Environment."""
from pathlib import Path
import json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
s=(ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
def block(marker):
 start=s.index(marker);a=s.index('{',start);depth=1;end=a+1
 while depth:
  if s[end]=='{':depth+=1
  elif s[end]=='}':depth-=1
  end+=1
 return s[start:end]
form=block('Column {\n                        id: environmentCreationForm')
components='\n'.join(block('component '+name+':') for name in ('MenuButton','CreationChoice','FeatureCard','SelectionIndicator'))
functions='\n'.join(block('function '+name+'(') for name in ('environmentCreateVisibleFocusIndices','moveEnvironmentCreateFocus','moveEnvironmentCreateVertical','moveEnvironmentCreateHorizontal','activateEnvironmentCreateFocus','environmentModuleIndex'))
qml='''import QtQuick
import QtTest
import "apx"
Item {
 id: root; width:520; height:1000
 property bool isHub:true
 property bool environmentCreateOpen:true
 property bool environmentManagementBusy:false
 property bool environmentCreateCustomizeOpen:false
 property bool environmentKeyboardFocus:true
 property string environmentDraftName:""
 property string environmentDraftDescription:""
 property string environmentSystemKind:"arch"
 property string environmentFeatureDrawer:""
 property string environmentFeatureInfo:""
 property int environmentCreateFocusIndex:-1
 property int environmentNativeWindowsSizeGib:120
 property var environmentSelectedModules:({system:true,files:true})
 property var environmentModuleGroups:[{key:'essentials',label:'System',modules:['system','files']}]
 property var environmentModuleCatalog:[{key:'system'},{key:'files'}]
 property int environmentCreateModuleFocusBase:14
 property int environmentCreateSubmitFocusIndex:32
 property var nativeCreationPreview:({})
 property color controlButtonSurface:'#1b1d26'
 property color controlButtonActive:'#353a4a'
 property color controlButtonOutline:'#414654'
 property color controlButtonHover:'#292d3a'
 property color textMain:'#d9dcea'
 property color textDim:'#a4abc0'
 property color cyan:'#55e6ff'
 property int menuBodySize:12
 property int menuSmallSize:12
 property int menuMetaSize:10
 property int menuTitleSize:14
 property int submitted:0
 property string submittedName:""
 function cancelEnvironmentCreate(){environmentCreateOpen=false}
 function createEnvironment(name,description){submitted++;submittedName=name}
 function environmentModuleInfo(key){return {key:key,label:key,detail:'Details',programs:'Apps'}}
 function setEnvironmentModule(key,enabled){var next=Object.assign({},environmentSelectedModules);next[key]=enabled;environmentSelectedModules=next}
 QtObject {id:nativeCreationPreviewProcess;property bool running:false}
 Item {id:environmentMenu;width:root.width;height:root.height
 FORM
 }
 COMPONENTS
 Component {id:basicAction;MenuButton {}}
 Component {id:tileAction;ControlTile {}}
 FUNCTIONS
 TestCase {
  name:'EnvironmentCreation';when:windowShown
  function init(){root.environmentSystemKind='arch';root.environmentCreateCustomizeOpen=false;root.environmentDraftName='';root.environmentDraftDescription='';root.environmentFeatureDrawer='';root.submitted=0;wait(30)}
  function test_shared_action_dimensions(){
   for (var i=0;i<5;i++) {
    var button=basicAction.createObject(root,{label:['Environment','IA','Bateria','Controlos','Calendário'][i],iconName:'box'})
    compare(button.height,50);compare(button.radius,12)
    var circle=findChild(button,'menuIconCircle');verify(circle);compare(circle.width,32);compare(circle.x,9);compare(circle.y,9);compare(button.height-circle.y-circle.height,9)
    button.destroy()
   }
   var tile=tileAction.createObject(root,{showCaption:true,caption:'Ligações'})
   compare(tile.height,50);compare(tile.radius,12)
   var circle=findChild(tile,'controlIconCircle');verify(circle);compare(circle.width,32);compare(circle.x,9);compare(circle.y,9);compare(tile.height-circle.y-circle.height,9)
   tile.destroy()
  }
  function test_input_submit_and_collapsed_options(){
   var submit=findChild(root,'createSubmit');verify(submit);verify(!submit.enabled)
   mouseClick(environmentNameInput,10,12);keyClick(Qt.Key_T);keyClick(Qt.Key_E);keyClick(Qt.Key_S);keyClick(Qt.Key_T)
   compare(root.environmentDraftName,'test');verify(submit.enabled)
   mouseClick(environmentDescriptionInput,10,12);keyClick(Qt.Key_A);compare(root.environmentDraftDescription,'a')
   verify(environmentCreationForm.height<600)
   mouseClick(submit,submit.width/2,submit.height/2);compare(root.submitted,1);compare(root.submittedName,'test')
   var indices=root.environmentCreateVisibleFocusIndices();verify(indices.indexOf(5)>=0);verify(indices.indexOf(6)<0);verify(indices.indexOf(9)<0)
  }
  function test_system_switch_and_sizes(){
   var windows=findChild(root,'createWindowsChoice');mouseClick(windows,windows.width/2,windows.height/2)
   compare(root.environmentSystemKind,'windows-native');compare(root.environmentDraftName,'windows-2')
   var indices=root.environmentCreateVisibleFocusIndices();verify(indices.indexOf(5)<0);verify(indices.indexOf(6)>=0)
   root.environmentCreateFocusIndex=8;root.activateEnvironmentCreateFocus();compare(root.environmentNativeWindowsSizeGib,250)
   var apx=findChild(root,'createApxChoice');mouseClick(apx,apx.width/2,apx.height/2);compare(root.environmentSystemKind,'arch')
  }
  function test_advanced_options_and_keyboard(){
   var advanced=findChild(root,'createCustomize');mouseClick(advanced,advanced.width/2,advanced.height/2)
   verify(root.environmentCreateCustomizeOpen);verify(root.environmentCreateVisibleFocusIndices().indexOf(9)>=0)
   root.environmentCreateFocusIndex=9;root.activateEnvironmentCreateFocus();compare(root.environmentFeatureDrawer,'essentials')
   verify(root.environmentCreateVisibleFocusIndices().indexOf(14)>=0)
   root.environmentCreateFocusIndex=5;root.activateEnvironmentCreateFocus();verify(!root.environmentCreateCustomizeOpen)
   root.moveEnvironmentCreateFocus(1);compare(root.environmentCreateFocusIndex,32)
  }
 }
}
'''.replace('FORM',form).replace('COMPONENTS',components).replace('FUNCTIONS',functions)
marker=Path('/run/apx/active-graphical-environment-v1.json');marker=marker if marker.exists() else Path('/run/apx/official-hub-graphical-v1.json');state=json.loads(marker.read_text());home=Path('/var/lib/apx/environments')/state.get('name','hub')/'home/apx';stage=home/'.cache/apx-create-form-validation';assert not stage.exists();stage.mkdir();meta=home.stat()
try:
 shutil.copytree(ROOT/'config/environment-shell-v1/quickshell/apx',stage/'apx')
 (stage/'apx/Appearance.qml').write_text('pragma Singleton\nimport QtQuick\nQtObject { property string fontFamily: "monospace"; property bool tintButtons:false; property color hover:"#292d3a"; property color iconColor:"#d9dcea"; property real interactionSpeed:1; property bool reduceMotion:false; property int bodySize:12; property int motionDuration:100; property int menuActionHeight:50; property int menuIconCircleSize:32; property int menuGlyphSize:14; property int menuIconInset:9; property int menuLabelInset:50; property int menuActionRadius:12 }')
 (stage/'apx/qmldir').write_text('singleton Appearance 1.0 Appearance.qml\n')
 (stage/'tst_form.qml').write_text(qml)
 for p in [stage,*stage.rglob('*')]:os.chown(p,meta.st_uid,meta.st_gid)
 r=subprocess.run(['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=20)
 (Path(__file__).parent/'form-test.log').write_text(r.stdout+r.stderr);print((r.stdout+r.stderr)[-4500:]);assert r.returncode==0
finally:shutil.rmtree(stage)
