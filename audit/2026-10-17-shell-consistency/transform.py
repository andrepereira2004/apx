from pathlib import Path
import re
REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
AUDIT=Path(__file__).resolve().parent
QML_NAMES=[p.name for p in (SOURCE/'quickshell/apx').glob('*.qml') if p.name not in ['DesktopActivity.qml','GhostLines.qml']]
RELATIVES=['quickshell/apx/'+n for n in QML_NAMES]+['rofi/config.rasi']
KEYS=['controlsWifiOpen','controlsBluetoothOpen','controlsAudioOpen','controlsMicrophoneOpen','controlsMoreOpen','controlsAppearanceOpen','controlsActivityKind','shortcutsOpen','powerConfirmOpen']

def once(s,a,b):
 assert s.count(a)==1,(a[:120],s.count(a));return s.replace(a,b,1)

def fonts(s):
 s=re.sub(r'font\.family: "[^"]+"', 'font.family: Appearance.fontFamily', s)
 # Body/action text shares a size; small details retain one secondary size.
 s=re.sub(r'font.pixelSize: (?:9|10)(?!\d)', 'font.pixelSize: Appearance.metaSize', s)
 s=re.sub(r'font.pixelSize: (?:11|12)(?!\d)', 'font.pixelSize: Appearance.bodySize', s)
 s=re.sub(r'(?<![\w.])pixelSize: (?:10|11|12)(?!\d)', 'pixelSize: Appearance.bodySize', s)
 # Calendar chevrons and numeric day glyphs also use the same actual font.
 s=re.sub(r'Text \{(?![^{}]*\bfont(?:\.family\s*:|\s*:))([^{}]*)\}',lambda m:'Text { font.family: Appearance.fontFamily;'+m[1]+'}',s)
 return s

def finish_shell(s):
 if 'id: panelMaterialFade' not in s:s=once(s, '            color: splitControls ? "transparent" : root.popupPanel', '            color: splitControls ? "transparent" : root.popupPanel\n            Behavior on color { ColorAnimation { id: panelMaterialFade; duration: 180; easing.type: Easing.OutCubic } }')
 if '// APX staged IPC navigation' not in s:
  s=once(s, '        function openControls(): void {\n            root.popupKeyboardRequested = true', '        function openControls(): void {\n            // APX staged IPC navigation: use the same page transition as pointer actions.\n            root.controlsWifiOpen = false; root.controlsBluetoothOpen = false\n            root.controlsAudioOpen = false; root.controlsMicrophoneOpen = false\n            root.controlsMoreOpen = false; root.controlsAppearanceOpen = false\n            root.controlsActivityKind = ""; root.shortcutsOpen = false\n            root.popupKeyboardRequested = true\n            if (popup.open && root.popupKind === "controls" && !root.popupClosing) return')
 if 'function visibleMenuFonts()' not in s:
  s=once(s, '    function renderedControlsAllClosed() {', '    function visibleMenuFonts() {\n        var fonts = []\n        function visit(item) {\n            if (!item || !item.visible || item.width <= 0 || item.height <= 0) return\n            if (item.font !== undefined && item.text !== undefined && String(item.text).length) {\n                var key = item.font.family + ":" + item.font.pixelSize\n                if (fonts.indexOf(key) < 0) fonts.push(key)\n            }\n            var children = item.children || []\n            for (var i = 0; i < children.length; ++i) visit(children[i])\n        }\n        visit(menuContent)\n        return fonts.sort()\n    }\n    function renderedControlsAllClosed() {')
  s=once(s, 'body_size: Appearance.bodySize, title_size: Appearance.titleSize,', 'body_size: Appearance.bodySize, title_size: Appearance.titleSize, visible_fonts: root.visibleMenuFonts(),')
 return s

