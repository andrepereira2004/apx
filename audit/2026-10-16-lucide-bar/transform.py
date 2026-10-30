import re

def shell(s):
    assert 'readonly property string batteryIconName' not in s
    font='''    FontLoader { source: "file:///home/apx/.local/share/fonts/jetbrains-mono/JetBrainsMono-Regular.ttf" }
    FontLoader { source: "file:///home/apx/.local/share/fonts/jetbrains-mono/JetBrainsMono-Bold.ttf" }
'''
    s=s.replace('    // Register the trial UI font',font+'\n    // Register the trial UI font',1)
    s=s.replace('font.family: "Selawik"','font.family: "JetBrains Mono"')
    s=s.replace('property color panel: "#d90a1014"','property color panel: "#b3262939"').replace('property color popupPanel: "#d90a1014"','property color popupPanel: "#ed242736"')
    s=s.replace('property color shellBorder: "#26343a"','property color shellBorder: "#485064"')
    s=s.replace('property color textMain: "#eceef0"','property color textMain: "#d9dcea"').replace('property color textDim: "#9ba3ac"','property color textDim: "#a4abc0"')
    s=s.replace('controlButtonSurface: "#191d22"','controlButtonSurface: "#303445"').replace('controlButtonHover: "#272c33"','controlButtonHover: "#41475b"').replace('controlButtonActive: "#30353b"','controlButtonActive: "#454d64"').replace('controlButtonOutline: "#343a41"','controlButtonOutline: "#50586d"')
    s=s.replace('isHub ? "HUB" : String(environmentIdentity.display_name || environmentIdentity.name || "ENVIRONMENT").toUpperCase()', 'isHub ? "Hub" : String(environmentIdentity.display_name || environmentIdentity.name || "Environment")')
    anchor='    property string batteryStatus: "Desconhecido"'
    s=s.replace(anchor,'''    readonly property string batteryIconName: {
        var percent = parseInt(batteryText)
        if (batteryStatus === "A carregar") return "battery-charging"
        if (!isFinite(percent)) return "battery"
        if (percent <= 10) return "battery-warning"
        if (percent <= 30) return "battery-low"
        if (percent <= 70) return "battery-medium"
        return "battery-full"
    }
    readonly property string appsIconName: {
        var name = String(environmentIdentity.name || "").toLowerCase()
        if (name === "minecraft") return "pickaxe"
        if (name === "faculdade") return "zap"
        if (name === "hytale") return "swords"
        return "grid-2x2"
    }
'''+anchor)
    start=s.index('    Variants {\n        id: barVariants');end=s.index('    PanelWindow {\n        id: hotkeyOsdWindow',start)
    bar=s[start:end]
    bar=bar.replace('margins { left: 19; right: 19 }','margins { left: 8; right: 8 }')
    bar=bar.replace('            color: root.panel\n            border.width: 1','            color: "transparent"\n            border.width: 0',1)
    bar=bar.replace('spacing: 2','spacing: 6').replace('spacing: 4','spacing: 6')
    bar=bar.replace('label: "[ " + root.clockText + " ]"','label: root.clockText\n                    iconName: "calendar-days"\n                    accessibleLabel: "Calendário, " + root.clockText')
    bar=bar.replace('label: "[ " + root.environmentLabel + " ]"','label: root.environmentLabel\n                iconName: "monitor"\n                accessibleLabel: "Environment " + root.environmentLabel')
    bar=bar.replace('label: root.modelStoreState.state === "active" ? "[ IA ON ]" : (root.modelStoreState.state === "safe-to-remove" ? "[ SSD OK ]" : "[ IA OFF ]")','label: root.modelStoreState.state === "active" ? "IA ligada" : (root.modelStoreState.state === "safe-to-remove" ? "SSD pronto" : "IA desligada")\n                    iconName: "hard-drive"')
    bar=bar.replace('label: "[ MIC ATIVO ]"','label: "Microfone"\n                    iconName: "mic"')
    bar=bar.replace('label: "[ APPS ]"','label: ""\n                    iconName: root.appsIconName\n                    accessibleLabel: "Aplicações"')
    bar=bar.replace('label: "[ BAT " + root.batteryText + " ]"','label: root.batteryText\n                    iconName: root.batteryIconName\n                    accessibleLabel: "Bateria " + root.batteryText + ", " + root.batteryStatus')
    bar=bar.replace('compactSymbol: true','compactSymbol: false')
    bar=bar.replace('label: "[|]"\n                    alternateLabel: "[A]"','label: ""\n                    alternateLabel: ""\n                    iconName: "hexagon"\n                    alternateIconName: "ghost"\n                    accessibleLabel: "Central de Controlo"')
    s=s[:start]+bar+s[end:]
    s=s.replace('+ " | " + two(now.getHours())','+ " · " + two(now.getHours())')
    # Reuse the existing icon/tint renderer for the volume/brightness hotkey OSD.
    replacements={'airplane-mode-symbolic':'plane','airplane-mode-disabled-symbolic':'plane','audio-volume-muted-symbolic':'volume-x','audio-volume-high-symbolic':'volume-2','microphone-sensitivity-muted-symbolic':'mic-off','audio-input-microphone-symbolic':'mic','display-brightness-symbolic':'sun','dialog-warning-symbolic':'circle-alert','view-grid-symbolic':'grid-2x2','accessories-calculator-symbolic':'calculator','preferences-desktop-display-symbolic':'monitor','focus-windows-symbolic':'panels-top-left','camera-photo-symbolic':'camera','input-touchpad-symbolic':'touchpad'}
    for old,new in replacements.items():
        s=re.sub(r'"file:///usr/share/icons/Adwaita/symbolic/[^"\n]*/'+re.escape(old)+r'\.svg"','Qt.resolvedUrl("icons/lucide/'+new+'.svg")',s)
    # Control-centre labels gain real SVG icons without changing their hit areas.
    start=s.index('text: "Wi-Fi"; color: root.textMain')
    # Include the opening Text of the first Wi-Fi summary tile.
    start=s.rfind('                            Text {',0,start)
    end=s.index('                Column {\n                    width: parent.width; spacing: 7\n                    visible: root.popupKind === "controls" && root.shortcutsOpen',start)
    controls=s[start:end]
    mapping={
      '"Wi-Fi"':'root.wifiDisplayActive() ? "wifi" : "wifi-off"',
      '"Bluetooth"':'root.bluetoothDisplayPowered() ? "bluetooth" : "bluetooth-off"',
      '"Volume"':'root.volumeMuted ? "volume-x" : "volume-2"',
      '"Microfone"':'root.microphoneMuted ? "mic-off" : "mic"',
      '"Brilho do ecrã"':'"sun"','"Teclado"':'"keyboard"',
      '"Bloquear"':'"lock-keyhole"','root.isHub ? "Reiniciar" : "Ficheiros"':'root.isHub ? "rotate-cw" : "folder"',
      '"Atualizar"':'"refresh-cw"','"Encerrar"':'"power"',
      '"Terminal do Host"':'"terminal"','"Sair para o Host"':'"log-out"'}
    # Only Text blocks with simple labels; no form inputs or paragraph text.
    def label(match):
        b=match.group(0)
        for expr,icon in mapping.items():
            if re.search(r'text: '+re.escape(expr)+r'(?=;|\n)',b):
                b=b.replace('Text {','IconLabel {',1)
                b=re.sub(r'font.family: "JetBrains Mono";?\s*','',b)
                b=re.sub(r'font.pixelSize:', 'pixelSize:',b)
                b=re.sub(r';?\s*font.weight: Font.Normal','',b)
                b=b.replace('horizontalAlignment: Text.AlignHCenter','')
                b=re.sub(r'width: parent.width - 8;?\s*','',b)
                b=b.replace('IconLabel {','IconLabel { iconName: '+icon+';',1)
                return b
        return b
    controls=re.sub(r'Text \{[^{}]*\}',label,controls)
    # Network strength becomes the same Lucide family; keep the percentage.
    controls=controls.replace('text: root.wifiSignalBars(root.wifiDetails(modelData).signal)', 'text: root.wifiSignalBars(root.wifiDetails(modelData).signal)')
    s=s[:start]+controls+s[end:]
    return s

def workspace(s):
    s=s.replace('label: "[ " + modelData.name + " ]"','label: modelData.name')
    start=s.index('        // Lucide chevron-right:')
    end=s.index('        alternateLabel: label',start)
    s=s[:start]+'        iconName: "chevron-right"\n'+s[end:]
    return s
