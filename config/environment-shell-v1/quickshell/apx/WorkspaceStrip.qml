pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import Quickshell
import Quickshell.Wayland
import Quickshell.Hyprland
import "WorkspacePager.js" as WorkspacePager

Item {
    id: strip
    required property var workspaces
    required property var barWindow
    required property url wallpaper
    required property color surfaceColor
    required property color activeColor
    required property color mainColor
    required property color dimColor
    required property color borderColor
    property bool expanded: true
    signal toggleRequested()
    property bool grouped: false
    property bool menusOpen: false
    property int offset: 0
    property var previewTarget: null
    property bool previewOpen: false
    readonly property var page: WorkspacePager.page(workspaces, offset)
    readonly property var previewWorkspace: previewTarget ? previewTarget.modelData : null
    signal activated()
    property real reveal: expanded ? 1 : 0
    Behavior on reveal { NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
    implicitWidth: workspaceSymbol.width + labelsViewport.width
    implicitHeight: 32
    width: implicitWidth; height: implicitHeight

    onWorkspacesChanged: {
        if (offset >= workspaces.length || workspaces.length <= 5) offset = 0
        if (previewWorkspace && workspaces.indexOf(previewWorkspace) < 0) hidePreview()
    }
    onExpandedChanged: if (!expanded) hidePreview()
    onVisibleChanged: if (!visible) hidePreview()
    onMenusOpenChanged: if (menusOpen) hidePreview()

    function hidePreview() {
        previewDelay.stop()
        previewClose.stop()
        previewOpen = false
        previewTarget = null
    }
    function hoverButton(button, hovered) {
        if (hovered && !menusOpen) {
            previewClose.stop()
            previewTarget = button
            if (!previewOpen) previewDelay.restart()
            Hyprland.refreshToplevels()
        } else if (previewTarget === button) {
            previewDelay.stop()
            previewClose.restart()
        }
    }

    Timer {
        id: previewDelay
        interval: 250
        onTriggered: if (strip.visible && !strip.menusOpen && strip.previewTarget) strip.previewOpen = true
    }
    Timer {
        id: previewClose
        interval: 180
        onTriggered: if (!previewHover.hovered) strip.hidePreview()
    }

    BarButton {
        id: workspaceSymbol
        border.width: 0
        grouped: strip.grouped
        height: 32
        iconName: "square-stack"
        accessibleLabel: strip.expanded ? "Ocultar workspaces" : "Mostrar workspaces"
        onActivated: strip.toggleRequested()
    }

    // Keep delegates alive so labels retain their positions throughout reversal.
    Item {
        id: labelsViewport
        x: workspaceSymbol.width
        width: (labels.implicitWidth > 0 ? labels.implicitWidth + 4 : 0) * strip.reveal
        height: 32; clip: true
        opacity: strip.reveal
        enabled: strip.expanded
        Row {
            id: labels
            x: 4; height: 32; spacing: 4
            Repeater {
                model: strip.page
                delegate: BarButton {
                    id: workspaceButton
                    grouped: strip.grouped
                    required property var modelData
                    label: modelData.name
                    alternateLabel: label
                    alternateActive: modelData.focused
                    activeSurface: strip.activeColor
                    accentColor: strip.mainColor
                    textColor: strip.dimColor
                    Accessible.role: Accessible.Button
                    Accessible.name: "Workspace " + modelData.name + (modelData.focused ? ", atual" : "")
                    Component.onDestruction: if (strip.previewTarget === workspaceButton) strip.hidePreview()
                    HoverHandler {
                        onHoveredChanged: strip.hoverButton(workspaceButton, hovered)
                    }
                    onActivated: {
                        strip.hidePreview()
                        strip.activated()
                        modelData.activate()
                    }
                }
            }
            BarButton {
                id: nextWorkspaceButton
                grouped: strip.grouped
                visible: strip.workspaces.length > 5
                label: ""
                implicitWidth: 40
                iconName: "chevron-right"
                alternateLabel: label
                activeSurface: strip.activeColor
                accentColor: strip.mainColor
                textColor: strip.dimColor
                Accessible.role: Accessible.Button
                Accessible.name: "Mostrar os próximos workspaces"
                onActivated: {
                    strip.hidePreview()
                    strip.offset = WorkspacePager.nextOffset(strip.workspaces, strip.offset)
                }
            }

        }
    }

    // Keep the layer mapped, like the common menus, so hover does not remap
    // a surface under the pointer. It only accepts input inside the preview.
    PanelWindow {
        id: previewWindow
        screen: strip.barWindow.screen
        anchors { top: true; bottom: true; left: true; right: true }
        exclusionMode: ExclusionMode.Ignore
        exclusiveZone: 0
        color: "transparent"
        visible: strip.visible
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
        mask: Region { item: previewInput }

        Item {
            id: previewInput
            x: previewLoader.x
            y: previewLoader.y
            width: strip.previewOpen ? previewLoader.width : 0
            height: strip.previewOpen ? previewLoader.height : 0
        }
        HoverHandler {
            id: previewHover
            parent: previewInput
            onHoveredChanged: {
                if (hovered) previewClose.stop()
                else if (strip.previewOpen) previewClose.restart()
            }
        }
        Loader {
            id: previewLoader
            active: strip.previewOpen && strip.previewWorkspace !== null
            width: Math.min(340, previewWindow.width - 32)
            x: {
                var target = strip.previewTarget
                var left = target ? target.mapToItem(strip.barWindow.contentItem, 0, 0).x + strip.barWindow.margins.left : 16
                return Math.max(16, Math.min(left, previewWindow.width - width - 16))
            }
            y: Appearance.menuTop
            sourceComponent: WorkspacePreview {
                workspace: strip.previewWorkspace
                wallpaper: strip.wallpaper
                surfaceColor: strip.surfaceColor
                mainColor: strip.mainColor
                dimColor: strip.dimColor
                borderColor: strip.borderColor
                maxHeight: previewWindow.height - previewLoader.y - 16
            }
        }
    }
}
