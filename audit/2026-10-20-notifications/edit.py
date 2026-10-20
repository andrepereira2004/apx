from pathlib import Path
base=Path('config/environment-shell-v1')
p=base/'local/bin/apx-desktop-activity-v1';s=p.read_text();s=s.replace("active=action=='list'))", "active=action=='list',can_open=action=='list' and 'default' in (item.get('actions') or {})))")
needle='def status():\n'
s=s.replace(needle,'''def notification_action(action, raw_id=None):
    if action not in ('read', 'read-all', 'open'):
        raise ValueError('Ação de notificação inválida.')
    notes, _ = notifications()
    if action == 'read-all':
        # Snapshot IDs: notifications arriving during this action stay unread.
        targets = [n for n in notes if n['active']]
    else:
        if not raw_id or not re.fullmatch(r'[0-9]{1,10}', raw_id):
            raise ValueError('Notificação inválida.')
        targets = [n for n in notes if n['active'] and n['id'] == int(raw_id)]
        if not targets:
            raise ValueError('Esta notificação já não está disponível.')
    for note in targets:
        if action == 'open' and not note['can_open']:
            raise ValueError('Esta aplicação não disponibiliza uma ação para abrir.')
        command = ['/usr/bin/makoctl', 'invoke' if action == 'open' else 'dismiss', '-n', str(note['id'])]
        if action == 'open': command.append('default')
        result = subprocess.run(command, capture_output=True, text=True, timeout=3)
        if result.returncode:
            raise RuntimeError('Não foi possível abrir a notificação.' if action == 'open' else 'Não foi possível marcar a notificação como lida.')


'''+needle)
s=s.replace("    elif len(args)==3 and args[0]=='media':", "    elif len(args) in (2,3) and args[0]=='notification':\n        if (args[1] == 'read-all') != (len(args) == 2): raise ValueError('Ação de notificação inválida.')\n        notification_action(args[1], args[2] if len(args) == 3 else None)\n        notes,count=notifications()\n        print(json.dumps(dict(notifications=notes,active_notifications=count),ensure_ascii=False));return\n    elif len(args)==3 and args[0]=='media':")
p.write_text(s)
p=base/'quickshell/apx/DesktopActivity.qml';s=p.read_text().replace('        if (busy) return\n        error = ""','        if (busy) return\n        if (args[0] === "notification" && notificationsProcess.running) notificationsProcess.running = false\n        error = ""');s=s.replace('onTriggered: if (!activity.notificationsProcess.running)', 'onTriggered: if (!activity.busy && !activity.notificationsProcess.running)');p.write_text(s)
p=base/'quickshell/apx/ActivityPanel.qml';s=p.read_text();s=s.replace('    Text {\n        width: parent.width; wrapMode:', '''    Row {
        visible: panel.kind !== "media" && panel.entries.some(function(n) { return n.active })
        width: parent.width
        ControlTile { width: parent.width; showCaption: true; iconName: "check-check"; caption: "Marcar todas como lidas"; enabled: !DesktopActivity.busy; onActivated: DesktopActivity.action(["notification", "read-all"]) }
    }
    Text {
        visible: panel.kind !== "media" && DesktopActivity.error.length > 0
        width: parent.width; wrapMode: Text.WordWrap; text: DesktopActivity.error; textFormat: Text.PlainText
        color: "#f0b7b7"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
    }
    Text {
        width: parent.width; wrapMode:''',1)
s=s.replace('radius: 8\n', 'radius: panel.kind === "media" ? 8 : 12\n')
s=s.replace('                Image {', '''                Row {
                    visible: panel.kind !== "media" && !!card.entry.active
                    width: parent.width; spacing: 6
                    ControlTile {
                        visible: !!card.entry.can_open; showCaption: true
                        width: (parent.width - 6) * 0.36; iconName: "external-link"; caption: "Abrir"
                        enabled: !DesktopActivity.busy
                        onActivated: DesktopActivity.action(["notification", "open", String(card.entry.id)])
                    }
                    ControlTile {
                        showCaption: true; width: card.entry.can_open ? (parent.width - 6) * 0.64 : parent.width
                        iconName: "check"; caption: "Marcar como lida"; enabled: !DesktopActivity.busy
                        onActivated: DesktopActivity.action(["notification", "read", String(card.entry.id)])
                    }
                }
                Image {''')
p.write_text(s)
p=Path('scripts/physical-pilot/deploy-notifications-20261020.py');s=Path('scripts/physical-pilot/deploy-controls-minimal-20261019.py').read_text().replace('2026-10-19-controls-minimal','2026-10-20-notifications').replace('-controls-minimal','-notifications').replace("['quickshell/apx/shell.qml', 'quickshell/apx/PersonalizationPanel.qml']", "['quickshell/apx/ActivityPanel.qml', 'quickshell/apx/DesktopActivity.qml', 'local/bin/apx-desktop-activity-v1']");p.write_text(s)
