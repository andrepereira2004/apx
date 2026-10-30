import QtQuick
import QtTest
Item {
 id: root; width:1280; height:720
 property real islandProgress:0
 property rect islandOrigin:Qt.rect(1100,8,72,32)
 property int widthChanges:0
 property var appearance: ({menuTop:65,menuMaxHeight:400})
 property var popup: ({height:720})
 Rectangle {
  id:popupBackground
  property real targetWidth:340
  property real contentInset:10
  property real contentBottomInset:12
  readonly property real targetHeight: Math.min(
                Math.max(0, popup.height - root.appearance.menuTop - 10),
                root.appearance.menuMaxHeight,
                menuContent.implicitHeight + contentInset + contentBottomInset)
  width:root.islandOrigin.width+(targetWidth-root.islandOrigin.width)*root.islandProgress
  height:root.islandOrigin.height+(targetHeight-root.islandOrigin.height)*root.islandProgress
  clip:true
  Flickable {
   id:menuFlick; width: Math.max(0, popupBackground.targetWidth - popupBackground.contentInset * 2); height:parent.height
   contentWidth:width;contentHeight:menuContent.implicitHeight
   onWidthChanged:root.widthChanges++
   Column {
    id:menuContent; width:parent.width
    Rectangle {id:extraContent;width:parent.width;height:0}
    Text {width:parent.width;wrapMode:Text.WordWrap;text:'Long text in a menu must keep the same wrapping throughout the reveal without forcing a different height on every frame.'}
   }
  }
 }
 NumberAnimation {id:opening;target:root;property:'islandProgress';to:1;duration:300;easing.type:Easing.OutCubic}
 TestCase {
  name:'StableMenuLayout';when:windowShown
  function test_tall_content_is_capped_and_scrollable() {
   extraContent.height=2000;wait(30)
   compare(popupBackground.targetHeight,400)
   root.islandProgress=1;wait(30)
   verify(menuFlick.contentHeight>menuFlick.height)
   menuFlick.contentY=150;compare(menuFlick.contentY,150)
   extraContent.height=0;menuFlick.contentY=0;root.islandProgress=0;wait(30)
  }
  function test_reveal_does_not_reflow() {
   wait(50)
   var expectedHeight=popupBackground.targetHeight
   var expectedWidth=menuFlick.width
   root.widthChanges=0
   opening.start()
   for(var i=0;i<24;i++) {
    wait(16)
    compare(menuFlick.width,expectedWidth)
    compare(popupBackground.targetHeight,expectedHeight)
   }
   compare(root.widthChanges,0)
   compare(root.islandProgress,1)
   compare(menuFlick.width,popupBackground.width-20)
   // A real destination resize must still update the content and wrapped height.
   popupBackground.targetWidth=260;wait(30)
   compare(menuFlick.width,240)
   verify(popupBackground.targetHeight>=expectedHeight)
  }
 }
}
