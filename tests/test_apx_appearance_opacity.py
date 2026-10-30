import contextlib
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

HELPER = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-appearance-v1'

class OpacityTests(unittest.TestCase):
    def setUp(self):
        loader = importlib.machinery.SourceFileLoader('appearance_opacity', str(HELPER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.m = importlib.util.module_from_spec(spec)
        loader.exec_module(self.m)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.m.HOME = Path(self.tmp.name)
        self.m.STATE = self.m.HOME / '.config/apx/appearance.json'
        self.m.global_style = lambda: dict(self.m.DEFAULT_STYLE)

    def test_partial_changes_preserve_color_and_other_opacities(self):
        m = self.m
        m.save({'style': {**m.DEFAULT_STYLE, 'color': '#67d9ed'}})
        with contextlib.redirect_stdout(io.StringIO()):
            m.main(['opacity', '{"terminal":40}'])
            m.main(['opacity', '{"files":70}'])
        state = m.status()
        self.assertEqual(state['opacity']['terminal'], 40)
        self.assertEqual(state['opacity']['files'], 70)
        self.assertEqual(state['effective_icon_color'], '#67d9ed')
        self.assertIn('background_opacity 0.4', (m.HOME / '.config/kitty/apx-appearance.conf').read_text())
        self.assertIn('rgba(10, 16, 20, 0.7)', (m.HOME / '.config/gtk-3.0/gtk.css').read_text())

    def test_endpoints_and_repeated_generation(self):
        m = self.m
        for percent, alpha in [(0, '00'), (100, 'ff')]:
            m.save({'opacity': {'files': percent, 'rofi': percent, 'terminal': percent}})
            m.status()
            m.status()
            css = (m.HOME / '.config/gtk-3.0/gtk.css').read_text()
            self.assertEqual(css.count('APX appearance override BEGIN'), 1)
            self.assertIn('#0a1014' + alpha, (m.HOME / '.config/rofi/apx-appearance.rasi').read_text())

    def test_invalid_changes_are_rejected_without_writing(self):
        for value in [{'bar': -1}, {'files': 101}, {'rofi': True}, {'terminal': '50'}, {'unknown': 50}]:
            with self.assertRaises(ValueError):
                self.m.main(['opacity', json.dumps(value)])
        self.assertFalse(self.m.STATE.exists())

if __name__ == '__main__':
    unittest.main()
