#!/usr/bin/env python3
"""Reversible, target-bound Island presentation experiment; no auth/service changes."""
from pathlib import Path
import datetime,fcntl,hashlib,importlib.util,json,os,re,shutil,sys
REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
CANDIDATE=SOURCE
SEED=Path('/usr/share/apx/config-seeds/environment-shell-v1')

def write(path,data,mode,uid,gid):
    assert not path.is_symlink(),path
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.island-tmp');temporary.write_bytes(data)
    os.chmod(temporary,mode);os.chown(temporary,uid,gid);os.replace(temporary,path)

def sync_media_shell(text):
    source=(SOURCE/'quickshell/apx/shell.qml').read_text()
    a=text.index('            MediaIsland {');b=text.index('\n            BarButton {',a)
    sa=source.index('            MediaIsland {');sb=source.index('\n            BarButton {',sa)
    text=text[:a]+source[sa:sb]+text[b:]
    text=text.replace('root.popupKind === "controls" && root.controlsActivityKind === "media"','(root.popupKind === "media" || (root.popupKind === "controls" && root.controlsAllClosed()))')
    text=text.replace('(root.popupKind === "battery" ? 340 : 300)', '(root.popupKind === "battery" || root.popupKind === "media" ? 340 : 300)')
    text=text.replace(': (root.popupKind === "model" ? 370', ': (root.popupKind === "media" ? Math.min(popup.height - 74, menuContent.implicitHeight + 20) : root.popupKind === "model" ? 370')
    text=text.replace('title: root.popupKind === "battery" ?', 'title: root.popupKind === "media" ? "Reprodução" : root.popupKind === "battery" ?') if 'title: root.popupKind === "media"' not in text else text
    if 'id: mediaMenu' not in text:
        a=source.index('                Column {\n                    id: mediaMenu')
        end='                Column {\n                    width: parent.width; spacing: 10; visible: root.popupKind === "model"'
        b=source.index(end,a);target=text.index(end)
        text=text[:target]+source[a:b]+text[target:]
    if 'readonly property var mediaButton:' not in text:
        text=text.replace('    readonly property var appsButton:', '    readonly property var mediaButton: bar ? bar.mediaButton : null\n    readonly property var appsButton:',1)
        text=text.replace('        property alias appsButton: appsButton','        property alias mediaButton: mediaIsland\n        property alias appsButton: appsButton',1)
    text=text.replace('var buttons = [calendarButton, environmentButton, modelStoreButton, appsButton,', 'var buttons = [calendarButton, environmentButton, modelStoreButton, mediaButton, appsButton,')
    text=text.replace('controls: controlCenterButton, battery: batteryButton, model: modelStoreButton', 'controls: controlCenterButton, media: mediaButton, battery: batteryButton, model: modelStoreButton')
    if 'function openMedia(): void' not in text:
        text=text.replace('        function openControls(): void {','        function openMedia(): void { DesktopActivity.refresh(); root.toggleFocusedPopup("media") }\n\n        function openControls(): void {',1)
    text=text.replace('enabled: root.islandProgress > .99 && !root.popupClosing; NumberAnimation { duration: 200;', 'enabled: root.islandProgress > .99 && !root.popupClosing && !(root.popupKind === "controls" && compactDashboard.mediaTransitionRunning) && !(root.popupKind === "media" && mediaMenu.mediaTransitionRunning); NumberAnimation { duration: 200;')
    text=text.replace('id: mediaMenu\n                    width:', 'id: mediaMenu\n                    readonly property bool mediaTransitionRunning: mediaPanel.transitioning\n                    width:').replace('ActivityPanel { width: parent.width; kind: "media"; showBack: false }','ActivityPanel { id: mediaPanel; width: parent.width; kind: "media"; showBack: false }')
    return text

