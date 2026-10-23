import QtQuick

ControlIcon {
    property string name: ""
    implicitWidth: 18
    implicitHeight: 18
    source: name.length ? Qt.resolvedUrl("icons/lucide/" + name + ".svg") : ""
    tint: Appearance.iconColor
}
