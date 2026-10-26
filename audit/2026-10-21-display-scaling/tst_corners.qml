import QtQuick
import QtQuick.Window
import QtQuick.Window
import QtQuick.Effects
import QtTest
Rectangle {
 id:root;width:220;height:220;color:"#ff0000"
 property var popup:({open:true})
        Rectangle {
            id: popupClipMask
            width: popupBackground.width
            height: popupBackground.height
            radius: popupBackground.radius
            color: "white"
            visible: false
            layer.enabled: popup.open
            layer.textureSize: Qt.size(Math.ceil(width * popupBackground.textureScale), Math.ceil(height * popupBackground.textureScale))
        }


 Rectangle {
  id:popupBackground;readonly property real renderScale:Window.window.devicePixelRatio;readonly property real textureScale:Math.ceil(renderScale);x:20;y:20;width:180;height:180;radius:20;color:"#101117"
  clip:true;layer.enabled:popup.open
            layer.textureSize: Qt.size(Math.ceil(width * popupBackground.textureScale), Math.ceil(height * popupBackground.textureScale))
            layer.effect: MultiEffect {
                autoPaddingEnabled: false
                maskEnabled: true
                maskSource: popupClipMask
            }
  Flickable {
   id:scroll;anchors.fill:parent;contentHeight:400;clip:true
   Text {x:20;y:25;text:"Central de Controlo";font.family:"JetBrains Mono";font.pixelSize:14;renderType:Text.CurveRendering;color:"black";z:2}
   ControlIcon {x:120;y:50;width:18;height:18;source:"wifi.svg";tint:"black";z:2}
   Column {
    width:180;spacing:8
    Repeater {model:5;Rectangle {width:180;height:70;radius:18;color:"#ffffff"}}
   }
  }
 }
 TestCase {
  name:"RoundedScrollClip";when:windowShown
  function test_same_corner_contour_at_every_scroll_position() {
   fuzzyCompare(popupBackground.renderScale,2.0,0.001)
   console.log("SCALE_METRICS",JSON.stringify({dpr:Screen.devicePixelRatio,windowDpr:root.Window.window.devicePixelRatio,textureWidth:popupBackground.layer.textureSize.width,maskWidth:popupClipMask.layer.textureSize.width}))
   compare(popupBackground.layer.textureSize.width,Math.ceil(popupBackground.width*popupBackground.textureScale))
   compare(popupClipMask.layer.textureSize.width,Math.ceil(popupBackground.width*popupBackground.textureScale))
   var positions=[0,20,65,85,140]
   for(var n=0;n<positions.length;n++) {
    scroll.contentY=positions[n];wait(35)
    var frame=grabImage(root)
    var dpr=frame.width/root.width
    fuzzyCompare(dpr,2.0,0.01)
    function sample(x,y) {return frame.pixel(Math.floor(x*dpr),Math.floor(y*dpr))}
    frame.save(Qt.resolvedUrl("scroll-corners.png").toString().replace("file://",""))
    verify(sample(110,110)!==Qt.rgba(1,0,0,1), "Menu content must remain rendered")
    compare(sample(21,21),Qt.rgba(1,0,0,1))
    compare(sample(198,21),Qt.rgba(1,0,0,1))
    compare(sample(21,198),Qt.rgba(1,0,0,1))
    compare(sample(198,198),Qt.rgba(1,0,0,1))
    for(var delta=1;delta<18;delta+=4)
     fuzzyCompare(sample(20+delta,23).g,frame.pixel(frame.width-1-Math.floor((20+delta)*dpr),Math.floor(23*dpr)).g,0.06)
    if(n===1)frame.save(Qt.resolvedUrl("scroll-corners.png").toString().replace("file://",""))
   }
  }
 }
}
