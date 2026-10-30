import ast
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-settings'


class SettingsScaleTests(unittest.TestCase):
    def options(self, width, height):
        tree = ast.parse(SOURCE.read_text())
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'display_scales')
        scope = {}; exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), 'exec'), scope)
        return scope['display_scales'](width, height)

    def test_standard_label_and_unsupported_scale(self):
        options = dict(self.options(1920, 1080))
        self.assertEqual(options['1.25'], '100% · Padrão APX')
        self.assertNotIn('1.75', options)
        self.assertIn('1.5', options)

    def test_all_offered_scales_are_compatible_with_each_resolution(self):
        for width, height in [(1920,1080),(1680,1050),(1280,1024),(1440,900),(1280,800),(1280,720),(1024,768),(800,600),(640,480)]:
            options = self.options(width, height)
            self.assertTrue(options)
            for key, _label in options:
                self.assertTrue((width/float(key)).is_integer())
                self.assertTrue((height/float(key)).is_integer())


if __name__ == '__main__': unittest.main()
