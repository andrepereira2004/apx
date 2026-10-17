#!/usr/bin/env python3
"""Narrow, reversible presentation update for the fixed disposable physical pilot."""
from pathlib import Path
import datetime, fcntl, hashlib, json, os, re, shutil, sys
REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-shell-v1'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
AUDIT = REPO / 'audit/2026-10-17-desktop-motion'
RELATIVES = ['hypr/hyprland.lua'] + ['quickshell/apx/' + name + '.qml' for name in ['shell', 'MediaIsland', 'BarButton', 'ControlTile', 'ControlDashboard', 'ActivityPanel', 'PersonalizationPanel']]

def replace_once(text, before, after):
    assert text.count(before) == 1, before[:100]
    return text.replace(before, after, 1)

def hypr(text):
    if '-- APX coordinated motion v2' in text:
        return text
    # Layer movement lasts 300ms; fading finishes earlier so the launcher is readable in transit.
    motions = {
        'windowsMove': (2.4, 'apxMenuOutCubic', None),
        'windowsOut': (1.8, 'apxMenuOutCubic', 'popin 96%'),
        'fadeOut': (1.8, 'apxMenuOutCubic', None),
        'layersIn': (3.0, 'apxMenuOutCubic', 'fade'),
        'layersOut': (2.2, 'apxMenuOutCubic', 'fade'),
        'fadeLayersIn': (2.0, 'apxMenuOutCubic', None),
        'fadeLayersOut': (1.8, 'apxMenuOutCubic', None),
        'workspaces': (2.8, 'apxMenuOutCubic', 'slidefade 12%'),
        'workspacesIn': (2.8, 'apxMenuOutCubic', 'slidefade 12%'),
        'workspacesOut': (2.8, 'apxMenuOutCubic', 'slidefade 12%'),
    }
    for leaf, (speed, curve, style) in motions.items():
        line = f'hl.animation({{ leaf = "{leaf}", enabled = true, speed = {speed}, bezier = "{curve}"'
        if style: line += f', style = "{style}"'
        line += ' })'
        text, count = re.subn(r'hl\.animation\(\{ leaf = "' + leaf + r'",[^\n]*\}\)', lambda _: line, text)
        assert count == 1, leaf
    text = replace_once(text, '-- Rofi is a full-screen transparent layer containing a centered card.\n-- Scale only that layer; resident QuickShell menus animate their own content.', '-- APX coordinated motion v2: the launcher rises from the screen bottom.\n-- QuickShell menus animate internally and retain their own content transition.')
    text = replace_once(text, 'name = "apx-rofi-menu-motion",\n    match = { namespace = "^rofi$" },\n    animation = "popin 96%",', 'name = "apx-rofi-menu-motion",\n    match = { namespace = "^rofi$" },\n    animation = "slide bottom",')
    return text

def dark(text):
    # Default palette only; explicit Environment/global tint choices retain priority.
    colors = {'#b3262939':'#ed101117', '#ed242736':'#f2101117', '#303445':'#1b1d26', '#41475b':'#292d3a', '#454d64':'#353a4a', '#50586d':'#414654', '#485064':'#343947', '#dc202330':'#ed15171f', '#ed343a4d':'#f2292d3a'}
    for before, after in colors.items(): text = text.replace(before, after)
    return text

def finish_shell(text):
    text = text.replace('if (popupKind === kind && popup.open) {', 'if (popupKind === kind && popup.open && !popupClosing) {')
    if 'visual_height: popupBackground.height' not in text:
        text = replace_once(text, 'visual_width: popupBackground.width, visual_x: popupBackground.x,', 'visual_width: popupBackground.width, visual_height: popupBackground.height, visual_x: popupBackground.x, fullscreen: root.focusedFullscreen,')
    return text

