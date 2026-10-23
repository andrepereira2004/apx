from pathlib import Path
p=Path('config/environment-shell-v1/quickshell/apx/shell.qml');s=p.read_text()
for kind,icon,title in [('mouse','mouse','rato'),('trackpad','touchpad','trackpad')]:
 needle=f'                        IconLabel {{ anchors.left: parent.left; anchors.leftMargin: 12; anchors.top: parent.top; anchors.topMargin: 8; text: "Sensibilidade do {title}";'
 a=s.rfind('                    Rectangle {',0,s.index(needle));end=s.index(f'                    Text {{ visible: root.{kind}SensitivityError',a)
 block=s[a:end].replace('height: 72; radius: 11','height: 56; radius: 14').replace('border.width: 1; border.color: root.controlButtonOutline','border.width: 0; border.color: root.controlButtonOutline')
 start=block.index('                        IconLabel {');e=block.index('                        Text {',start)
 block=block[:start]+f'''                        RadioIconButton {{
                            x: 8; anchors.verticalCenter: parent.verticalCenter
                            iconName: "{icon}"; powered: true
                            actionLabel: "Ajustar sensibilidade do {title}"
                            busy: {kind}SensitivityProcess.running
                            onActivated: {kind}SensitivitySlider.forceActiveFocus(Qt.TabFocusReason)
                        }}
''' +block[e:]
 block=block.replace('Text { anchors.right: parent.right; anchors.rightMargin: 12; anchors.top: parent.top; anchors.topMargin: 8;',f'Text {{ id: {kind}SensitivityPercent; width: 46; horizontalAlignment: Text.AlignRight; anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter;').replace('anchors.left: parent.left; anchors.leftMargin: 12; anchors.right: parent.right; anchors.rightMargin: 12',f'anchors.left: parent.left; anchors.leftMargin: 54; anchors.right: {kind}SensitivityPercent.left; anchors.rightMargin: 8').replace('anchors.bottom: parent.bottom; anchors.bottomMargin: 3','anchors.verticalCenter: parent.verticalCenter')
 if kind=='mouse':block=block.replace('ControlSlider {','MenuSlider {').replace('onMoved: if (!pressed) root.setMouseSensitivity(value)','wheelEnabled: false\n                            onKeyboardValueChanged: nextValue => root.setMouseSensitivity(nextValue)')
 s=s[:a]+block+s[end:]
p.write_text(s)
