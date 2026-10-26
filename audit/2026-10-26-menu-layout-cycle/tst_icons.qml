import QtQuick
import QtTest
Item {
 id:root;width:10;height:10
 Component {id:factory;ControlIcon{width:14;height:14;tint:"#ff3366"}}
 TestCase {
  name:"OriginalSvgLoading";when:windowShown
  function test_all_icons() {
   var names=["battery-full", "battery-medium", "battery-warning", "battery-charging", "battery", "monitor", "battery-low", "pickaxe", "chevron-right", "chevron-left", "calendar-days", "hexagon", "swords", "zap", "ghost", "grid-2x2", "volume-2", "mic", "sun", "volume-x", "mic-off", "keyboard", "hard-drive", "wifi", "bluetooth-off", "bluetooth", "wifi-off", "wifi-high", "wifi-low", "lock-keyhole", "power", "log-out", "folder", "rotate-cw", "terminal", "calculator", "panels-top-left", "camera", "touchpad", "refresh-cw", "touchpad-off", "shield-check", "search", "settings", "mouse", "circle-alert", "globe", "plane", "usb", "x", "check", "bell", "play", "video", "skip-forward", "pause", "skip-back", "music", "audio-lines", "square-stack", "satellite-dish", "paintbrush", "package", "package-open", "box", "folder-open", "calendar-search", "copy-plus", "cpu", "trash-2", "undo-2", "bring-to-front", "book-a", "book-open", "layout-panel-left", "layout-dashboard", "layout-grid", "list", "mouse-off", "leaf", "scale", "cross", "gpu", "gamepad-2", "joystick", "trophy", "dice-5", "target", "rocket", "puzzle", "medal", "graph-hub", "graph-star", "camera-off", "plane-off", "mouse-pointer-2", "arrow-up-down"]
   for(var i=0;i<names.length;i++) {
    var item=factory.createObject(root,{source:Qt.resolvedUrl("icons/lucide/"+names[i]+".svg")})
    verify(item.originalLucide,names[i])
    var image=item.children[0]
    tryCompare(image,"status",Image.Ready)
    compare(image.sourceSize.width,28)
    compare(image.width,14)
    compare(image.color.toString(),"#ff3366")
    item.visible = false
    compare(image.status, Image.Ready)
    verify(image.source.toString().length > 0, names[i])
    item.visible = true
    compare(image.status, Image.Ready)
    item.destroy()
   }
  }
 }
}