from pathlib import Path
import json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
marker=Path('/run/apx/active-graphical-environment-v1.json')
if not marker.exists():marker=Path('/run/apx/official-hub-graphical-v1.json')
home=Path('/var/lib/apx/environments')/json.loads(marker.read_text()).get('name','hub')/'home/apx'
stage=home/'.cache/apx-inbox-camera-native-test';assert not stage.exists();stage.mkdir()
source=(ROOT/'config/environment-shell-v1/quickshell/apx/DesktopActivity.qml').read_text();a=source.index('    function accept(text) {');b=source.index('    function refresh()',a);accept=source[a:b]
try:
 shutil.copytree(ROOT/'config/environment-shell-v1/quickshell/apx',stage/'apx')
 (stage/'apx/DesktopActivity.qml').write_text('''pragma Singleton
import QtQuick
QtObject {property var notificationEntries: [];property bool busy:false;property var actions:[]
 function action(args){actions=actions.concat([args])}}
''')
 (stage/'apx/Appearance.qml').write_text('''pragma Singleton
import QtQuick
QtObject {
 readonly property string fontFamily:"JetBrains Mono"
 readonly property int bodySize:12
 readonly property int metaSize:11
 readonly property int menuActionHeight:50
 readonly property int menuActionRadius:12
 readonly property int menuIconCircleSize:32
 readonly property int menuIconInset:9
 readonly property int menuGlyphSize:14
 readonly property int menuLabelInset:50
 readonly property color iconColor:"#d9dcea"
 readonly property color surface:"#1b1d26"
 readonly property color hover:"#292d3a"
 readonly property color active:"#353a4a"
 readonly property bool tintButtons:false
}
''')
 qml='''import QtQuick
import QtTest
import "apx" as A
import "apx/NotificationGroups.js" as Groups
Item {
 width:760;height:850
 property var sample:[
  {id:5,app:"ZapZap",title:"Ana",body:"Mensagem cinco",active:false,can_open:false},
  {id:4,app:"ZapZap",title:"Ana",body:"Mensagem quatro",active:false,can_open:false},
  {id:3,app:"ZapZap",title:"Bruno",body:"Mensagem três",active:false,can_open:false},
  {id:2,app:"Terminal",title:"Compilação",body:"Concluída",active:false,can_open:false}]
 QtObject {
  id:payload
  property var state:({players:[],notifications:[]})
  property var notificationEntries:[]
  property double clock:0
  property bool busy:false
  property var pendingSeek:null
  function position(p){return p.position||0}
  function settlePlaybackFeedback(){}
  function settleSeekFeedback(){}
  // ACCEPT
 }
 A.NotificationInbox {id:inbox;width:340;notes:payload.notificationEntries}
 A.CameraIndicator {id:camera;x:400;active:false;visible:active}
 SignalSpy {id:spy;target:payload;signalName:"notificationEntriesChanged"}
 TestCase {
  name:"InboxCamera";when:windowShown
  function init(){payload.accept(JSON.stringify({notifications:sample}));inbox.expandedApps=({});inbox.expandedThreads=({});spy.clear();camera.active=false;wait(30)}
  function test_groups_by_application_and_conversation(){
   compare(inbox.groups.length,2);compare(inbox.groups[0].app,"ZapZap")
   compare(inbox.groups[0].threads.length,2);compare(inbox.groups[0].threads[0].notes.length,2)
   compare(findChild(inbox,"notificationUnreadLabel").text,"4 mensagens por ler")
   compare(Groups.unreadLabel(1),"1 mensagem por ler");compare(Groups.unreadLabel(0),"0 mensagens por ler")
  }
  function test_expanding_app_and_thread(){
   var collapsed=inbox.implicitHeight;var key=inbox.groups[0].key
   inbox.toggleApp(key);wait(30);verify(inbox.implicitHeight>collapsed)
   var compact=inbox.implicitHeight;inbox.toggleThread(inbox.groups[0].threads[0].key);wait(30)
   verify(inbox.implicitHeight>compact);inbox.toggleApp(key);wait(30);compare(inbox.implicitHeight,collapsed)
  }
  function test_media_polling_and_equal_notifications_do_not_rebuild(){
   var before=inbox.groupKeys;var height=inbox.implicitHeight
   for(var i=0;i<20;i++){
    payload.accept(JSON.stringify({players:[]}))
    payload.accept(JSON.stringify({notifications:sample}))
   }
   wait(30);compare(spy.count,0);verify(inbox.groupKeys===before);compare(inbox.implicitHeight,height)
   verify(inbox.continuousScrollContent)
  }
  function test_group_action_is_id_snapshot(){
   A.DesktopActivity.actions=[];inbox.readGroup(inbox.groups[0].threads[0].notes)
   compare(A.DesktopActivity.actions[0][1],"read-group")
   compare(A.DesktopActivity.actions[0][2],"[5,4]")
  }
  function test_z_render_preview(){
   var done=false
   inbox.grabToImage(function(image){image.saveToFile("/home/apx/.cache/apx-notification-stack-preview.png");done=true})
   tryVerify(function(){return done},1000)
  }
  function test_camera_contour_runs_only_while_visible_and_active(){
   var animation=findChild(camera,"cameraContourAnimation");var contour=findChild(camera,"cameraUsageContour")
   verify(animation!==null);verify(!animation.running)
   camera.active=true;wait(120);verify(animation.running);verify(camera.phase>0);compare(camera.width,88);compare(camera.height,32)
   var done=false
   camera.grabToImage(function(result){result.saveToFile("/home/apx/.cache/camera-first.png");done=true})
   tryVerify(function(){return done},1000)
   wait(300);done=false
   camera.grabToImage(function(result){result.saveToFile("/home/apx/.cache/camera-second.png");done=true})
   tryVerify(function(){return done},1000)
   camera.visible=false;wait(30);verify(!animation.running)
   camera.visible=Qt.binding(function(){return camera.active});camera.active=false;wait(20);verify(!animation.running)
  }
 }
}
'''.replace('  // ACCEPT',accept)
 (stage/'tst_inbox.qml').write_text(qml);(OUT/'tst_inbox.qml').write_text(qml)
 meta=home.stat()
 for p in [stage]+list(stage.rglob('*')):os.chown(p,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=wayland','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=20)
 (OUT/'ui-results.log').write_text(result.stdout+result.stderr);print(result.stdout+result.stderr);assert result.returncode==0
 from PIL import Image, ImageChops
 first=Image.open(home/'.cache/camera-first.png').convert('RGBA');second=Image.open(home/'.cache/camera-second.png').convert('RGBA')
 white=sum(1 for r,g,b,a in first.getdata() if r>220 and g>220 and b>220 and a>100)
 assert 4 < white < 150, white
 assert ImageChops.difference(first,second).getbbox() is not None, 'Contour pixels did not move'
 print('VISIBLE_WHITE_MOVING_TRACE_PASS',white)
 shutil.copy2(home/'.cache/camera-first.png',OUT/'camera-trace-first.png')
 shutil.copy2(home/'.cache/camera-second.png',OUT/'camera-trace-second.png')
finally:shutil.rmtree(stage)
