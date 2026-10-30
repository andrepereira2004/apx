from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
b=ROOT/'config/environment-shell-v1/quickshell/apx'
p=b/'ControlDashboard.qml';s=p.read_text();a=s.index('    ActivityPanel { width: parent.width; kind: "media"');z=s.index('    Grid {',a);section=s[a:z];media=section[:section.index('    Row {')];sliders=section[section.index('    Row {'):];s=s[:a]+s[z:];a=s.index('    Rectangle {\n        width: dashboard.width; height: notifications.')
new='''    Rectangle {
        width: dashboard.width; height: playback.implicitHeight + 20; radius: 18
        visible: playback.entries.length > 0
        color: dashboard.controller.popupPanel
        border.width: 1; border.color: dashboard.controller.shellBorder
        ActivityPanel { id: playback; x: 10; y: 10; width: parent.width - 20; kind: "media"; embedded: true }
    }
    Rectangle {
        width: dashboard.width; height: levels.implicitHeight + 20; radius: 18
        color: dashboard.controller.popupPanel
        border.width: 1; border.color: dashboard.controller.shellBorder
        Column {
            id: levels
            x: 10; y: 10; width: parent.width - 20
'''+sliders+'''        }
    }
''';s=s[:a]+new+s[a:];p.write_text(s)
p=b/'shell.qml';s=p.read_text().replace('root.popupKind === "controls" && root.controlsActivityKind === "media"','(root.popupKind === "media" || (root.popupKind === "controls" && root.controlsAllClosed()))');a=s.index('            MediaIsland {');z=s.index('\n            BarButton {',a);part=s[a:z];k=part.index('                onActivated: {');part=part[:k]+'''                onActivated: {
                    DesktopActivity.refresh()
                    root.togglePopup("media", mediaIsland, true)
                }
            }
''';s=s[:a]+part+s[z:];s=s.replace('(root.popupKind === "battery" ? 340 : 300)', '(root.popupKind === "battery" || root.popupKind === "media" ? 340 : 300)');s=s.replace(': (root.popupKind === "model" ? 370', ': (root.popupKind === "media" ? Math.min(popup.height - 74, menuContent.implicitHeight + 20) : root.popupKind === "model" ? 370');s=s.replace('title: root.popupKind === "battery" ?', 'title: root.popupKind === "media" ? "Reprodução" : root.popupKind === "battery" ?');a=s.index('                Column {\n                    width: parent.width; spacing: 10; visible: root.popupKind === "model"')
new='''                Column {
                    id: mediaMenu
                    width: parent.width; spacing: 10
                    visible: root.popupKind === "media"
                    ActivityPanel { width: parent.width; kind: "media"; showBack: false }
                    Row {
                        width: parent.width; spacing: 8; height: 36
                        LucideIcon { width: 20; height: 20; anchors.verticalCenter: parent.verticalCenter; name: root.volumeMuted ? "volume-x" : "volume-2" }
                        ControlSlider {
                            id: mediaVolume
                            width: parent.width - 28; height: 36
                            from: 0; to: 100; stepSize: 1; activeFocusOnTab: true
                            Accessible.name: "Volume de reprodução"
                            onMoved: { root.previewVolume(value); if (!pressed) root.commitVolume(value) }
                            onPressedChanged: if (!pressed) root.commitVolume(value)
                            Binding { target: mediaVolume; property: "value"; value: root.volumeMuted ? 0 : root.volumeValue; when: !mediaVolume.pressed }
                        }
                    }
                }

''';s=s[:a]+new+s[a:];p.write_text(s)
p=b/'ActivityPanel.qml';s=p.read_text().replace('    property bool embedded: false','    property bool embedded: false\n    property bool showBack: !embedded').replace('visible: !panel.embedded;','visible: panel.showBack;');p.write_text(s)
