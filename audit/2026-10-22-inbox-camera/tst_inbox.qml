import QtQuick
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
    function accept(text) {
        try {
            if (!text.trim().length) return
            var report = JSON.parse(text)
            clock = Date.now()
            if (report.players) {
                report.players = report.players.map(function(player) {
                    var previous = state.players.find(function(old) { return old.name === player.name && old.track_id === player.track_id })
                    if (previous && Number(previous.sampled_at) > Number(player.sampled_at)) return previous
                    if (previous && previous.status === "Playing" && player.status === "Playing" && !activity.busy && !(pendingSeek && pendingSeek.name === player.name && pendingSeek.track === player.track_id)) {
                        var predicted = position(previous)
                        var measured = position(player)
                        // Ignore sub-frame sampling drift; real seeks remain authoritative.
                        if (Math.abs(predicted - measured) < 0.35) {
                            player.position = predicted
                            player.sampled_at = clock
                        }
                    }
                    return player
                })
            }
            if (report.notifications) {
                if (JSON.stringify(report.notifications) !== JSON.stringify(notificationEntries))
                    notificationEntries = report.notifications
                report.notifications = notificationEntries
            }
            // Notification polling must not rebuild unchanged media/menu models.
            var next = Object.assign({}, state, report)
            if (JSON.stringify(next) !== JSON.stringify(state)) state = next
            settlePlaybackFeedback()
            settleSeekFeedback()
        } catch (e) {}
    }

 }
 A.NotificationInbox {id:inbox;width:340;notes:payload.notificationEntries}
 A.CameraIndicator {id:camera;x:400;active:false;visible:active}

 QtObject {
  id:controller
  property string opened:""
  property color popupPanel:"#1b1d26"
  property color shellBorder:"#4f566c"
  property color controlButtonOutline:"#4f566c"
  property bool airplaneMode:false
  property bool volumeMuted:false
  function wifiDisplayActive(){return true}
  function bluetoothDisplayPowered(){return false}
  function openActivitySection(kind){opened=kind}
  function openControlSection(kind){}
  function openMoreOptions(){}
  function runControlAction(action){}
 }
 A.ControlDashboard {id:dashboard;x:400;y:100;width:340;controller:controller}
 SignalSpy {id:spy;target:payload;signalName:"notificationEntriesChanged"}
 TestCase {
  name:"InboxCamera";when:windowShown
  function init(){payload.accept(JSON.stringify({notifications:sample}));inbox.expandedApps=({});inbox.expandedThreads=({});spy.clear();camera.active=false;wait(30)}

  function test_dashboard_notification_shortcut(){
   var button=findChild(dashboard,"notificationShortcut");verify(button!==null)
   A.DesktopActivity.notificationEntries=sample;wait(20)
   compare(button.caption,"4 mensagens por ler")
   button.activated();compare(controller.opened,"notifications")
   A.DesktopActivity.notificationEntries=[];wait(20)
   compare(button.caption,"0 mensagens por ler");verify(button.enabled)
   var emptyHeight=dashboard.implicitHeight
   A.DesktopActivity.notificationEntries=sample;wait(20)
   compare(dashboard.implicitHeight,emptyHeight)
  }
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
