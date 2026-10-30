pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import Quickshell
import Quickshell.Wayland

Rectangle {
    id: preview
    required property var workspace
    required property url wallpaper
    required property color surfaceColor
    required property color mainColor
    required property color dimColor
    required property color borderColor
    required property real maxHeight
    readonly property var windows: workspace ? workspace.toplevels.values : []
    readonly property var monitor: workspace && workspace.monitor ? workspace.monitor.lastIpcObject : ({})
    readonly property real monitorWidth: Math.max(1, (monitor.width || 1920) / (monitor.scale || 1))
    readonly property real monitorHeight: Math.max(1, (monitor.height || 1080) / (monitor.scale || 1))
    implicitHeight: Math.min(maxHeight, content.implicitHeight + 24)
    color: surfaceColor
    radius: 10
    border.width: 1
    border.color: borderColor

    readonly property var desktopApplications: DesktopEntries.applications.values

    function appName(window) {
        // Observe the index becoming ready or changing while the preview is open.
        var applications = desktopApplications
        var appId = window.wayland ? window.wayland.appId : ""
        var id = appId || (window.lastIpcObject || {}).class || ""
        if (id === "apx-host-console-v1") return "APX Terminal"
        var entry = id ? (DesktopEntries.byId(id) || DesktopEntries.heuristicLookup(id)) : null
        if (!entry && id.indexOf(".") >= 0)
            entry = DesktopEntries.byId(id.split(".").pop())
        return entry ? entry.name : (id || "Aplicação")
    }

    Column {
        id: content
        x: 12; y: 12
        width: parent.width - 24
        spacing: 10
        Text {
            width: parent.width
            text: "Workspace " + (preview.workspace ? preview.workspace.name : "")
            color: preview.mainColor
            font.family: Appearance.fontFamily
            font.pixelSize: 14
            font.weight: Font.DemiBold
        }
        Rectangle {
            id: desktop
            width: parent.width
            height: width * preview.monitorHeight / preview.monitorWidth
            color: "#0a1014"
            clip: true
            radius: 5
            Image {
                anchors.fill: parent
                source: preview.wallpaper
                fillMode: Image.PreserveAspectCrop
                asynchronous: true
            }
            Repeater {
                model: preview.windows
                delegate: Rectangle {
                    id: thumbnail
                    required property var modelData
                    readonly property var geometry: modelData.lastIpcObject || ({})
                    readonly property real factor: desktop.width / preview.monitorWidth
                    x: ((geometry.at || [0, 0])[0] - (preview.monitor.x || 0)) * factor
                    y: ((geometry.at || [0, 0])[1] - (preview.monitor.y || 0)) * factor
                    width: Math.max(12, (geometry.size || [preview.monitorWidth, preview.monitorHeight])[0] * factor)
                    height: Math.max(12, (geometry.size || [preview.monitorWidth, preview.monitorHeight])[1] * factor)
                    z: modelData.activated ? 1 : 0
                    color: "#17232a"
                    border.width: 1
                    border.color: preview.borderColor
                    clip: true
                    ScreencopyView {
                        id: capture
                        anchors.fill: parent
                        anchors.margins: 1
                        captureSource: thumbnail.modelData.wayland
                        live: false
                    }
                    Text {
                        anchors.centerIn: parent
                        width: parent.width - 8
                        visible: !capture.hasContent
                        text: preview.appName(thumbnail.modelData)
                        elide: Text.ElideRight
                        color: preview.mainColor
                        font.family: Appearance.fontFamily
                        font.pixelSize: Appearance.metaSize
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }
        }
        Text {
            visible: preview.windows.length === 0
            text: "Sem aplicações abertas"
            color: preview.dimColor
            font.family: Appearance.fontFamily
            font.pixelSize: Appearance.bodySize
        }
        ScrollView {
            width: parent.width
            height: Math.min(appList.implicitHeight, Math.max(38, Math.min(228, preview.maxHeight - desktop.height - 70)))
            visible: preview.windows.length > 0
            clip: true
            contentWidth: availableWidth
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            Column {
                id: appList
                width: parent.width
                spacing: 6
                Repeater {
                    model: preview.windows
                    delegate: Column {
                        required property var modelData
                        width: appList.width
                        spacing: 2
                        Text {
                            width: parent.width
                            text: preview.appName(parent.modelData)
                            elide: Text.ElideRight
                            color: preview.mainColor
                            font.family: Appearance.fontFamily
                            font.pixelSize: Appearance.bodySize
                        }
                        Text {
                            width: parent.width
                            text: parent.modelData.title
                            elide: Text.ElideRight
                            color: preview.dimColor
                            font.family: Appearance.fontFamily
                            font.pixelSize: Appearance.bodySize
                        }
                    }
                }
            }
        }
    }
}
