from pathlib import Path
p=Path('config/environment-shell-v1/quickshell/apx/shell.qml');s=p.read_text()
s=s.replace('text: "Palavra-passe"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }\n                                }\n                                Text { visible: wifiDomainField', 'text: "Introduz a palavra-passe"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }\n                                }\n                                Text { visible: wifiDomainField',1).replace('text: "Certificado CA no Host · domínio obrigatório"','text: "Verifica o domínio e o certificado da organização."',1)
# The existing verified connect operation is shared by open/saved networks.
s=s.replace('''        id: hostActionProcess
        onExited: hostStatusProcess.running = true''','''        id: hostActionProcess
        stderr: StdioCollector { onStreamFinished: if (command[1] === "wifi-connect" && text.trim()) root.wifiMessage = text.trim() }
        onExited: (code, status) => {
            if (command[1] === "wifi-connect" && root.wifiPasswordVisible) {
                if (code === 0) { root.cancelWifiPassword(); root.wifiMessage = "Ligação efetuada." }
                else if (!root.wifiMessage.length || root.wifiMessage.indexOf("A ligar") === 0) root.wifiMessage = "Não foi possível estabelecer a ligação."
            }
            hostStatusProcess.running = true
        }''',1)
s=s.replace('    function stepDisplayBrightness(delta) {','''    property int displayBrightnessBeforeDim: 70
    function toggleDisplayDim() {
        if (displayBrightnessProcess.running) return
        if (displayBrightness > 5) {
            displayBrightnessBeforeDim = displayBrightness
            commitDisplayBrightness(5)
        } else commitDisplayBrightness(Math.max(6, displayBrightnessBeforeDim))
    }

    function stepDisplayBrightness(delta) {''',1)
s=s.replace('ControlTile { width: implicitWidth; height: 28; color: "transparent"; showCaption: true; iconName: root.volumeMuted ? "volume-x" : "volume-2"; caption: "Som"; onActivated: root.openControlSection("audio") }','ControlTile { width: parent.width; height: 48; quiet: true; showCaption: true; iconName: root.volumeMuted ? "volume-x" : "volume-2"; caption: "Som"; selected: !root.volumeMuted; iconActionEnabled: true; iconActionAvailable: !localActionProcess.running; iconActionLabel: root.volumeMuted ? "Reativar som" : "Silenciar som"; onIconActivated: root.toggleVolumeMute(); onActivated: root.openControlSection("audio") }',1)
s=s.replace('IconLabel { iconName: "sun"; text: "Brilho do ecrã"; color: root.textMain; pixelSize: root.menuBodySize }','ControlTile { width: parent.width; height: 48; quiet: true; showCaption: true; iconName: "sun"; caption: "Brilho do ecrã"; selected: root.displayBrightness > 5; iconActionEnabled: true; iconActionAvailable: !displayBrightnessProcess.running; iconActionLabel: root.displayBrightness > 5 ? "Reduzir brilho" : "Restaurar brilho"; onIconActivated: root.toggleDisplayDim(); onActivated: root.toggleDisplayDim() }',1)
s=s.replace('ControlTile { width: parent.width; height: 42; showCaption: true; iconName: root.microphoneMuted ? "mic-off" : "mic"; caption: "Microfone"; onActivated:', 'ControlTile { width: parent.width; height: 48; quiet: true; showCaption: true; iconName: root.microphoneMuted ? "mic-off" : "mic"; caption: "Microfone"; selected: !root.microphoneMuted; iconActionEnabled: true; iconActionAvailable: !localActionProcess.running; iconActionLabel: root.microphoneMuted ? "Reativar microfone" : "Silenciar microfone"; onIconActivated: root.toggleMicrophoneMute(); onActivated:',1)
s=s.replace('ControlTile { width: parent.width; height: 42; showCaption: true; iconName: "keyboard"; caption: "Iluminação do teclado"; selected: root.keyboardBrightness > 0; onActivated:', 'ControlTile { width: parent.width; height: 48; quiet: true; showCaption: true; iconName: "keyboard"; caption: "Iluminação do teclado"; selected: root.keyboardBrightness > 0; iconActionEnabled: true; iconActionAvailable: !keyboardBrightnessProcess.running; iconActionLabel: "Alterar iluminação do teclado"; onIconActivated: root.cycleKeyboardBrightness(); onActivated:',1)
for kind,method,icon in [('volume','Volume','volume-2'),('microphone','Microphone','mic')]:
    # Put the mute action into the slider header and remove its duplicate button.
    pos=s.index('                                id: '+kind+'Slider') if kind=='volume' else s.index('                                id: microphoneSlider')
    start=s.rfind('                        Rectangle {',0,pos)
    section=s[start:pos]
    section=section.replace('height: 68;','height: 80;',1)
    i=section.index('                            Text {')
    section=section[:i]+'''                            RadioIconButton {
                                x: 6; y: 3
                                iconName: root.KINDMuted ? "OFF" : "ON"
                                powered: !root.KINDMuted; busy: localActionProcess.running
                                actionLabel: root.KINDMuted ? "Reativar LABEL" : "Silenciar LABEL"
                                onActivated: root.toggleMETHODMute()
                            }
'''.replace('KIND',kind).replace('OFF','volume-x' if kind=='volume' else 'mic-off').replace('ON',icon).replace('LABEL','som' if kind=='volume' else 'microfone').replace('METHOD',method)+section[i:]
    section=section.replace('anchors.leftMargin: 16; anchors.top:', 'anchors.leftMargin: 50; anchors.top:',1).replace('anchors.topMargin: 8','anchors.topMargin: 12')
    s=s[:start]+section+s[pos:]
    marker='                            color: '+kind+'MuteMouse.containsMouse'
    pos=s.index(marker);start=s.rfind('                        Rectangle {',0,pos)
    level=0;end=None
    for j in range(s.index('{',start),len(s)):
        if s[j]=='{':level+=1
        elif s[j]=='}':
            level-=1
            if level==0:end=j+1;break
    s=s[:start]+s[end:]
p.write_text(s)
