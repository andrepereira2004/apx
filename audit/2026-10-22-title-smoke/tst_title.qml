import QtQuick
import QtTest
Item {
 id:root; width:340;height:240
 property string popupKind:"controls"
 property bool calendarEditor:false
 property real islandProgress:1
 property color popupPanel:"#101117"
 property color textMain:"white"
 property color controlButtonOutline:"gray"
 property int menuTitleSize:14
 property var popup:({open:true})
 QtObject {id:appearance;property string fontFamily:"sans-serif";property int menuTitleInset:8}
    component MenuHeader: Item {
        id: menuHeader
        opacity: popupBackground.scrollingHeader === menuHeader
            ? 1 - stickyMenuHeader.revealProgress : 1
        property string title: ""
        width: parent.width
        height: 30
        Text { renderType: Text.CurveRendering;
            anchors.left: parent.left
            anchors.leftMargin: appearance.menuTitleInset
            anchors.right: parent.right
            height: 24
            verticalAlignment: Text.AlignVCenter
            text: parent.title
            color: root.textMain
            font.family: appearance.fontFamily
            font.pixelSize: root.menuTitleSize
            font.weight: Font.DemiBold
        }
        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 1
            color: root.controlButtonOutline
        }
    }


    function ensureMenuItemVisible(item) {
        if (!item || !item.visible || menuFlick.height <= 0) return
        menuFlick.stopWheel()
        var target = item.navigationTarget || (item.menuViewportGuard !== undefined ? item.parent : item)
        var point = target.mapToItem(menuFlick.contentItem, 0, 0)
        var maximum = Math.max(0, menuFlick.contentHeight - menuFlick.height)
        var destination = menuFlick.contentY
        var topInset = menuFlick.headerInset || 0
        var availableHeight = menuFlick.height - topInset
        var margin = Math.min(8, Math.max(0, (availableHeight - target.height) / 2))
        // A tall section should reveal its beginning instead of jumping to its end.
        if (target.height > availableHeight)
            destination = point.y - topInset
        else if (point.y < destination + topInset + margin) destination = point.y - topInset - margin
        else if (point.y + target.height > destination + menuFlick.height - margin)
            destination = point.y + target.height - menuFlick.height + margin
        menuFlick.contentY = Math.max(0, Math.min(maximum, destination))
    }

    function menuButtonFits(surface) {
        var topInset = menuFlick.headerInset || 0
        var scroll = menuFlick.contentY + topInset
        var viewport = menuFlick.height - topInset
        var layoutHeight = menuFlick.contentHeight
        var localY = surface.y
        if (!popup.open || root.islandProgress < 1 || !surface.visible
                || surface.height > viewport) return true
        var point = surface.mapToItem(menuFlick.contentItem, 0, 0)
        // Let rows pass continuously beneath the title gradient; keep the bottom-card rule.
        return point.y + surface.height <= scroll + viewport + 0.5
    }


 Item {id:calendarMenuHeader;visible:false;property string title:"Calendário"}
 Item {id:calendarEditorHeader;visible:false;property string title:"Novo evento"}
 Rectangle {
  id:popupBackground;width:340;height:240;radius:20
  property real contentInset:10
            readonly property Item scrollingHeader: root.popupKind === "calendar"
                ? (root.calendarEditor ? calendarEditorHeader : calendarMenuHeader) : scrollingMenuHeader
            readonly property bool headerScrolledOut: scrollingHeader && scrollingHeader.visible
                && menuFlick.contentY >= scrollingHeader.mapToItem(menuFlick.contentItem, 0, 0).y + scrollingHeader.height

            Rectangle {
                id: stickyMenuHeader
                x: 1
                y: 1
                width: Math.max(0, popupBackground.width - 2)
                height: popupBackground.contentInset + 34
                clip: false
                z: 2
                property real revealProgress: popup.open && popupBackground.headerScrolledOut ? 1 : 0
                Behavior on revealProgress {
                    id: titleRevealBehavior
                    enabled: popup.open
                    NumberAnimation {
                        duration: titleRevealBehavior.targetValue > 0 ? 420 : 240
                        easing.type: titleRevealBehavior.targetValue > 0 ? Easing.InOutSine : Easing.InOutQuad
                    }
                }
                visible: popup.open && (popupBackground.headerScrolledOut || revealProgress > 0)
                // Keep the backdrop steady on entrance; animate only the text.
                readonly property color backdropColor: root.popupPanel
                readonly property real backdropStrength: popupBackground.headerScrolledOut ? 1 : revealProgress
                function smoke(alpha) {
                    return Qt.rgba(backdropColor.r, backdropColor.g, backdropColor.b, alpha * backdropStrength)
                }
                color: "transparent"
                opacity: menuFlick.opacity
                Rectangle {
                    id: stickyTitleBackdrop
                    width: parent.width
                    height: parent.height + 18
                    radius: Math.max(0, popupBackground.radius - 1)
                    gradient: Gradient {
                        orientation: Gradient.Vertical
                        GradientStop { position: 0; color: stickyMenuHeader.smoke(1) }
                        GradientStop { position: Math.min(0.25, 8 / stickyTitleBackdrop.height); color: stickyMenuHeader.smoke(1) }
                        GradientStop { position: 0.75; color: stickyMenuHeader.smoke(0.75) }
                        GradientStop { position: 1; color: stickyMenuHeader.smoke(0) }
                    }
                }
                // The title owns clicks; wheel events continue to the scrolling content.
                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.AllButtons
                    onWheel: event => event.accepted = false
                }
                Text { renderType: Text.CurveRendering;
                    id: stickyTitleText
                    opacity: stickyMenuHeader.revealProgress
                    anchors.fill: parent
                    anchors.topMargin: Math.max(0, popupBackground.contentInset - 1)
                    anchors.leftMargin: popupBackground.contentInset + appearance.menuTitleInset
                    anchors.rightMargin: popupBackground.contentInset
                    anchors.bottomMargin: 5
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    text: popupBackground.scrollingHeader ? popupBackground.scrollingHeader.title : ""
                    color: root.textMain
                    font.family: appearance.fontFamily
                    font.pixelSize: root.menuTitleSize
                    font.weight: Font.DemiBold
                    elide: Text.ElideRight
                }
            }


  Item {
   id:menuScrollClip;x:10;y:10;width:320;height:220;clip:true
  Flickable {
   id:menuFlick;x:0;y:0;width:320;height:220;contentHeight:900;clip:true
   property real headerInset:stickyMenuHeader.visible ? stickyMenuHeader.y+stickyMenuHeader.height-popupBackground.contentInset : 0
   function stopWheel() {cancelFlick()}
   Column {
    width:320;spacing:5
    MenuHeader {id:scrollingMenuHeader;title:"Central de Controlo"}
    Repeater {id:rows;model:12;Rectangle {id:row; width:320;height:56; color:"#1b1d26"; opacity:root.menuButtonFits(row) ? 1 : 0}}
   }
  }
 }
 }
 TestCase {
  name:"StickyTitle";when:windowShown
  function init() {menuFlick.contentY=0;wait(380)}
  function test_content_remains_under_the_title() {
   menuFlick.contentY=50;wait(500)
   compare(menuScrollClip.y,10);compare(menuFlick.y,0)
   compare(menuScrollClip.height,220);compare(menuFlick.headerInset,35)
   verify(menuScrollClip.clip)
  }
  function test_vertical_smoke_is_75_percent_opaque_at_three_quarters() {
   menuFlick.contentY=50;wait(500)
   compare(stickyMenuHeader.x,1);compare(stickyMenuHeader.y,1)
   compare(stickyMenuHeader.width,popupBackground.width-2)
   compare(stickyTitleBackdrop.radius,popupBackground.radius-1)
   var stops=stickyTitleBackdrop.gradient.stops
   compare(stickyTitleBackdrop.gradient.orientation,Gradient.Vertical)
   compare(stops.length,4)
   compare(stops[0].position,0);compare(stops[0].color.a,1)
   fuzzyCompare(stops[1].position*stickyTitleBackdrop.height,8,0.01);compare(stops[1].color.a,1)
   compare(stops[2].position,0.75);fuzzyCompare(stops[2].color.a,0.75,0.01)
   compare(stops[3].position,1);compare(stops[3].color.a,0)
  }
  function test_partial_rows_do_not_disappear_under_the_title() {
   for(var scroll=30;scroll<95;scroll+=3){
    menuFlick.contentY=scroll;wait(1)
    compare(rows.itemAt(0).opacity,1)
   }
   compare(rows.itemAt(1).opacity,1)
   // Existing bottom-card rule still applies beyond the viewport.
   compare(rows.itemAt(8).opacity,0)
  }
  function test_title_animation_and_return_remain_continuous() {
   menuFlick.contentY=50;wait(100)
   verify(stickyMenuHeader.revealProgress>0 && stickyMenuHeader.revealProgress<1)
   fuzzyCompare(stickyMenuHeader.backdropStrength,1,0.01)
   menuFlick.contentY=0;wait(30);verify(stickyMenuHeader.visible)
   menuFlick.contentY=50;wait(500);compare(stickyMenuHeader.revealProgress,1)
   menuFlick.contentY=0;wait(380);verify(!stickyMenuHeader.visible)
   compare(scrollingMenuHeader.opacity,1)
  }
  function test_keyboard_reveal_keeps_actions_below_title() {
   menuFlick.contentY=90
   root.ensureMenuItemVisible(rows.itemAt(1))
   var y=rows.itemAt(1).mapToItem(menuFlick.contentItem,0,0).y-menuFlick.contentY
   verify(y>=menuFlick.headerInset)
   root.ensureMenuItemVisible(rows.itemAt(0));compare(menuFlick.contentY,0)
  }
  function test_z_render_preview() {
   menuFlick.contentY=45;wait(500)
   var done=false
   root.grabToImage(function(result){result.saveToFile("/home/apx/.cache/apx-title-smoke-preview.png");done=true})
   tryVerify(function(){return done},1000)
  }
 }
}
