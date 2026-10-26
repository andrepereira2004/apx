import QtQuick
import QtQuick.Window
import QtTest
Rectangle {
 id:dashboard;width:220;height:220;color:"#ff0000"
 property var controller:({popupPanel:"#101117",shellBorder:"#808080"})
 property real displayScale:Window.window.devicePixelRatio
 readonly property real outlineWidth:Math.max(1,Math.round(displayScale))/displayScale
    component DashboardCard: Rectangle {
        id: card
        color: dashboard.controller.popupPanel
        antialiasing: true
        Rectangle {
            anchors.fill: parent
            anchors.margins: 1 / dashboard.displayScale
            radius: Math.max(0, card.radius - anchors.margins)
            color: "transparent"
            antialiasing: true
            border.pixelAligned: false
            border.width: dashboard.outlineWidth
            border.color: dashboard.controller.shellBorder
            z: 100
        }
    }

 DashboardCard {id:card;x:20;y:20;width:180;height:180;radius:20}
 TestCase {
  name:'DashboardOutline';when:windowShown
  function test_same_stroke_on_all_sides_at_monitor_scale() {
   wait(80);var frame=grabImage(dashboard),dpr=frame.width/dashboard.width
   fuzzyCompare(dpr,1.5,0.01)
   fuzzyCompare(dashboard.outlineWidth*dpr,Math.round(dpr),0.01)
   var left=0,right=0,top=0,bottom=0
   for(var i=0;i<Math.ceil(6*dpr);i++) {
    var l=frame.pixel(Math.round(20*dpr)+i,Math.floor(110*dpr)).g
    var r=frame.pixel(Math.round(200*dpr)-1-i,Math.floor(110*dpr)).g
    var t=frame.pixel(Math.floor(110*dpr),Math.round(20*dpr)+i).g
    var b=frame.pixel(Math.floor(110*dpr),Math.round(200*dpr)-1-i).g
    left+=Math.max(0,(l-17/255)/(128/255-17/255))
    right+=Math.max(0,(r-17/255)/(128/255-17/255))
    top+=Math.max(0,(t-17/255)/(128/255-17/255))
    bottom+=Math.max(0,(b-17/255)/(128/255-17/255))
   }
   fuzzyCompare(left,right,0.08);fuzzyCompare(left,top,0.08);fuzzyCompare(top,bottom,0.08)
   verify(left>0.8)
   frame.save(Qt.resolvedUrl('outline.png').toString().replace('file://',''))
   console.log('OUTLINE_METRICS',JSON.stringify({dpr:dpr,left:left,right:right,top:top,bottom:bottom}))
  }
 }
}
