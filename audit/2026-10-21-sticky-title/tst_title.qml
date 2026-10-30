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
 QtObject {id:appearance;property string fontFamily:"sans-serif"}
    component MenuHeader: Item {
        id: menuHeader
        opacity: popupBackground.scrollingHeader === menuHeader
            ? 1 - stickyMenuHeader.revealProgress : 1
        property string title: ""
        width: parent.width
        height: 30
        Text { renderType: Text.CurveRendering;
            anchors.left: parent.left
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
        return point.y >= scroll - 0.5 && point.y + surface.height <= scroll + viewport + 0.5
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
                x: 0
                y: 0
                width: popupBackground.width
                height: popupBackground.contentInset + 35
                clip: true
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
                readonly property color backdropColor: Qt.darker(root.popupPanel, 1.18)
                readonly property color backdropFill: Qt.rgba(backdropColor.r, backdropColor.g, backdropColor.b,
                    0.65 * (popupBackground.headerScrolledOut ? 1 : revealProgress))
                color: "transparent"
                opacity: menuFlick.opacity
                Rectangle {
                    id: stickyTitleBackdrop
                    width: parent.width
                    height: parent.height + popupBackground.radius
                    radius: popupBackground.radius
                    gradient: Gradient {
                        GradientStop { position: 0; color: stickyMenuHeader.backdropFill }
                        GradientStop {
                            position: Math.max(0, stickyMenuHeader.height - 10) / stickyTitleBackdrop.height
                            color: stickyMenuHeader.backdropFill
                        }
                        GradientStop {
                            position: stickyMenuHeader.height / stickyTitleBackdrop.height
                            color: Qt.rgba(stickyMenuHeader.backdropColor.r, stickyMenuHeader.backdropColor.g,
                                           stickyMenuHeader.backdropColor.b, 0)
                        }
                        GradientStop { position: 1; color: "transparent" }
                    }
                }
                Text { renderType: Text.CurveRendering;
                    id: stickyTitleText
                    opacity: stickyMenuHeader.revealProgress
                    anchors.fill: parent
                    anchors.topMargin: popupBackground.contentInset
                    anchors.leftMargin: popupBackground.contentInset
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
   id:menuScrollClip;x:10;y:10+menuFlick.headerInset;width:320;height:220-menuFlick.headerInset;clip:true
  Flickable {
   id:menuFlick;x:0;y:-headerInset;width:320;height:220;contentHeight:900;clip:true
   property real headerInset:stickyMenuHeader.visible ? stickyMenuHeader.height-popupBackground.contentInset : 0
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
  function test_all_content_is_clipped_below_title_without_moving_scroll_geometry() {
   compare(menuScrollClip.y+menuFlick.y,10)
   menuFlick.contentY=50;wait(500)
   compare(menuScrollClip.y,45)
   compare(menuScrollClip.height,185)
   compare(menuScrollClip.y+menuFlick.y,10)
   verify(menuScrollClip.clip)
   menuFlick.contentY=0;wait(380)
   compare(menuScrollClip.y,10)
   compare(menuScrollClip.height,220)
  }
  function test_entrance_keeps_steady_dark_backdrop_while_text_animates() {
   menuFlick.contentY=50;wait(260)
   verify(stickyMenuHeader.revealProgress>0.4 && stickyMenuHeader.revealProgress<0.95)
   fuzzyCompare(stickyMenuHeader.backdropFill.a,0.65,0.01)
   verify(stickyMenuHeader.backdropFill.r<root.popupPanel.r)
   wait(240);compare(stickyMenuHeader.revealProgress,1)
  }
  function test_title_animates_in_and_out_and_reverses_cleanly() {
   menuFlick.contentY=50;wait(60)
   verify(stickyMenuHeader.revealProgress>0 && stickyMenuHeader.revealProgress<1)
   fuzzyCompare(stickyMenuHeader.backdropFill.a,0.65,0.01)
   fuzzyCompare(scrollingMenuHeader.opacity+stickyMenuHeader.revealProgress,1,0.001)
   verify(stickyMenuHeader.visible)
   menuFlick.contentY=0;wait(30)
   verify(stickyMenuHeader.visible)
   menuFlick.contentY=50;wait(500)
   compare(stickyMenuHeader.revealProgress,1)
   menuFlick.contentY=0;wait(60)
   verify(stickyMenuHeader.revealProgress>0 && stickyMenuHeader.revealProgress<1)
   wait(320);compare(stickyMenuHeader.revealProgress,0);verify(!stickyMenuHeader.visible)
  }
  function test_original_title_returns_as_the_backdrop_dissolves() {
   menuFlick.contentY=50;wait(500)
   fuzzyCompare(stickyMenuHeader.backdropFill.a,0.65,0.01)
   menuFlick.contentY=0
   compare(scrollingMenuHeader.opacity,0)
   wait(80)
   verify(scrollingMenuHeader.opacity>0 && scrollingMenuHeader.opacity<1)
   verify(stickyMenuHeader.backdropFill.a>0 && stickyMenuHeader.backdropFill.a<1)
   fuzzyCompare(stickyMenuHeader.backdropFill.a,stickyMenuHeader.revealProgress*0.65,0.01)
   fuzzyCompare(scrollingMenuHeader.opacity+stickyMenuHeader.revealProgress,1,0.001)
   wait(300);compare(scrollingMenuHeader.opacity,1);verify(!stickyMenuHeader.visible)
  }
  function test_translucent_backdrop_covers_full_top_width_and_margin() {
   menuFlick.contentY=50;wait(500)
   compare(stickyMenuHeader.x,0);compare(stickyMenuHeader.y,0)
   compare(stickyMenuHeader.width,popupBackground.width)
   compare(stickyMenuHeader.height,45);compare(menuFlick.headerInset,35)
   verify(stickyMenuHeader.backdropFill.a>0 && stickyMenuHeader.backdropFill.a<1)
   compare(stickyTitleBackdrop.radius,popupBackground.radius)
   verify(stickyTitleBackdrop.height>stickyMenuHeader.height)
   var stops=stickyTitleBackdrop.gradient.stops
   fuzzyCompare(stops[0].color.a,0.65,0.01)
   fuzzyCompare(stops[1].position*stickyTitleBackdrop.height,35,0.01)
   fuzzyCompare(stops[2].position*stickyTitleBackdrop.height,45,0.01)
   compare(stops[2].color.a,0)
  }
  function test_opaque_rows_do_not_slide_under_the_translucent_title() {
   menuFlick.contentY=50;wait(500)
   compare(rows.itemAt(0).opacity,0)
   compare(rows.itemAt(1).opacity,1)
   fuzzyCompare(stickyMenuHeader.backdropFill.a,0.65,0.01)
   menuFlick.contentY=0;wait(380)
   compare(rows.itemAt(0).opacity,1)
  }
  function test_original_title_stays_left_until_it_has_scrolled_out() {
   verify(!stickyMenuHeader.visible)
   compare(scrollingMenuHeader.children[0].horizontalAlignment,Text.AlignLeft)
   menuFlick.contentY=20;verify(!stickyMenuHeader.visible)
   menuFlick.contentY=30;verify(stickyMenuHeader.visible)
   compare(stickyTitleText.horizontalAlignment,Text.AlignHCenter)
   compare(stickyTitleText.text,"Central de Controlo")
  }
  function test_pinned_position_is_constant_and_restores_on_return() {
   menuFlick.contentY=50;var y=stickyMenuHeader.y
   menuFlick.contentY=200;compare(stickyMenuHeader.y,y)
   compare(menuFlick.headerInset,35)
   menuFlick.contentY=0;wait(380);verify(!stickyMenuHeader.visible)
   compare(menuFlick.headerInset,0)
  }
  function test_arrow_reveal_does_not_put_the_card_under_the_title() {
   menuFlick.contentY=90
   root.ensureMenuItemVisible(rows.itemAt(1))
   var y=rows.itemAt(1).mapToItem(menuFlick.contentItem,0,0).y-menuFlick.contentY
   verify(y>=menuFlick.headerInset)
   root.ensureMenuItemVisible(rows.itemAt(0))
   compare(menuFlick.contentY,0);wait(380);verify(!stickyMenuHeader.visible)
  }
 }
}