def main():
    assert Path('/etc/hostname').read_text().strip()=='apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    if len(sys.argv)==3 and sys.argv[1]=='--rollback':
        backup=Path(sys.argv[2]).resolve();assert backup.parent==Path('/var/lib/apx/backups') and backup.name.endswith('-control-layout')
        for item in json.loads((backup/'inventory.json').read_text()):
            path=Path(item['path'])
            if item['existed']:write(path,(backup/str(path).lstrip('/')).read_bytes(),item['mode'],item['uid'],item['gid'])
            elif path.exists():path.unlink()
        for p in Path('/var/lib/apx/environments').glob('*/home/apx/.config/quickshell/apx/shell.qml'):p.touch()
        print('Restored',backup);return
    assert len(sys.argv)==1
    relatives=['quickshell/apx/'+name+'.qml' for name in ['ControlDashboard','DesktopActivity','MediaTimeline','ActivityPanel','PersonalizationPanel','ControlTile','BarButton','MediaIsland','shell']]+['local/bin/apx-appearance-v1','local/bin/apx-desktop-activity-v1','rofi/config.rasi','gtk-3.0/gtk.css']
    planned={}
    roots=[SOURCE,SEED]+[Path('/var/lib/apx/environments')/n/'home/apx' for n in ['hub','faculdade','hytale','minecraft','steam']]
    for base in roots:
        for rel in relatives:
            dest=base/rel if base in (SOURCE,SEED) else base/('.local/'+rel[6:] if rel.startswith('local/') else '.config/'+rel)
            data=(SOURCE/rel).read_bytes()
            if rel=='quickshell/apx/shell.qml' and base != SOURCE:
                text=dest.read_text().replace('else if (action === "poweroff") beginPower("poweroff")','else if (action === "reboot") beginPower("reboot")\n        else if (action === "poweroff") beginPower("poweroff")') if 'action === "reboot") beginPower' not in dest.read_text() else dest.read_text()
                if 'readonly property bool splitControls:' not in text:
                    a=text.index('            id: popupBackground');b=text.index('            NumberAnimation {',a)
                    part=text[a:b].replace('color: root.popupPanel','readonly property bool splitControls: root.popupKind === "controls" && root.controlsAllClosed() && !root.controlsMoreOpen && !root.shortcutsOpen && !root.powerConfirmOpen\n            color: splitControls ? "transparent" : root.popupPanel').replace('border.width: 1','border.width: splitControls ? 0 : 1')
                    text=text[:a]+part+text[b:]
                text=text.replace('visible: root.popupKind !== "calendar"\n                    title:', 'visible: root.popupKind !== "calendar" && !popupBackground.splitControls\n                    title:')
                text=text.replace('property int menuBodySize: 12','property int menuBodySize: 11').replace('property int menuSmallSize: 11','property int menuSmallSize: 10').replace('property int menuMetaSize: 10','property int menuMetaSize: 9')
                text=text.replace('x: rightActions.x - 3; y: rightActions.y - 3','x: rightActions.x - 3; y: rightActions.y').replace('width: rightActions.width + 6; height: rightActions.height + 6','width: rightActions.width + 6; height: rightActions.height')
                text=text.replace('x: rightActions.x - 3; y: rightActions.y','x: rightActions.x; y: rightActions.y').replace('width: rightActions.width + 6; height: rightActions.height','width: rightActions.width; height: rightActions.height')
                data=text.replace('anchors.right: environmentButton.left','anchors.right: rightActions.left').replace('environmentButton.x - leftActions.width - 36','rightActions.x - (environmentButton.x + environmentButton.width) - 36').encode()
            elif rel=='gtk-3.0/gtk.css' and base != SOURCE:
                data=dest.read_text().replace('.thunar.background { background-color: rgba(10, 16, 20, 0.85)', '.thunar.background { background-color: rgba(48, 52, 69, 0.85)').encode()
            elif rel=='rofi/config.rasi' and base != SOURCE:
                data=dest.read_text().replace('#0a1014d9','#303445d9').replace('#191d22d9','#303445d9').encode()
            if rel=='quickshell/apx/shell.qml':data=sync_media_shell(data.decode()).encode()
            if rel=='hypr/apx-lock-appearance.conf' and dest.exists():continue
            planned[dest]=data
    for runtime,base in [(REPO/'scripts/virtual-lab/apx-lab-runtime.py',SOURCE),(Path('/usr/lib/apx/apx-lab-runtime.py'),SEED)]:
        text=runtime.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2;section=text[start:end]
        for rel in relatives:
            path=base/rel;digest=hashlib.sha256(planned.get(path,path.read_bytes() if path.exists() else b'')).hexdigest()
            section,count=re.subn(r'("'+re.escape(rel)+r'": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest+m[2],section);assert count<=1
            if not count:section=section.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    '+json.dumps(rel)+': '+json.dumps(digest)+',',1)
        planned[runtime]=(text[:start]+section+text[end:]).encode()
    recovery=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
    text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+hashlib.sha256(planned[REPO/'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(),recovery.read_text());assert count==1
    planned[recovery]=text.encode()
    planned={path:data for path,data in planned.items() if not path.exists() or path.read_bytes()!=data}
    if not planned:print('Control layout already installed.');return
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-control-layout');backup.mkdir(parents=True)
    inventory=[]
    for path in planned:
        existed=path.exists();metadata=path.stat() if existed else path.parent.stat()
        mode=metadata.st_mode&0o777 if existed else (0o755 if '/bin/' in str(path) else 0o644)
        saved=backup/str(path).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True)
        if existed:shutil.copy2(path,saved)
        inventory.append(dict(path=str(path),existed=existed,mode=mode,uid=metadata.st_uid,gid=metadata.st_gid))
    (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    for item in sorted(inventory,key=lambda i:Path(i['path']).name=='shell.qml'):
        path=Path(item['path']);write(path,planned[path],item['mode'],item['uid'],item['gid'])
        assert path.read_bytes()==planned[path]
    for p in Path('/var/lib/apx/environments').glob('*/home/apx/.config/quickshell/apx/shell.qml'):p.touch()
    print(backup);print('Verified',len(planned),'files. No authentication, service or Hyprland animation changes.')

if __name__=='__main__':
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);main()
