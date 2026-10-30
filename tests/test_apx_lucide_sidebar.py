"""GTK symbolic rendering must preserve the outline geometry of Lucide icons."""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sidebar_icons',ROOT/'scripts/physical-pilot/build-thunar-lucide-icons-20261019.py')
icons=importlib.util.module_from_spec(spec)
spec.loader.exec_module(icons)

class SidebarLucideTests(unittest.TestCase):
    def test_all_outline_shapes_use_gtk_stroke_class(self):
        for group in icons.SIDEBAR.values():
            for name in group:
                root=E.fromstring(icons.gtk_symbolic((icons.SOURCES/(name+'.svg')).read_text()))
                for shape in root:
                    kind=shape.tag.rsplit('}',1)[-1]
                    self.assertNotIn(kind,('line','polygon','polyline'))
                    if shape.get('fill',root.get('fill','none'))=='none':
                        self.assertEqual(shape.get('class'),'stroke',name)

    def test_line_conversion_preserves_endpoints(self):
        svg='<svg xmlns="http://www.w3.org/2000/svg" fill="none"><line x1="2" y1="3" x2="8" y2="9"/></svg>'
        shape=list(E.fromstring(icons.gtk_symbolic(svg)))[0]
        self.assertEqual(shape.get('d'),'M2 3L8 9')
        self.assertEqual(shape.get('class'),'stroke')
