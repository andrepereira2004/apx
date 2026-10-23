from pathlib import Path
p=Path('config/environment-shell-v1/quickshell/apx/shell.qml')
s=p.read_text().replace('import QtQuick.Window','import QtCore\nimport QtQuick.Window',1)
s=s.replace('    property string environmentEditDescription: ""','''    property string environmentEditDescription: ""
    property string environmentEditIcon: "box"
    property string environmentPendingIconKey: ""
    property string environmentPendingIcon: "box"
    readonly property var environmentIconChoices: ["box", "monitor", "terminal", "book-open", "swords", "shield-check", "globe", "folder", "cpu", "music", "camera", "paintbrush", "pickaxe", "hexagon", "zap", "satellite-dish"]
    Settings {
        id: environmentIcons
        fileName: "/home/apx/.config/apx-environment-icons.ini"
        category: "Environments"
        property string choices: "{}"
    }
    function environmentIconKey(item) {
        return String(item.name) + ":" + String(item.generation)
    }
    function environmentIcon(item) {
        try {
            var icon = JSON.parse(environmentIcons.choices)[environmentIconKey(item)]
            if (environmentIconChoices.indexOf(icon) >= 0) return icon
        } catch (error) {}
        return "box"
    }
    function storeEnvironmentIcon(key, icon) {
        var choices = {}
        try { choices = JSON.parse(environmentIcons.choices) } catch (error) {}
        choices[key] = icon
        environmentIcons.choices = JSON.stringify(choices)
        environmentIcons.sync()
    }''',1)
s=s.replace('environmentEditDescription = String(selected.description || "")','environmentEditDescription = String(selected.description || "")\n        environmentEditIcon = environmentIcon(selected)',1)
s=s.replace('        environmentMetadataBusy = true\n        environmentMetadataProcess.command', '''        environmentPendingIconKey = environmentIconKey(environmentSelection())
        environmentPendingIcon = environmentEditIcon
        environmentMetadataBusy = true
        environmentMetadataProcess.command''',1)
a=s.index('    function handleEnvironmentEditKey(');b=s.index('\n    function ',a+10)
part=s[a:b].replace('(environmentEditFocusIndex + 3) % 4','(environmentEditFocusIndex + 4) % 5').replace('(environmentEditFocusIndex + 1) % 4','(environmentEditFocusIndex + 1) % 5')
part=part.replace('        else if (event.key === Qt.Key_Return', '''        else if (environmentEditFocusIndex === 3 && (event.key === Qt.Key_Left || event.key === Qt.Key_Right)) {
            var choices = environmentIconChoices
            environmentEditIcon = choices[(choices.indexOf(environmentEditIcon) + (event.key === Qt.Key_Left ? choices.length - 1 : 1)) % choices.length]
        }
        else if (event.key === Qt.Key_Return''',1)
part=part.replace('            else saveEnvironmentMetadata()', '            else if (environmentEditFocusIndex === 3) { environmentEditFocusIndex = 4 }\n            else saveEnvironmentMetadata()').replace('environmentEditFocusIndex === 3)', 'environmentEditFocusIndex >= 3)')
s=s[:a]+part+s[b:]
s=s.replace('            if (exitCode === 0) {\n                root.environmentEditOpen = false','            if (exitCode === 0) {\n                root.storeEnvironmentIcon(root.environmentPendingIconKey, root.environmentPendingIcon)\n                root.environmentEditOpen = false',1)
s=s.replace('width: parent.width; height: 62; radius: 9','width: parent.width; height: 46; radius: 12',1)
s=s.replace('                        border.width: 1\n                        border.color: keyboardFocused ? root.cyan : root.controlButtonOutline','                        border.width: keyboardFocused ? 1 : 0\n                        border.color: root.cyan',1)
s=s.replace('Rectangle { anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter; width: 9; height: 9; radius: 5; color: root.textMain }','LucideIcon { anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter; width: 18; height: 18; name: root.isHub ? "layout-dashboard" : "box" }',1)
s=s.replace('anchors.leftMargin: 34; anchors.right: activeEnvironmentBadge','anchors.leftMargin: 42; anchors.right: activeEnvironmentBadge',1)
s=s.replace('font.pixelSize: root.menuTitleSize; font.weight: Font.DemiBold; elide: Text.ElideRight }\n                            Text { visible: root.isHub; width: parent.width; text: "Centro de gestão e segurança"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize; elide: Text.ElideRight }','font.pixelSize: root.menuBodySize; font.weight: Font.Normal; elide: Text.ElideRight }',1)
s=s.replace('width: parent ? parent.width : 400; height: 59; radius: 9','width: parent ? parent.width : 400; height: 44; radius: 12',1)
s=s.replace('border.width: 1; border.color: keyboardFocused ? root.cyan : root.controlButtonOutline\n                                Rectangle { anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter; width: 8; height: 8; radius: 4; color: root.environmentIsOpenable(modelData) ? (parent.selected ? root.textMain : "#5d7b82") : "#79505a" }','border.width: keyboardFocused ? 1 : 0; border.color: root.cyan\n                                LucideIcon { anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter; width: 18; height: 18; name: root.environmentIcon(modelData) }',1)
a=s.index('                                    Row {\n                                        width: parent.width; height: 16; spacing: 6',s.index('id: hubEnvironmentCard'));b=s.index('\n                                }\n                                Text { id: environmentRowStatus',a)
s=s[:a]+s[b:]
s=s.replace('anchors.leftMargin: 32; anchors.right: environmentRowStatus','anchors.leftMargin: 42; anchors.right: environmentRowStatus',1)
a=s.index('                        MenuButton {\n                            width: parent.width; height: 42\n                            label: root.environmentMetadataBusy')
s=s[:a]+'''                        Text { text: "Ícone"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                        Grid {
                            width: parent.width; columns: 8; spacing: 5
                            Repeater {
                                model: root.environmentIconChoices
                                delegate: MenuButton {
                                    required property string modelData
                                    width: (parent.width - 35) / 8; height: 36
                                    iconName: modelData
                                    label: ""
                                    Accessible.name: "Ícone " + modelData
                                    selected: root.environmentEditIcon === modelData
                                    keyboardFocused: root.environmentEditFocusIndex === 3 && selected
                                    enabled: !root.environmentMetadataBusy
                                    onActivated: {
                                        root.environmentEditIcon = modelData
                                        root.environmentEditFocusIndex = 3
                                        environmentMenu.forceActiveFocus()
                                    }
                                }
                            }
                        }
'''+s[a:]
s=s.replace('keyboardFocused: root.environmentEditFocusIndex === 3\n','keyboardFocused: root.environmentEditFocusIndex === 4\n',1)
p.write_text(s)
