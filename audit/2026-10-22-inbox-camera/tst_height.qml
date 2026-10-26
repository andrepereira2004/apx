import QtQuick
import QtTest
Item {
 id:root;width:340;height:440
    function menuHeightForCompleteActions(limit) {
        var topPadding = popupBackground.contentInset
        var bottomPadding = popupBackground.contentBottomInset
        var viewport = Math.max(0, limit - topPadding - bottomPadding)
        var scroll = menuFlick.contentY
        var bottom = scroll + viewport
        var top = scroll + (menuFlick.headerInset || 0)
        var surfaces = []
        function visit(item) {
            if (!item.visible || item.continuousScrollContent === true) return
            var surface = item.navigationTarget
                || (item.menuViewportGuard !== undefined ? item.parent : (item.activeFocusOnTab ? item : null))
            if (surface && surface.visible && surfaces.indexOf(surface) < 0
                    && surface.height > 0 && surface.height <= viewport && surface.width > 0)
                surfaces.push(surface)
            var children = item.children || []
            for (var i = 0; i < children.length; ++i) visit(children[i])
        }
        visit(menuContent)
        var rects = surfaces.map(function(surface) {
            var point = surface.mapToItem(menuFlick.contentItem, 0, 0)
            return {x: point.x, y: point.y, width: surface.width, height: surface.height}
        })
        var partial = false
        var lastBottom = -Infinity
        for (var i = 0; i < rects.length; ++i) {
            var rect = rects[i]
            // Nested controls belong to their containing card's complete outline.
            var nested = false
            for (var j = 0; j < rects.length; ++j) {
                var outer = rects[j]
                if (i !== j && outer.x <= rect.x && outer.y <= rect.y
                        && outer.x + outer.width >= rect.x + rect.width
                        && outer.y + outer.height >= rect.y + rect.height
                        && (outer.width > rect.width || outer.height > rect.height)) { nested = true; break }
            }
            if (nested) continue
            var end = rect.y + rect.height
            if (rect.y < bottom - 0.5 && end > bottom + 0.5) partial = true
            if (rect.y >= top - 0.5 && end <= bottom + 0.5) lastBottom = Math.max(lastBottom, end)
        }
        if (!partial || !isFinite(lastBottom)) return limit
        return Math.min(limit, topPadding + lastBottom - scroll + bottomPadding)
    }


 Rectangle {
  id:popupBackground
  property real contentInset:10
  property real contentBottomInset:12
  property real viewportHeight:400
  width:340;height:root.menuHeightForCompleteActions(viewportHeight);clip:true
  Flickable {
   id:menuFlick;x:10;y:10;width:320
   height:popupBackground.viewportHeight-22
   contentHeight:menuContent.implicitHeight;clip:true
   property real headerInset:0
   Column {
    id:menuContent;width:320;spacing:8
    Item {height:27;width:320}
    Repeater {
     id:rows;model:12
     Rectangle {
      width:320;height:56;activeFocusOnTab:true
      property bool continuousScrollContent:false
      Rectangle {x:10;y:5;width:32;height:32;activeFocusOnTab:true}
     }
    }
   }
  }
 }
 TestCase {
  name:'WholeCardHeight';when:windowShown
  function init() {menuFlick.contentY=0;menuFlick.headerInset=0;popupBackground.viewportHeight=400;wait(5)}
  function test_frame_ends_after_last_whole_card() {
   compare(rows.itemAt(4).y+56,347)
   compare(popupBackground.height,369)
   compare(menuFlick.height,378)
   verify(rows.itemAt(5).y+56>378)
  }
  function test_repeated_layout_does_not_collapse_the_scroll_viewport() {
   for(var i=0;i<20;i++) {wait(1);compare(popupBackground.height,369);compare(menuFlick.height,378)}
  }
  function test_scrolling_fits_to_the_new_last_card_and_returns() {
   menuFlick.contentY=64
   compare(popupBackground.height,369)
   menuFlick.contentY=35
   compare(popupBackground.height,400)
   menuFlick.contentY=0;compare(popupBackground.height,369)
  }
  function test_end_of_content_preserves_normal_padding_and_bounds() {
   menuFlick.contentY=menuFlick.contentHeight-menuFlick.height
   compare(popupBackground.height,400)
   compare(menuFlick.contentY,menuFlick.contentHeight-menuFlick.height)
  }
  function test_z_notification_stream_does_not_resize_while_scrolling() {
   for(var i=0;i<rows.count;i++)rows.itemAt(i).continuousScrollContent=true
   for(var y=0;y<280;y+=14){menuFlick.contentY=y;compare(popupBackground.height,400)}
   for(var j=0;j<rows.count;j++)rows.itemAt(j).continuousScrollContent=false
  }
  function test_nested_buttons_do_not_define_the_outer_card_cutoff() {
   // The last nested button fits, but its enclosing card is clipped.
   menuFlick.contentY=14
   compare(popupBackground.height,355)
   compare(menuFlick.height,378)
  }
 }
}