def shell(text):
    if '// APX transient island v2' in text: return finish_shell(text)
    before = '                width: Math.min(220, Math.max(0, rightActions.x - (environmentButton.x + environmentButton.width) - 36))\n                visible: !root.isHub && mediaIsland.presence > 0 && width >= 110'
    after = '''                // APX transient island v2: resize in one curve, then restore the media title.
                readonly property real availableWidth: Math.max(0, rightActions.x - (environmentButton.x + environmentButton.width) - 36)
                width: Math.min(transientActive ? 300 : 220, availableWidth) * presence
                Behavior on width { enabled: mediaIsland.presence === 1; NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }
                visible: (!root.isHub || root.hotkeyOsdVisible) && (presence > 0 || width > 1) && availableWidth >= 110
                transientActive: root.hotkeyOsdVisible && root.bar === screenBar
                transientIcon: root.hotkeyOsdIcon
                transientTitle: root.hotkeyOsdTitle
                transientDetail: root.hotkeyOsdDetail
                transientProgress: root.hotkeyOsdProgress
                expandedAmount: root.bar === screenBar && popup.open && root.popupKind === "media" ? root.islandProgress : 0'''
    text = replace_once(text, before, after)
    text = replace_once(text, '        visible: root.hotkeyOsdVisible\n        anchors { bottom: true }', '        visible: root.hotkeyOsdVisible && (!root.mediaButton || !root.mediaButton.visible || popup.open || root.focusedFullscreen)\n        anchors { bottom: true }')
    # Keep the fallback for fullscreen clients, open menus and narrow screens.
    # Its removal timer must never hide a newer OSD during rapid repeated key presses.
    text = replace_once(text, '        hotkeyOsdIcon = icon\n', '        hotkeyOsdGoneTimer.stop()\n        hotkeyOsdIcon = icon\n')
    # Only show the bar transient when it can actually be seen. The fallback keeps working.
    text = text.replace('transientActive: root.hotkeyOsdVisible && root.bar === screenBar', 'transientActive: root.hotkeyOsdVisible && root.bar === screenBar && !popup.open && !root.focusedFullscreen')
    # Preserve the existing focused fullscreen binding if present.
    if 'readonly property bool focusedFullscreen:' not in text:
        text = replace_once(text, '    property bool hotkeyOsdVisible: false', '    readonly property bool focusedFullscreen: !!(Hyprland.activeToplevel && Hyprland.activeToplevel.lastIpcObject.fullscreen > 0)\n    readonly property bool filesFocused: !!(Hyprland.activeToplevel && /^(thunar|org\\.xfce\\.Thunar)$/i.test(String(Hyprland.activeToplevel.wayland ? Hyprland.activeToplevel.wayland.appId : Hyprland.activeToplevel.lastIpcObject.class || \"\")))\n    property bool hotkeyOsdVisible: false')
    # Media grows from the capsule while keeping its top edge on the same baseline.
    text = replace_once(text, '            y: root.islandOrigin.y + (65 - root.islandOrigin.y) * root.islandProgress', '            property real settledY: root.popupKind === "media" ? root.islandOrigin.y : 65\n            Behavior on settledY { enabled: popup.open && root.islandProgress > .99 && !root.popupClosing; NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }\n            y: root.islandOrigin.y + (settledY - root.islandOrigin.y) * root.islandProgress')
    text = replace_once(text, 'duration: 240; easing.type: Easing.OutQuint', 'duration: 300; easing.type: Easing.OutCubic')
    text = replace_once(text, 'duration: 180; easing.type: Easing.InOutCubic', 'duration: 240; easing.type: Easing.InOutCubic')
    text = replace_once(text, '                    accessibleLabel: "Abrir gestor de ficheiros"', '                    accessibleLabel: "Abrir gestor de ficheiros"\n                    alternateActive: root.filesFocused && !popup.open && !environmentAppsProcess.running\n                    alternateLabel: filesButton.label')
    text = replace_once(text, '    property real islandContentOpacity: 1', '    property real islandContentOpacity: 1\n    readonly property string menuRoute: [popupKind, controlsWifiOpen, controlsBluetoothOpen, controlsAudioOpen, controlsMicrophoneOpen, controlsMoreOpen, controlsAppearanceOpen, controlsActivityKind, shortcutsOpen, powerConfirmOpen, calendarView, calendarEditor, environmentCreateOpen, environmentEditOpen, environmentDeleteConfirm].join(":")\n    onMenuRouteChanged: Qt.callLater(function() {\n        if (!popup.open || root.popupClosing || root.popupAnimationPending) return\n        root.islandContentOpacity = 0\n        islandContentAnimation.restart()\n    })')
    text = replace_once(text, '            readonly property real targetWidth: Math.min(popup.menuWidth, popup.width - 16)', '            property real targetWidth: Math.min(popup.menuWidth, popup.width - 16)\n            Behavior on targetWidth { enabled: popup.open && root.islandProgress > .99 && !root.popupClosing; NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }')
    text = replace_once(text, '            x: root.islandOrigin.x + (Math.max(8, Math.min(root.popupLeftMargin, popup.width - targetWidth - 8)) - root.islandOrigin.x) * root.islandProgress', '            property real settledX: Math.max(8, Math.min(root.popupLeftMargin, popup.width - targetWidth - 8))\n            Behavior on settledX { enabled: popup.open && root.islandProgress > .99 && !root.popupClosing; NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }\n            x: root.islandOrigin.x + (settledX - root.islandOrigin.x) * root.islandProgress')
    text = replace_once(text, '                x: 10; y: 10\n                width: popupBackground.targetWidth - 20', '                x: 10; y: 10 + 8 * (1 - root.islandContentOpacity)\n                width: popupBackground.targetWidth - 20')
    text = replace_once(text, '                                    popup_opacity: popupBackground.opacity,', '                                    popup_opacity: popupBackground.opacity,\n                                    content_opacity: root.islandContentOpacity, visual_width: popupBackground.width, visual_x: popupBackground.x,\n                                    files_active: root.filesFocused, osd_visible: root.hotkeyOsdVisible, island_transient: root.mediaButton ? root.mediaButton.transientActive : false,')
    text = text.replace('NumberAnimation { duration: 200; easing.type: Easing.OutQuint } }', 'NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }')
    return finish_shell(dark(text))

