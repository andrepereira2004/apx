from pathlib import Path
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent;s=r/'config/environment-shell-v1'
rels=['local/bin/apx-appearance-v1','quickshell/apx/Appearance.qml','quickshell/apx/PersonalizationPanel.qml','quickshell/apx/shell.qml','quickshell/apx/BarButton.qml','quickshell/apx/MediaIsland.qml']
for rel in rels:
 t=(s/rel).read_text()
 if rel.endswith('apx-appearance-v1'):
  t=t.replace("DEFAULT_STYLE = dict", "DEFAULT_OPACITY = dict(bar=93, menus=95, terminal=85, files=85, rofi=85)\n\ndef validate_opacity(value):\n    if not isinstance(value, dict) or set(value) - set(DEFAULT_OPACITY):\n        raise ValueError('Destino de opacidade inválido.')\n    if any(type(v) is not int or not 0 <= v <= 100 for v in value.values()):\n        raise ValueError('A opacidade deve estar entre 0 e 100%.')\n    return {**DEFAULT_OPACITY, **value}\n\n\nDEFAULT_STYLE = dict")
  t=t.replace("result = {}","result = {}\n        if 'opacity' in data: result['opacity'] = validate_opacity(data['opacity'])",1)
  t=t.replace('def apply_theme(style):','def apply_theme(style, opacity):')
  t=t.replace("    if style['windows']: kitty +=", "    kitty += 'background_opacity ' + str(opacity['terminal'] / 100) + '\\n'\n    if style['windows']: kitty +=")
  t=t.replace("', 0.85); }'", "', ' + str(opacity['files'] / 100) + '); }'")
  start=t.index("    rofi += 'launcherbox");end=t.index("    if style['buttons']:",start)
  t=t[:start]+"""    alpha = f"{round(opacity['rofi'] * 255 / 100):02x}"
    rofi += 'launcherbox, inputbar, button { background-color: ' + window_surface + alpha + '; }\\n'
"""+t[end:]
  t=t.replace('    apply_theme(effective)','    opacity = validate_opacity(values.get("opacity", {}))\n    apply_theme(effective, opacity)')
  t=t.replace('return dict(style=values.get', 'return dict(opacity=opacity, style=values.get')
  t=t.replace("    elif len(args) == 2 and args[0] == 'environment-style':", """    elif len(args) == 2 and args[0] == 'opacity':
        update = json.loads(args[1])
        validate_opacity(update)
        values = local()
        values['opacity'] = validate_opacity({**values.get('opacity', {}), **update})
        save(values)
    elif len(args) == 2 and args[0] == 'environment-style':""")
 if rel.endswith('Appearance.qml'):
  t=t.replace('    readonly property color iconColor:', '''    readonly property var opacityDefaults: ({bar: 93, menus: 95, terminal: 85, files: 85, rofi: 85})
    function opacityPercent(key) {
        var values = state.opacity || opacityDefaults
        return values[key] === undefined ? opacityDefaults[key] : values[key]
    }
    function backgroundColor(value, target) {
        var shade = Qt.color(value)
        return Qt.rgba(shade.r, shade.g, shade.b, opacityPercent(target) / 100)
    }
    readonly property color capsuleSurface: backgroundColor("#15171f", "bar")
    function setOpacity(key, value) {
        var update = {}; update[key] = Math.round(value)
        change("opacity", JSON.stringify(update))
    }
    readonly property color iconColor:''')
 if rel.endswith('PersonalizationPanel.qml'):
  marker='    Rectangle { width: parent.width; height: 1; color: "#414654" }'
  controls='''    Rectangle { width: parent.width; height: 1; color: "#414654" }
    Caption { text: "Opacidade deste Environment"; color: "#e1e5f0"; font.pixelSize: Appearance.titleSize }
    Repeater {
        model: [{key: "bar", label: "Barra"}, {key: "menus", label: "Menus APX"}, {key: "terminal", label: "Terminal"}, {key: "files", label: "Gestor de ficheiros"}, {key: "rofi", label: "Rofi"}]
        Column {
            id: opacityRow
            required property var modelData
            width: panel.width; spacing: 2
            Row {
                width: parent.width
                Text { width: parent.width - 48; text: opacityRow.modelData.label; color: "#e1e5f0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize }
                Text { width: 48; horizontalAlignment: Text.AlignRight; text: Math.round(opacitySlider.value) + "%"; color: "#e1e5f0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize }
            }
            ControlSlider {
                id: opacitySlider
                width: parent.width; height: 36; from: 0; to: 100; stepSize: 1
                activeFocusOnTab: true; enabled: !Appearance.busy
                Accessible.name: "Opacidade: " + opacityRow.modelData.label
                Binding { target: opacitySlider; property: "value"; value: Appearance.opacityPercent(opacityRow.modelData.key); when: !opacitySlider.pressed && !opacitySave.running }
                onMoved: if (!pressed) opacitySave.restart()
                onPressedChanged: if (!pressed) opacitySave.restart()
            }
            Timer { id: opacitySave; interval: 180; onTriggered: Appearance.setOpacity(opacityRow.modelData.key, opacitySlider.value) }
        }
    }
    Caption { text: "0% transparente · 100% opaco. O gestor de ficheiros pode precisar de ser reaberto."; font.pixelSize: Appearance.metaSize }
'''
  assert marker in t;t=t.replace(marker,controls+marker,1)
 if rel.endswith('shell.qml'):
  start=t.index('    // Original panel opacity.');end=t.index('\n',t.index('    property color popupPanel:',start))
  t=t[:start]+'''    // Background alpha is independent of foreground and animation opacity.
    property color panel: Appearance.backgroundColor("#101117", "menus")
    property color popupPanel: Appearance.backgroundColor("#101117", "menus")'''+t[end:]
  t=t.replace('Appearance.tintButtons ? Appearance.barSurface : "#ed15171f"','Appearance.capsuleSurface')
 if rel.endswith(('BarButton.qml','MediaIsland.qml')):
  t=t.replace('(Appearance.tintButtons ? Appearance.barSurface : "#ed15171f")','Appearance.capsuleSurface')
 dest=a/'assets'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(t)
(a/'transform.py').write_text('from pathlib import Path\nRELATIVES='+repr(rels)+'\ndef transform(rel,s):\n return (Path(__file__).parent/"assets"/rel).read_text()\n')
d=(r/'scripts/physical-pilot/deploy-personalization-compact-20261017.py').read_text().replace('personalization-compact','opacity').replace('personalization_compact','opacity')
(r/'scripts/physical-pilot/deploy-opacity-20261017.py').write_text(d)
v=(r/'audit/2026-10-17-personalization-compact/validate-candidate.py').read_text().replace('personalization-compact','opacity').replace('personalization-validation','opacity-validation')
(a/'validate-candidate.py').write_text(v)
