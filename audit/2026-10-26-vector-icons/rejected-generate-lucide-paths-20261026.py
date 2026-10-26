#!/usr/bin/env python3
"""Compile the local Lucide SVG geometry for Qt Quick's GPU curve renderer."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
BASE = Path(__file__).resolve().parents[2] / 'config/environment-shell-v1/quickshell/apx'
def path_data(node):
    tag = node.tag.split('}')[-1]
    a = node.attrib
    if tag == 'path':
        d = a['d'].strip()
        assert d[0] in 'mM'
        return 'M' + d[1:]
    if tag == 'line':
        return f"M{a['x1']} {a['y1']} L{a['x2']} {a['y2']}"
    if tag == 'polyline':
        return 'M' + a['points']
    if tag == 'circle':
        x,y,r = (float(a[k]) for k in ('cx','cy','r'))
        return f'M{x-r:g} {y:g} a{r:g} {r:g} 0 1 0 {2*r:g} 0 a{r:g} {r:g} 0 1 0 {-2*r:g} 0 Z'
    if tag == 'rect':
        x,y,w,h = (float(a.get(k,0)) for k in ('x','y','width','height'))
        rx=min(float(a.get('rx',a.get('ry',0))),w/2)
        ry=min(float(a.get('ry',a.get('rx',0))),h/2)
        if not rx or not ry:
            return f'M{x:g} {y:g} h{w:g} v{h:g} h{-w:g} Z'
        return (f'M{x+rx:g} {y:g} H{x+w-rx:g} A{rx:g} {ry:g} 0 0 1 {x+w:g} {y+ry:g} '
                f'V{y+h-ry:g} A{rx:g} {ry:g} 0 0 1 {x+w-rx:g} {y+h:g} '
                f'H{x+rx:g} A{rx:g} {ry:g} 0 0 1 {x:g} {y+h-ry:g} '
                f'V{y+ry:g} A{rx:g} {ry:g} 0 0 1 {x+rx:g} {y:g} Z')
    raise ValueError(tag)
paths = {}
for p in sorted((BASE / 'icons/lucide').glob('*.svg')):
    root=ET.fromstring(p.read_bytes())
    assert root.get('viewBox') == '0 0 24 24'
    assert root.get('stroke-width') == '2' and root.get('fill') == 'none'
    assert root.get('stroke-linecap') == 'round' and root.get('stroke-linejoin') == 'round'
    assert all(set(n.attrib) <= {'d','x','y','width','height','rx','ry','cx','cy','r','x1','x2','y1','y2','points'} for n in root)
    paths[p.stem] = ' '.join(path_data(n) for n in root)
(BASE / 'LucidePaths.js').write_text('// Generated from icons/lucide/*.svg; run scripts/physical-pilot/generate-lucide-paths-20261026.py.\n.pragma library\nvar paths = ' + json.dumps(paths,indent=2) + ';\n')
print(f'Compiled {len(paths)} original SVG geometries')