def atomic(path, data, mode, uid, gid):
    assert not path.is_symlink(), path
    temporary = path.with_name(path.name + '.motion-v2-tmp')
    temporary.write_bytes(data); os.chmod(temporary, mode); os.chown(temporary, uid, gid); os.replace(temporary, path)

def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    if len(sys.argv) == 3 and sys.argv[1] == '--rollback':
        backup = Path(sys.argv[2]).resolve()
        assert backup.parent == Path('/var/lib/apx/backups') and backup.name.endswith('-desktop-motion-v2')
        for item in json.loads((backup / 'inventory.json').read_text()):
            atomic(Path(item['path']), (backup / item['path'].lstrip('/')).read_bytes(), item['mode'], item['uid'], item['gid'])
        print('Restored', backup); return
    assert sys.argv[1:] in ([], ['--check'])
    plans = {}
    homes = [Path('/var/lib/apx/environments') / n / 'home/apx' for n in ['hub', 'faculdade', 'hytale', 'minecraft', 'steam']]
    for base in [SOURCE, SEED] + homes:
        for rel in RELATIVES:
            dest = base / rel if base in (SOURCE, SEED) else base / '.config' / rel
            assert dest.is_file() and not dest.is_symlink(), dest
            plans[dest] = (dark((AUDIT / 'MediaIsland.qml').read_text()) if rel.endswith('/MediaIsland.qml') else hypr(dest.read_text()) if rel.endswith('.lua') else shell(dest.read_text()) if rel.endswith('/shell.qml') else dark(dest.read_text())).encode()
    for runtime, base in [(REPO/'scripts/virtual-lab/apx-lab-runtime.py',SOURCE), (Path('/usr/lib/apx/apx-lab-runtime.py'),SEED)]:
        text = runtime.read_text()
        for rel in RELATIVES:
            digest = hashlib.sha256(plans[base/rel]).hexdigest()
            text, n = re.subn(r'("'+re.escape(rel)+r'": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest+m[2],text); assert n==1
        plans[runtime] = text.encode()
    recovery = REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
    text,n = re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+hashlib.sha256(plans[REPO/'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(),recovery.read_text()); assert n==1
    plans[recovery] = text.encode()
    plans = {p:d for p,d in plans.items() if p.read_bytes()!=d}
    if sys.argv[1:] == ['--check']:
        (AUDIT/'planned-paths.json').write_text(json.dumps([str(p) for p in plans],indent=2)+'\n')
        # Repository candidates can be validated in the active namespace before installation.
        (AUDIT/'hyprland-candidate.lua').write_text(hypr((SOURCE/'hypr/hyprland.lua').read_text()))
        print('Validated transforms:',len(plans),'planned files'); return
    if not plans: print('Desktop motion v2 already installed.'); return
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-desktop-motion-v2')
    backup.mkdir(parents=True)
    inventory=[]
    for path in plans:
        stat=path.stat(); saved=backup/str(path).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,saved)
        inventory.append(dict(path=str(path),mode=stat.st_mode&0o777,uid=stat.st_uid,gid=stat.st_gid,sha256_before=hashlib.sha256(path.read_bytes()).hexdigest(),sha256_after=hashlib.sha256(plans[path]).hexdigest()))
    (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    for item in sorted(inventory,key=lambda i:Path(i['path']).name=='shell.qml'):
        path=Path(item['path']);atomic(path,plans[path],item['mode'],item['uid'],item['gid']);assert path.read_bytes()==plans[path]
    (AUDIT/'backup.txt').write_text(str(backup)+'\n')
    for home in homes: (home/'.config/quickshell/apx/shell.qml').touch()
    print(backup);print('Verified',len(plans),'files.')

if __name__=='__main__':
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);main()
