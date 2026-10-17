import re

def shell(text):
    if 'id: personalizationPanel' in text:return text
    text=text.replace('    property bool controlsMoreOpen: false','    property bool controlsMoreOpen: false\n    property bool controlsAppearanceOpen: false')
    text=re.sub(r'(?m)^( +)controlsMoreOpen = false$', lambda m: m[0]+'\n'+m[1]+'controlsAppearanceOpen = false', text)
    # Center all background consumers on the persistent Environment-local choice.
    anchor='    property int wallpaperIndex:'
    text=text.replace(anchor,'    readonly property url currentWallpaper: Appearance.wallpaper.length ? Appearance.wallpaper : root.wallpaperSources[root.wallpaperIndex]\n'+anchor,1)
    text=text.replace('source: root.wallpaperSources[root.wallpaperIndex]','source: root.currentWallpaper')
    text=text.replace('wallpaper: root.wallpaperSources[root.wallpaperIndex]','wallpaper: root.currentWallpaper')
    text=text.replace('interval: 15 * 60 * 1000\n        running: true', 'interval: 15 * 60 * 1000\n        running: !Appearance.wallpaper.length')
    text=text.replace('property color panel: "#b3262939"','property color panel: Appearance.tintWindows ? Qt.rgba(Appearance.surface.r, Appearance.surface.g, Appearance.surface.b, 0.85) : "#b3262939"')
    text=text.replace('property color popupPanel: "#ed242736"','property color popupPanel: Appearance.tintWindows ? Qt.rgba(Appearance.surface.r, Appearance.surface.g, Appearance.surface.b, 0.93) : "#ed242736"')
    for name,field,old in [('controlButtonSurface','surface','#303445'),('controlButtonHover','hover','#41475b'),('controlButtonActive','active','#454d64'),('controlButtonOutline','border','#50586d')]:
        text=text.replace(name+': "'+old+'"',name+': Appearance.tintButtons ? Appearance.'+field+' : "'+old+'"')
    text=text.replace('source: root.hotkeyOsdIcon\n                tint: root.textMain','source: root.hotkeyOsdIcon\n                tint: Appearance.iconColor')
    text=text.replace('root.controlsMoreOpen ? 340 * root.controlCenterScale','root.controlsMoreOpen ? (root.controlsAppearanceOpen ? Math.min(popup.height - 74, menuContent.implicitHeight + 20) : 340) * root.controlCenterScale')
    text=text.replace('(root.controlsMoreOpen ? "Mais opções" : "Central de Controlo")','(root.controlsMoreOpen ? (root.controlsAppearanceOpen ? "Personalização" : "Mais opções") : "Central de Controlo")')
    text=text.replace('visible: root.popupKind === "controls" && root.controlsMoreOpen && !root.shortcutsOpen','visible: root.popupKind === "controls" && root.controlsMoreOpen && !root.shortcutsOpen && !root.controlsAppearanceOpen')
    anchor='                    MenuButton { outlined: true; label: "‹ Voltar aos controlos"; onActivated: { root.controlsMoreOpen = false; menuFlick.contentY = 0 } }'
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'\n                    MenuButton { outlined: true; iconName: "settings"; label: "Personalização"; onActivated: { Appearance.refresh(); root.controlsAppearanceOpen = true; menuFlick.contentY = 0 } }')
    anchor='                Column {\n                    width: parent.width; spacing: 7\n                    visible: root.popupKind === "controls" && root.shortcutsOpen'
    assert text.count(anchor)==1
    panel='''                PersonalizationPanel {
                    id: personalizationPanel
                    width: parent.width
                    visible: root.popupKind === "controls" && root.controlsMoreOpen && root.controlsAppearanceOpen && !root.shortcutsOpen
                    wallpapers: root.wallpaperSources
                    onBack: { root.controlsAppearanceOpen = false; menuFlick.contentY = 0 }
                    onChooseImage: { root.closePopup(); Appearance.chooseWallpaper() }
                }

'''
    text=text.replace(anchor,panel+anchor)
    text=text.replace('        // Text fields own cursor movement; only Tab navigates the menu.','        if (arrow && root.controlsAppearanceOpen && personalizationPanel.colorInputActive) return\n        // Text fields own cursor movement; only Tab navigates the menu.')
    old='Text { anchors.left: parent.left; anchors.leftMargin: 12; anchors.top: parent.top; anchors.topMargin: 8; text: "Sensibilidade do rato"; color: root.textMain; font.family: "JetBrains Mono"; font.pixelSize: root.menuBodySize }'
    new='IconLabel { anchors.left: parent.left; anchors.leftMargin: 12; anchors.top: parent.top; anchors.topMargin: 8; text: "Sensibilidade do rato"; iconName: "mouse"; color: root.textMain; pixelSize: root.menuBodySize }'
    assert text.count(old)==1
    text=text.replace(old,new)
    for caption in ['text: "Modo de energia · " + root.platformLabel(root.hardwareProfile.platform_profile)','text: "Liga o carregador para usar o modo Desempenho do portátil."']:
        at=text.index(caption);start=text.rfind('                    Text {',0,at);end=text.index('\n                    }',at)+len('\n                    }')
        text=text[:start]+text[end:]
    text=text.replace('root.hardwareMessage = "Perfil " + root.platformLabel(result.platform_profile) + " confirmado pelo sistema."','root.hardwareMessage = ""')
    # Keep labels readable on tinted state surfaces.
    text=text.replace('(microphoneState === 1 ? "#3b4850" : "#b8d8dc")','(Appearance.tintButtons ? (microphoneState === 1 ? Appearance.hover : Appearance.active) : (microphoneState === 1 ? "#3b4850" : "#b8d8dc"))')
    text=text.replace('(lightState === 1 ? "#3b4850" : "#b8d8dc")','(Appearance.tintButtons ? (lightState === 1 ? Appearance.hover : Appearance.active) : (lightState === 1 ? "#3b4850" : "#b8d8dc"))')
    text=text.replace('parent.microphoneState === 2 ? "#172126"','parent.microphoneState === 2 && !Appearance.tintButtons ? "#172126"')
    text=text.replace('parent.lightState === 2 ? "#172126"','parent.lightState === 2 && !Appearance.tintButtons ? "#172126"')
    text=text.replace('function hotkeyTouchpadOff(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/touchpad.svg")','function hotkeyTouchpadOff(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/touchpad-off.svg")')
    return text

if __name__=='__main__':
    from pathlib import Path
    path=Path('config/environment-shell-v1/quickshell/apx/shell.qml');path.write_text(shell(path.read_text()))
