import QtQuick
import QtQuick.Window
import QtQuick.Effects
import QtTest
Rectangle {
 id:root;width:700;height:260;color:"#101117"
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
  id:popupBackground;readonly property real renderScale:Window.window.devicePixelRatio;readonly property real textureScale:Math.ceil(renderScale);x:360;y:20;width:300;height:220;radius:20;color:"#101117"
  clip:true;layer.enabled:popup.open
            layer.textureSize: Qt.size(Math.ceil(width * popupBackground.textureScale), Math.ceil(height * popupBackground.textureScale))
            layer.effect: MultiEffect {
                autoPaddingEnabled: false
                maskEnabled: true
                maskSource: popupClipMask
            }
  Text {renderType:Text.CurveRendering;x:20;y:30;text:"Central de Controlo";font.family:"JetBrains Mono";font.pixelSize:14;color:"white"}
  Text {renderType:Text.CurveRendering;x:20;y:65;text:"Ligações · Wi-Fi · Bluetooth";font.family:"JetBrains Mono";font.pixelSize:12;color:"#c8ccdc"}
  Text {renderType:Text.CurveRendering;x:20;y:100;text:"Brilho 50% · Bateria 28%";font.family:"JetBrains Mono";font.pixelSize:12;color:"#c8ccdc"}
  ControlIcon {id:sampleIcon;x:20;y:145;width:16;height:16;source:"wifi.svg";tint:"white"}
  ControlIcon {x:60;y:145;width:18;height:18;source:"volume-2.svg";tint:"white"}
 }
 Rectangle {
  x:20;y:20;width:300;height:220;radius:20;color:"#101117"
  Text {x:20;y:30;text:"Central de Controlo";font.family:"JetBrains Mono";font.pixelSize:14;color:"white"}
  Text {x:20;y:65;text:"Ligações · Wi-Fi · Bluetooth";font.family:"JetBrains Mono";font.pixelSize:12;color:"#c8ccdc"}
  Text {x:20;y:100;text:"Brilho 50% · Bateria 28%";font.family:"JetBrains Mono";font.pixelSize:12;color:"#c8ccdc"}
  ControlIcon {x:20;y:145;width:18;height:18;source:"wifi.svg";tint:"white"}
  ControlIcon {x:60;y:145;width:18;height:18;source:"volume-2.svg";tint:"white"}
 }
 TestCase {
  name:"MenuSharpness";when:windowShown
  function test_capture() {
   wait(150)
   var frame=grabImage(root)
   frame.save(Qt.resolvedUrl("sharpness.png").toString().replace("file://",""))
   var dpr=frame.width/root.width, err=0, nativeEnergy=0, maskEnergy=0, count=0
   for(var y=Math.floor(50*dpr);y<Math.floor(153*dpr);y++) {
    for(var x=Math.floor(40*dpr);x<Math.floor(300*dpr);x++) {
     var a=frame.pixel(x,y).r,b=frame.pixel(x+Math.round(340*dpr),y).r
     var da=a-frame.pixel(x+1,y).r
     var db=b-frame.pixel(x+Math.round(340*dpr)+1,y).r
     err+=Math.abs(a-b);nativeEnergy+=da*da;maskEnergy+=db*db;count++
    }
   }
   verify(maskEnergy/nativeEnergy>0.90, "Text must preserve at least 90% of reference edge contrast")
   console.log("SHARPNESS_METRICS",JSON.stringify({meanError:err/count,nativeEnergy:nativeEnergy,maskedEnergy:maskEnergy,ratio:maskEnergy/nativeEnergy}))
  }
 }
}