def shell(s):
 if '// APX consistent shell v3' in s:return finish_shell(fonts(s))
 s=once(s,'    readonly property int menuTitleSize: 14','    // APX consistent shell v3\n    readonly property int menuTitleSize: Appearance.titleSize')
 s=re.sub(r'    property int menuBodySize: \d+','    readonly property int menuBodySize: Appearance.bodySize',s)
 s=re.sub(r'    property int menuSmallSize: \d+','    readonly property int menuSmallSize: Appearance.bodySize',s)
 s=re.sub(r'    property int menuMetaSize: \d+','    readonly property int menuMetaSize: Appearance.metaSize',s)
 s=once(s,'font.pixelSize: parent.title === "Environments" || parent.title === "Calendário" ? root.menuTitleSize + 1 : root.menuTitleSize','font.pixelSize: root.menuTitleSize')
 s=once(s,'property real settledY: root.popupKind === "media" ? root.islandOrigin.y : 65','property real settledY: Appearance.menuTop')
 # Shared background for the left group, with independent hit targets.
 anchor='''                id: leftActions
                anchors.left: parent.left'''
 s=once(s,anchor,'''                id: leftActions
                Rectangle {
                    parent: leftActions.parent
                    x: leftActions.x; y: leftActions.y; width: leftActions.width; height: leftActions.height
                    z: -1; radius: height / 2
                    color: Appearance.tintButtons ? Appearance.barSurface : "#ed15171f"
                    border.width: 1; border.color: "#304f566c"
                }
                anchors.left: parent.left''')
 s=once(s,'                    id: calendarButton\n','                    id: calendarButton\n                    grouped: true\n')
 s=once(s,'                Item { width: visible ? 16 : 0; height: 1; visible: !root.isHub }\n','')
 s=once(s,'                WorkspaceStrip {\n','                WorkspaceStrip {\n                    grouped: true\n')
 # Move the media/transient capsule into the existing right group.
 a=s.index('            MediaIsland {');b=s.index('\n            BarButton {',a);media=s[a:b]
 s=s[:a]+s[b:]
 media=media.replace('                anchors.right: rightActions.left\n                anchors.rightMargin: 12\n                anchors.verticalCenter: parent.verticalCenter\n','                grouped: true\n')
 media=media.replace('Math.max(0, rightActions.x - (environmentButton.x + environmentButton.width) - 36)','Math.max(0, rightActions.parent.width - (environmentButton.x + environmentButton.width) - rightActions.fixedWidth - 22)')
 media=media.replace('transientActive ? 300 : 220','transientActive ? 150 : 220')
 media=media.replace('availableWidth >= 110','availableWidth >= 90')
 s=once(s,'                id: rightActions\n','''                id: rightActions
                readonly property real fixedWidth: [modelStoreButton, microphoneButton, appsButton, filesButton, batteryButton, controlCenterButton].filter(function(item) { return item.visible }).reduce(function(total, item) { return total + item.width + rightActions.spacing }, 0)
'''+media+'\n')
 s=once(s,'                    visible: root.microphoneActive\n                    label: "Microfone"','                    id: microphoneButton\n                    grouped: true\n                    visible: root.microphoneActive\n                    label: "Microfone"')
 # Keep old control content during the outgoing phase. Only swap at opacity zero.
 a=s.index('    onMenuRouteChanged:');b=s.index('\n    property rect islandOrigin:',a)
 route='''    property var renderedControls: ({controlsWifiOpen: false, controlsBluetoothOpen: false, controlsAudioOpen: false, controlsMicrophoneOpen: false, controlsMoreOpen: false, controlsAppearanceOpen: false, controlsActivityKind: "", shortcutsOpen: false, powerConfirmOpen: false})
    function syncRenderedControls() {
        renderedControls = {'''+', '.join(k+': '+k for k in KEYS)+'''}
    }
    function renderedControlsAllClosed() {
        return !renderedControls.controlsWifiOpen && !renderedControls.controlsBluetoothOpen && !renderedControls.controlsAudioOpen && !renderedControls.controlsMicrophoneOpen && !String(renderedControls.controlsActivityKind || "").length
    }
    onMenuRouteChanged: Qt.callLater(function() {
        if (!popup.open || root.popupClosing || root.popupAnimationPending || root.islandProgress < .99) {
            root.syncRenderedControls()
            return
        }
        if (root.popupKind !== "controls") {
            root.syncRenderedControls()
            root.islandContentOpacity = 0
            islandContentAnimation.restart()
            return
        }
        islandContentAnimation.stop()
        controlPageAnimation.restart()
    })
    SequentialAnimation {
        id: controlPageAnimation
        NumberAnimation { target: root; property: "islandContentOpacity"; to: 0; duration: 90; easing.type: Easing.OutCubic }
        ScriptAction { script: { root.syncRenderedControls(); menuFlick.contentY = 0; Qt.callLater(function() { var items = root.genericMenuItems(); if (root.menuKeyboardNavigation && items.length) root.focusMenuItem(items[0]) }) } }
        NumberAnimation { target: root; property: "islandContentOpacity"; to: 1; duration: 220; easing.type: Easing.OutCubic }
    }
'''
 s=s[:a]+route+s[b:]
 s=once(s,'    function showPopup() {','    function showPopup() {\n        controlPageAnimation.stop()\n        syncRenderedControls()')
 s=once(s,'        popupClosing = true\n','        popupClosing = true\n        controlPageAnimation.stop()\n')
 # Only rendering reads use the delayed page. Actions/auth/focus still use real state.
 lines=s.splitlines()
 for i,line in enumerate(lines):
  if 'visible:' in line and any('root.'+k in line for k in KEYS):
   for k in KEYS:line=line.replace('root.'+k,'root.renderedControls.'+k)
  if 'visible:' in line:line=line.replace('root.controlsAllClosed()', 'root.renderedControlsAllClosed()')
  if 'title: root.popupKind === "media"' in line:
   for k in KEYS:line=line.replace('root.'+k,'root.renderedControls.'+k)
  lines[i]=line
 s='\n'.join(lines)+'\n'
 # Page sizing follows the staged content too; one geometry animation drives it.
 a=s.index('        property real menuHeight:');b=s.index('\n        color: "transparent"',a)
 part=s[a:b]
 for k in KEYS:part=part.replace('root.'+k,'root.renderedControls.'+k)
 part=part.replace('root.controlsAllClosed()', 'root.renderedControlsAllClosed()')
 part=part.replace('menuContent.implicitHeight + 20','menuContent.implicitHeight + (popupBackground.splitControls ? 0 : 20)')
 s=s[:a]+part+s[b:]
 a=s.index('            readonly property bool splitControls:');b=s.index('\n',a)
 part=s[a:b].replace('root.controlsAllClosed()', 'root.renderedControlsAllClosed()')
 for k in KEYS:part=part.replace('root.'+k,'root.renderedControls.'+k)
 s=s[:a]+part+s[b:]
 s=once(s,'? popup.menuHeight : menuContent.implicitHeight + 20)', '? popup.menuHeight : menuContent.implicitHeight + (splitControls ? 0 : 20))')
 s=once(s,'                x: 10; y: 10 + 8 * (1 - root.islandContentOpacity)\n                width: popupBackground.targetWidth - 20\n                height: popupBackground.settledHeight - 20', '''                x: popupBackground.splitControls ? 0 : 10
                y: (popupBackground.splitControls ? 0 : 10) + 6 * (1 - root.islandContentOpacity)
                width: popup.menuWidth - (popupBackground.splitControls ? 0 : 20)
                height: Math.max(0, popupBackground.height - (popupBackground.splitControls ? 0 : 20))''')
 # Hide outgoing content's displacement; move only the incoming page.
 s=s.replace('6 * (1 - root.islandContentOpacity)','(controlPageFadeOut.running ? 0 : 6 * (1 - root.islandContentOpacity))')
 s=once(s,'NumberAnimation { target: root; property: "islandContentOpacity"; to: 0; duration: 90;', 'NumberAnimation { id: controlPageFadeOut; target: root; property: "islandContentOpacity"; to: 0; duration: 90;')
 s=s.replace('enabled: !root.popupClosing && root.islandProgress > .8', 'enabled: !root.popupClosing && root.islandProgress > .8 && !controlPageAnimation.running')
 s=s.replace('root.popupKind === "controls" && compactDashboard.mediaTransitionRunning', 'root.popupKind === "controls" && root.renderedControlsAllClosed() && !root.renderedControls.controlsMoreOpen && compactDashboard.mediaTransitionRunning')
 s=once(s,'                                    files_active: root.filesFocused,','                                    panel_y: popupBackground.y, content_y: menuFlick.y, content_font: Appearance.fontFamily, body_size: Appearance.bodySize, title_size: Appearance.titleSize,\n                                    displayed_controls: root.renderedControls, page_transition: controlPageAnimation.running,\n                                    files_active: root.filesFocused,')
 # Raw chevrons in menu labels become standard icons.
 s=s.replace('label: "‹ Voltar aos controlos"', 'iconName: "chevron-left"; label: "Voltar aos controlos"')
 s=s.replace('label: "‹ Voltar às opções"', 'iconName: "chevron-left"; label: "Voltar às opções"')
 return finish_shell(fonts(s))

