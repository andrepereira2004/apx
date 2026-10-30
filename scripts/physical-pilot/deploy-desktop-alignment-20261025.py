#!/usr/bin/env python3
"""Bounded pilot deployment: shared desktop edges and shorter window motion."""
from pathlib import Path
import importlib.util
import fcntl
import sys

spec=importlib.util.spec_from_file_location('deploy',Path(__file__).with_name('deploy-controls-followup-20261020.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.AUDIT=m.REPO/'audit/2026-10-25-desktop-alignment';m.AUDIT.mkdir(exist_ok=True)
m.transform.RELATIVES=['quickshell/apx/Appearance.qml','quickshell/apx/shell.qml','hypr/hyprland.lua','local/bin/apx-shell-v1','quickshell/apx/ControlDashboard.qml','rofi/config.rasi','local/lib/rofi/apx-rofi-apps-v1.so','local/lib/rofi/apx-rofi-system-v1.so']
def transform(rel,text):
    if rel.endswith('ControlDashboard.qml'):
        text=text.replace('property real topCornerRadius: 18','property real topCornerRadius: Appearance.desktopCornerRadius').replace('radius: 18','radius: Appearance.desktopCornerRadius')
    elif rel.endswith('config.rasi'):
        text=text.replace('border-color: #343947; border-radius: 18px;', 'border-color: #343947; border-radius: 10px;')
    elif rel.endswith('apx-shell-v1'):
        anchor="# User-selected startup applications and optional clipboard history."
        if '# Keep the Environment-local file manager ready' not in text:
            text=text.replace(anchor, '# Keep the Environment-local file manager ready without blocking shell startup.\n# The existing Thunar daemon exits with this Environment session.\nif [[ -x /usr/bin/thunar ]]; then\n    start_desktop_service \'^/usr/bin/[Tt]hunar([[:space:]]|$)\' \\\n        /home/apx/.local/bin/thunar --daemon\nfi\n\n'+anchor)
    elif rel.endswith('Appearance.qml'):
        if 'desktopEdgeInset' not in text:
            text=text.replace('    id: appearance','    id: appearance\n    // Match Hyprland general.gaps_out; capsule borders share the tiled outer edge.\n    readonly property int desktopEdgeInset: 20')
        if 'desktopCornerRadius' not in text:
            text=text.replace('readonly property int desktopEdgeInset: 20','readonly property int desktopEdgeInset: 20\n    // Match Hyprland rounding=10 and rounding_power=2 (circular).\n    readonly property int desktopCornerRadius: 10')
    elif rel.endswith('shell.qml'):
        text=text.replace('radius: 15 + (20 - 15) * root.islandProgress','radius: Math.min(height / 2, Appearance.desktopCornerRadius)')
        text=text.replace('width: deviceRow.connected || !deviceRow.paired ? 108 : 68; height: Appearance.menuActionHeight', 'width: deviceRow.connected || !deviceRow.paired ? 104 : 68; height: 32; radius: 8')
        text=text.replace('if (!bar) return 19','if (!bar) return Appearance.desktopEdgeInset')
        text=text.replace('// Keep symmetric screen margins; button groups add an 8px inner inset.\n        margins { left: 8; right: 8 }','// Share outer edges with tiled application windows.\n        margins { left: Appearance.desktopEdgeInset; right: Appearance.desktopEdgeInset }')
        start=text.index('        id: barVariants');end=text.index('        id: popupDismissLayer',start)
        block=text[start:end].replace('anchors.leftMargin: 8','anchors.leftMargin: 0').replace('anchors.rightMargin: 8','anchors.rightMargin: 0')
        text=text[:start]+block+text[end:]
        text=text.replace('Math.max(8, Math.min(root.popupLeftMargin, popup.width - targetWidth - 8))','Math.max(Appearance.desktopEdgeInset, Math.min(root.popupLeftMargin, popup.width - targetWidth - Appearance.desktopEdgeInset))')
    else:
        for leaf,before,after in [('windows',2.2,3.2),('windowsIn',2.2,3.2),('fadeIn',2.2,3.2),('windowsOut',1.6,2.4),('fadeOut',1.6,2.4),('layersIn',3.0,3.2),('layersOut',1.4,2.4),('fadeLayersIn',3.0,3.2),('fadeLayersOut',1.4,2.4)]:
            import re
            text=re.sub(r'(leaf = "'+leaf+r'",[^\n]*?speed = )'+str(before).replace('.',r'\.'),lambda x:x[1]+str(after),text)
        import re
        for leaf in ('layersIn','fadeLayersIn'):
            text=re.sub(r'(leaf = "'+leaf+r'",[^\n]*?bezier = ")apxMenuOutCubic',lambda m:m[1]+'apxFluid',text)
        for leaf in ('layersOut','fadeLayersOut','windowsOut','fadeOut'):
            text=re.sub(r'(leaf = "'+leaf+r'",[^\n]*?bezier = ")[^"]+',lambda m:m[1]+'easeInOutCubic',text)
        start=text.index('    name = "apx-rofi-menu-motion"');end=text.index('\n})',start)
        text=text[:start]+text[start:end].replace('animation = "popin 97%"','animation = "slide bottom"')+text[end:]
        start=text.index('    name = "apx-thunar-menu-animation"');end=text.index('\n})',start)
        text=text[:start]+text[start:end].replace('popin 90%','popin 97%')+text[end:]
    return text
m.transform.transform=staticmethod(transform)
if __name__=='__main__':
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        m.main()
