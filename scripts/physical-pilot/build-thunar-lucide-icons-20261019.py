#!/usr/bin/env python3
"""Map GTK icon names to bundled official Lucide SVG geometry."""
from pathlib import Path
import configparser
import io
import re
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[2]
THEME = REPO/'config/environment-shell-v1/local/share/icons/APX-Graphite'
SOURCES = Path(__file__).with_name('lucide-file-manager-v1')
# Symbolic sidebar names only. Normal folder/file artwork and toolbar action
# names deliberately retain the original theme.
SIDEBAR = {'places': {'folder': 'folder folder-templates folder-publicshare',
            'folder-open': 'folder-open folder-documents',
            'folder-down': 'folder-download',
            'image': 'folder-pictures',
            'music': 'folder-music',
            'video': 'folder-videos',
            'folder-search': 'folder-saved-search',
            'folder-symlink': 'folder-remote',
            'monitor': 'user-desktop',
            'house': 'user-home',
            'trash-2': 'user-trash user-trash-full',
            'network': 'network-workgroup network-server',
            'clock': 'document-open-recent'},
 'devices': {'hard-drive': 'drive-harddisk drive-harddisk-solidstate drive drive-removable-media',
             'usb': 'drive-removable-media-usb drive-harddisk-usb '
                    'drive-removable-media-usb-pendrive',
             'disc': 'drive-optical media-optical',
             'computer': 'computer',
             'smartphone': 'phone multimedia-player',
             'printer': 'printer scanner'},
 'actions': {'eject': 'media-eject'}}

def gtk_symbolic(svg):
    """GTK3 forces path/circle fills unless the geometry has class=stroke.

    Convert line/polyline primitives to equivalent paths so GTK's symbolic
    foreground CSS recolors their outlines too. Preserve the Lucide geometry.
    """
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    root=ET.fromstring(svg)
    for element in root.iter():
        kind=element.tag.rsplit('}',1)[-1]
        if kind == 'line':
            x1,y1,x2,y2=(element.attrib.pop(key,'0') for key in ('x1','y1','x2','y2'))
            element.tag='{http://www.w3.org/2000/svg}path'
            element.set('d', f'M{x1} {y1}L{x2} {y2}')
            kind='path'
        elif kind in ('polyline','polygon'):
            points=re.split(r'[ ,]+',element.attrib.pop('points').strip())
            element.tag='{http://www.w3.org/2000/svg}path'
            element.set('d','M'+' '.join(points[:2])+''.join('L'+' '.join(points[i:i+2]) for i in range(2,len(points),2))+('Z' if kind=='polygon' else ''))
            kind='path'
        if kind in ('path','rect','circle') and element.get('fill', root.get('fill', 'none')) == 'none':
            element.set('class','stroke')
    root.set('stroke','#c7d0d8')
    return ET.tostring(root,encoding='unicode')+'\n'


def main():
    for context, mappings in SIDEBAR.items():
        directory=THEME/'scalable'/context
        directory.mkdir(parents=True,exist_ok=True)
        for name, aliases in mappings.items():
            svg=gtk_symbolic((SOURCES/(name+'.svg')).read_text())
            for alias in aliases.split():
                (directory/(alias+'-symbolic.svg')).write_text(svg)
    config=configparser.ConfigParser(interpolation=None);config.optionxform=str
    config['Icon Theme']=dict(Name='APX Graphite', Comment='Original folders with Lucide sidebar symbols',
                             Inherits='Adwaita,AdwaitaLegacy,hicolor',
                             Directories=','.join('scalable/'+c for c in SIDEBAR))
    for context in SIDEBAR:
        config['scalable/'+context]=dict(Size='48',MinSize='16',MaxSize='256',Type='Scalable',Context=context.title())
    stream=io.StringIO();config.write(stream,space_around_delimiters=False);(THEME/'index.theme').write_text(stream.getvalue().rstrip()+'\n')
    (THEME/'LICENSE-Lucide.txt').write_bytes((SOURCES/'LICENSE').read_bytes())

if __name__=='__main__':main()
