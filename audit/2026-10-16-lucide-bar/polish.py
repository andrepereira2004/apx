from pathlib import Path

def polish(s):
    s=s.replace('IconLabel { iconName: root.microphoneMuted ? "mic-off" : "mic";\n                                anchors.centerIn: parent','IconLabel { iconName: root.microphoneMuted ? "mic-off" : "mic"; stacked: true\n                                anchors.centerIn: parent')
    s=s.replace('IconLabel { iconName: "keyboard";\n                                anchors.centerIn: parent','IconLabel { iconName: "keyboard"; stacked: true\n                                anchors.centerIn: parent')
    # Optional icons for menu actions, preserving keyboard focus and activation.
    anchor='        id: menuButton\n        property string label: ""'
    s=s.replace(anchor,anchor+'\n        property string iconName: ""')
    start=s.index('    component MenuButton: Rectangle');end=s.index('    component ',start+10)
    block=s[start:end]
    block=block.replace('        Text {\n', '''        LucideIcon {
            visible: menuButton.iconName.length > 0
            name: menuButton.iconName; tint: root.textMain
            width: 17; height: 17
            anchors.left: parent.left; anchors.leftMargin: 11
            anchors.verticalCenter: parent.verticalCenter
        }
        Text {
''',1).replace('anchors.leftMargin: 11','anchors.leftMargin: menuButton.iconName.length ? 36 : 11',1)
    # Keep the icon at the padding edge; apply the inset to the text instead.
    block=block.replace('anchors.leftMargin: menuButton.iconName.length ? 36 : 11','anchors.leftMargin: 11',1)
    idx=block.index('        Text {');block=block[:idx]+block[idx:].replace('anchors.leftMargin: 11','anchors.leftMargin: menuButton.iconName.length ? 36 : 11',1)
    s=s[:start]+block+s[end:]
    s=s.replace('label: "Mais opções  ›"','iconName: "settings"; label: "Mais opções"')
    s=s.replace('label: "Lista de atalhos  ›"','iconName: "keyboard"; label: "Lista de atalhos"')
    return s

if __name__=='__main__':
 p=Path('config/environment-shell-v1/quickshell/apx/shell.qml');p.write_text(polish(p.read_text()))