def transform(rel,s):
 if rel=='rofi/config.rasi':
  return s.replace('width: 184px;', 'width: 248px;').replace('width: 88px;', 'width: 120px;')
 if rel.endswith('/shell.qml'):return shell(s)
 if rel.endswith('/Appearance.qml') and 'readonly property string fontFamily:' not in s:
  s=once(s,'    id: appearance','''    id: appearance
    readonly property string fontFamily: "JetBrains Mono"
    readonly property int titleSize: 14
    readonly property int bodySize: 12
    readonly property int metaSize: 11
    readonly property int menuTop: 65''')
 if rel.endswith('/WorkspaceStrip.qml'):
  s=s.replace('y: strip.barWindow.implicitHeight + 6', 'y: Appearance.menuTop')
  s=s.replace('    property bool menusOpen: false','    property bool grouped: false\n    property bool menusOpen: false') if 'property bool grouped:' not in s else s
  if 'grouped: strip.grouped' not in s:s=s.replace('            id: workspaceButton\n','            id: workspaceButton\n            grouped: strip.grouped\n').replace('        id: nextWorkspaceButton\n','        id: nextWorkspaceButton\n        grouped: strip.grouped\n')
 if rel.endswith('/ControlDashboard.qml'):
  if 'id: dashboardHeader' not in s:
   s=once(s, '    Text { width: parent.width; text: "Central de Controlo"; color: "#e1e5f0"; font.family: "JetBrains Mono"; font.pixelSize: 13 }', '    Item {\n        id: dashboardHeader\n        width: parent.width; height: 30\n        Text { width: parent.width; height: 24; verticalAlignment: Text.AlignVCenter; text: "Central de Controlo"; color: "#e1e5f0"; font.family: "JetBrains Mono"; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }\n        Rectangle { width: parent.width; height: 1; anchors.bottom: parent.bottom; color: dashboard.controller.controlButtonOutline }\n    }')
 if rel.endswith('/MediaIsland.qml'):
  if 'property bool grouped:' not in s:s=s.replace('    signal activated()','    signal activated()\n    property bool grouped: false')
  s=s.replace('color: pointer.containsMouse ?', 'color: grouped && !pointer.containsMouse ? "transparent" : pointer.containsMouse ?')
  s=s.replace('border.width: 1;', 'border.width: grouped ? 0 : 1;')
  s=s.replace('transientTitle + (transientDetail.length ? " · " + transientDetail : "")', '(transientProgress >= 0 && transientDetail.length ? transientDetail : transientTitle)')
  s=s.replace('Accessible.name: transientActive ? displayTitle', 'Accessible.name: transientActive ? transientTitle + " " + transientDetail')
 if rel.endswith('/IconLabel.qml'):s=s.replace('property int pixelSize: 12','property int pixelSize: Appearance.bodySize')
 if not rel.endswith(('/BarButton.qml','/MediaIsland.qml')):s=s.replace('font.pixelSize: 13','font.pixelSize: Appearance.bodySize')
 if rel.endswith('/PersonalizationPanel.qml'):s=s.replace('Caption { text: "Cor e superfícies"; color: "#e1e5f0"; font.pixelSize: Appearance.bodySize', 'Caption { text: "Cor e superfícies"; color: "#e1e5f0"; font.pixelSize: Appearance.titleSize')
 return fonts(s)
