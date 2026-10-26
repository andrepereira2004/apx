pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

Column {
    id: panel
    property var wallpapers: []
    property string section: ""
    property string scope: "environment"
    readonly property bool colorInputActive: customColor.activeFocus
    readonly property var selectedStyle: scope === "global" ? (Appearance.state.global_style || fallbackStyle) : (Appearance.state.style || Appearance.state.global_style || fallbackStyle)
    readonly property var fallbackStyle: ({ color: "#d9dcea", icons: true, buttons: false, windows: false })
    readonly property var swatches: ["#d9dcea", "#67d9ed", "#8bb8ff", "#b69cff", "#eb9bcd", "#efad72", "#8cdaa2", "#f2d87c"]
    onSelectedStyleChanged: if (customColor && !customColor.activeFocus) customColor.text = selectedStyle.color
    Component.onCompleted: customColor.text = selectedStyle.color
    signal navigation()
    onSectionChanged: navigation()
    signal back()
    signal chooseImage()
    spacing: 8

    function updateStyle(key, value) {
        var style = Object.assign({}, selectedStyle)
        style[key] = value
        style.icons = true; style.buttons = false; style.windows = false
        Appearance.setStyle(scope, style)
    }
    function applyColor() {
        if (/^#[0-9a-fA-F]{6}$/.test(customColor.text)) updateStyle("color", customColor.text)
        else Appearance.error = "Use uma cor no formato #RRGGBB."
    }

    component Action: Rectangle {
        id: action
        property string text: ""
        property string iconName: ""
        property bool selected: false
        signal clicked()
        implicitHeight: 44
        width: parent ? parent.width : 300
        radius: 14
        activeFocusOnTab: true
        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                action.clicked(); event.accepted = true
            }
        }
        opacity: enabled ? 1 : .45
        color: selected ? "#353a4a" : "#1b1d26"
        border.width: action.activeFocus || selected ? 1 : 0
        border.color: "#9da8c2"
        IconLabel { anchors.left: parent.left; anchors.leftMargin: 14; anchors.verticalCenter: parent.verticalCenter; text: action.text; iconName: action.iconName; pixelSize: Appearance.bodySize; iconSize: 16 }
        Accessible.role: Accessible.Button
        Accessible.name: text
        Accessible.checkable: false
        BounceMouseArea { id: actionMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: action.clicked() }
    }
    component Caption: Text { renderType: Text.CurveRendering;
        width: parent ? parent.width : 300
        color: "#b5bdd0"
        font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
        wrapMode: Text.WordWrap
    }

    Action { text: panel.section.length ? "Voltar à personalização" : "Voltar às opções"; iconName: "chevron-left"; onClicked: { if (panel.section.length) panel.section = ""; else panel.back() } }
    Column {
        width: parent.width; spacing: 8; visible: !panel.section.length
        Action { text: "Cor dos ícones"; iconName: "paintbrush"; onClicked: panel.section = "color" }
        Action { text: "Transparência"; iconName: "square-stack"; onClicked: panel.section = "opacity" }
        Action { text: "Fundo do ecrã"; iconName: "folder"; onClicked: panel.section = "wallpaper" }
    }
    Column {
        width: parent.width; spacing: 8; visible: panel.section === "color"
    Caption { text: "Cor dos ícones"; color: "#e1e5f0"; font.pixelSize: Appearance.titleSize }
    Row {
        width: parent.width; spacing: 6
        Action { width: (parent.width - 6) / 2; text: "Global"; selected: panel.scope === "global"; onClicked: panel.scope = "global" }
        Action { width: (parent.width - 6) / 2; text: "Este Environment"; selected: panel.scope === "environment"; onClicked: panel.scope = "environment" }
    }
    Caption {
        visible: false
        text: panel.scope === "global" ? "Aplica-se aos Environments que seguem a personalização global."
              : (Appearance.state.style ? "Este Environment tem uma personalização própria." : "Este Environment segue a personalização global.")
    }
    Grid {
        width: parent.width; columns: 4; columnSpacing: 6; rowSpacing: 6
        Repeater {
            model: panel.swatches
            Rectangle {
                required property string modelData
                width: (panel.width - 18) / 4; height: 27; radius: 6
                color: modelData
                border.width: panel.selectedStyle.color.toLowerCase() === modelData ? 3 : 1
                border.color: "#ffffff"
                Accessible.role: Accessible.Button
                Accessible.name: "Cor " + modelData
                BounceMouseArea { anchors.fill: parent; enabled: !Appearance.busy; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: panel.updateStyle("color", modelData) }
            }
        }
    }
    Row {
        width: parent.width; spacing: 6; height: 36
        Rectangle {
            width: parent.width - 100; height: 36; radius: 6; color: "#202431"
            border.width: 1; border.color: customColor.activeFocus ? "#b5c8ef" : "#414654"
            TextInput {
                id: customColor
                anchors.fill: parent; anchors.margins: 8
                text: "#d9dcea"
                color: "#e1e5f0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
                maximumLength: 7; selectByMouse: true; activeFocusOnTab: true
                Accessible.name: "Cor personalizada, formato hexadecimal"
                onAccepted: panel.applyColor()
                Keys.onPressed: function(event) {
                    if (event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab) event.accepted = false
                }
            }
        }
        Action { width: 94; text: "Aplicar"; enabled: !Appearance.busy; onClicked: panel.applyColor() }
    }
    Action {
        visible: panel.scope === "environment"
        height: visible ? implicitHeight : 0
        text: "Seguir personalização global"; iconName: "globe"
        enabled: !Appearance.busy && !!Appearance.state.style
        onClicked: Appearance.change("environment-style", "inherit")
    }
    }
    Column {
        width: parent.width; spacing: 8; visible: panel.section === "opacity"
    Caption { text: "Transparência"; color: "#e1e5f0"; font.pixelSize: Appearance.titleSize }
    Repeater {
        model: [{key: "bar", label: "Barra"}, {key: "menus", label: "Menus"}, {key: "terminal", label: "Terminal"}, {key: "files", label: "Gestor de ficheiros"}, {key: "rofi", label: "Aplicações"}]
        Column {
            id: opacityRow
            required property var modelData
            width: panel.width; spacing: 2
            Row {
                width: parent.width
                Text { renderType: Text.CurveRendering; width: parent.width - 48; text: opacityRow.modelData.label; color: "#e1e5f0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize }
                Text { renderType: Text.CurveRendering; width: 48; horizontalAlignment: Text.AlignRight; text: Math.round(opacitySlider.value) + "%"; color: "#e1e5f0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize }
            }
            ControlSlider {
                id: opacitySlider
                width: parent.width; height: 36; from: 0; to: 100; stepSize: 1
                activeFocusOnTab: true
                Accessible.name: "Opacidade: " + opacityRow.modelData.label
                Binding { target: opacitySlider; property: "value"; value: Appearance.opacityPercent(opacityRow.modelData.key); when: !opacitySlider.pressed }
                onMoved: Appearance.setOpacity(opacityRow.modelData.key, value)
                onPressedChanged: if (!pressed) Appearance.setOpacity(opacityRow.modelData.key, value)
            }
        }
    }
    }
    Column {
        width: parent.width; spacing: 8; visible: panel.section === "wallpaper"
    Caption { text: "Fundo do ecrã"; color: "#e1e5f0"; font.pixelSize: Appearance.bodySize }
    Row {
        width: parent.width; spacing: 6
        Repeater {
            model: panel.wallpapers
            Rectangle {
                required property string modelData
                required property int index
                width: (panel.width - 12) / 3; height: 54; radius: 6
                color: "#202431"
                Image { anchors.fill: parent; anchors.margins: 3; source: modelData; fillMode: Image.PreserveAspectCrop }
                border.width: Appearance.wallpaper === modelData ? 2 : 1; border.color: "#bac6e3"
                Accessible.role: Accessible.Button
                Accessible.name: "Wallpaper " + (index + 1)
                BounceMouseArea { anchors.fill: parent; enabled: !Appearance.busy; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: Appearance.change("wallpaper", decodeURIComponent(modelData.replace("file://", ""))) }
            }
        }
    }
    Action { text: Appearance.busy ? "A guardar…" : "Escolher imagem…"; iconName: "folder"; enabled: !Appearance.busy; onClicked: panel.chooseImage() }
    Action { text: "Voltar à rotação automática"; iconName: "rotate-cw"; enabled: !Appearance.busy && Appearance.wallpaper.length > 0; onClicked: Appearance.change("wallpaper", "default") }
    }
    Caption { visible: Appearance.error.length > 0 || !!Appearance.state.warning; text: Appearance.error || Appearance.state.warning || ""; color: "#ffa8b7" }
}
