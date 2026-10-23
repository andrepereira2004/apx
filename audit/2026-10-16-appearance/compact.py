import re

def end_block(text,start):
    begin=text.index('{',start);depth=0;quote=None;escape=False;i=begin
    while i<len(text):
        ch=text[i]
        if quote:
            if escape:escape=False
            elif ch=='\\':escape=True
            elif ch==quote:quote=None
        elif ch in ('"',"'",'`'):quote=ch
        elif text.startswith('//',i):
            i=text.find('\n',i)
            if i<0:raise ValueError('Unterminated comment')
            continue
        elif ch=='{':depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:return i+1
        i+=1
    raise ValueError('Unbalanced QML')

def compact(text):
    if 'id: compactDashboard' in text:return text
    for identity in ['wifiSummaryMouse','volumeSummarySlider','displayBrightnessSlider','terminalMouse','environmentsControlMouse']:
        at=text.index('id: '+identity)
        start=text.rfind('                    Row {',0,at)
        assert start>=0,identity
        text=text[:start]+text[end_block(text,start):]
    at=text.index('id: lockMouse');start=text.rfind('                    Grid {',0,at)
    text=text[:start]+text[end_block(text,start):]
    at=text.index('text: "Ações da sessão"');start=text.rfind('                    Text {',0,at)
    text=text[:start]+text[end_block(text,start):]
    at=text.index('label: "Mais opções"');start=text.rfind('                    MenuButton {',0,at)
    text=text[:start]+text[end_block(text,start):]
    # The old spacer belongs only to the removed session-action caption.
    text=re.sub(r'                    Item \{\n                        visible: root.controlsAllClosed\(\) && !root.powerConfirmOpen\n                        width: parent.width; height: visible \? 9 : 0\n                    \}', '',text)
    text=text.replace('    property bool controlsAppearanceOpen: false','    property bool controlsAppearanceOpen: false\n    property string controlsActivityKind: ""')
    text=re.sub(r'(?m)^( +)controlsAppearanceOpen = false$',lambda m:m[0]+'\n'+m[1]+'controlsActivityKind = ""',text)
    text=text.replace('return !controlsWifiOpen && !controlsBluetoothOpen && !controlsAudioOpen && !controlsMicrophoneOpen','return !controlsWifiOpen && !controlsBluetoothOpen && !controlsAudioOpen && !controlsMicrophoneOpen && !controlsActivityKind.length')
    anchor='    function controlsAllClosed() {'
    methods='''    function openActivitySection(kind) {
        controlsWifiOpen = false; controlsBluetoothOpen = false
        controlsAudioOpen = false; controlsMicrophoneOpen = false
        controlsActivityKind = kind
        DesktopActivity.refresh()
    }
    function openMoreOptions() { controlsMoreOpen = true; controlsAppearanceOpen = false; menuFlick.contentY = 0 }
    function runControlAction(action) {
        if (action === "lock") { closePopup(); if (!lockProcess.running) lockProcess.running = true }
        else if (action === "files-or-reboot") {
            if (isHub) beginPower("reboot")
            else { closePopup(); if (!environmentFilesProcess.running) environmentFilesProcess.running = true }
        } else if (action === "update") { closePopup(); if (!updateUiProcess.running) updateUiProcess.running = true }
        else if (action === "poweroff") beginPower("poweroff")
        else if (action === "terminal") { closePopup(); if (!hostConsoleProcess.running) hostConsoleProcess.running = true }
        else if (action === "exit") { closePopup(); if (!hostExitProcess.running) hostExitProcess.running = true }
    }

'''
    text=text.replace(anchor,methods+anchor,1)
    # Clear the activity page when a connectivity/audio section is selected.
    text=text.replace('    function openControlSection(section) {','    function openControlSection(section) {\n        controlsActivityKind = ""',1)
    anchor='''                    Rectangle {
                        visible: root.controlsWifiOpen
'''
    assert text.count(anchor)==1
    dashboard='''                    ControlDashboard {
                        id: compactDashboard
                        width: parent.width
                        visible: root.controlsAllClosed() && !root.powerConfirmOpen
                        controller: root
                    }
                    ActivityPanel {
                        width: parent.width
                        visible: root.controlsActivityKind.length > 0
                        kind: root.controlsActivityKind
                        onBack: { root.controlsActivityKind = ""; menuFlick.contentY = 0 }
                    }

'''
    text=text.replace(anchor,dashboard+anchor,1)
    text=text.replace('(root.isHub ? Math.min(popup.height - 74, menuContent.implicitHeight + 20) : 394)','Math.min(popup.height - 74, menuContent.implicitHeight + 20)')
    text=text.replace('visible: root.popupKind !== "calendar"\n                    title:', 'visible: root.popupKind !== "calendar" && !(root.popupKind === "controls" && root.controlsAllClosed() && !root.controlsMoreOpen && !root.shortcutsOpen)\n                    title:')
    text=text.replace('!displayBrightnessSlider.pressed','!compactDashboard.brightnessPressed')
    return text

if __name__=='__main__':
    from pathlib import Path
    path=Path('config/environment-shell-v1/quickshell/apx/shell.qml');path.write_text(compact(path.read_text()))
