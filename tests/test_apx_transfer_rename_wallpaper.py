from pathlib import Path
import importlib.machinery
import json
import os
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('transfer_test', str(ROOT / 'scripts/physical-pilot/apx-transfer-v1.py'))
app = types.ModuleType(loader.name)
loader.exec_module(app)

class TransferTests(unittest.TestCase):
    def test_rename_files_directories_and_refuse_overwrite_escape_links(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root/'a').write_text('photo'); (root/'other').write_text('keep')
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                app.rename_entry(fd, ['a'], 'renamed')
                self.assertEqual((root/'renamed').read_text(), 'photo')
                with self.assertRaises(ValueError): app.rename_entry(fd, ['renamed'], 'other')
                for name in ['../escape', '', '.', '.apx-wallpaper-used']:
                    with self.assertRaises(ValueError): app.rename_entry(fd, ['renamed'], name)
                (root/'folder').mkdir(); app.rename_entry(fd, ['folder'], 'new-folder')
                (root/'link').symlink_to('/tmp', target_is_directory=True)
                with self.assertRaises(OSError): app.rename_entry(fd, ['link', 'anything'], 'else')
                with self.assertRaises(ValueError): app.rename_entry(fd, ['link'], 'else')
                self.assertEqual((root/'other').read_text(), 'keep')
            finally: os.close(fd)

    def test_usage_includes_stopped_registered_envs_and_current_image_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            digest = 'a'*64
            for name in ('one', 'two'):
                env = root/name; home = env/'home/apx'
                (env/'registration.json').parent.mkdir(parents=True); (env/'registration.json').write_text('{}')
                state = home/'.config/apx/appearance.json'; state.parent.mkdir(parents=True)
                state.write_text(json.dumps({'wallpaper':f'/home/apx/.local/share/apx/appearance/wallpapers/{digest}.png'}))
                image = home/f'.local/share/apx/appearance/wallpapers/{digest}.png'
                image.parent.mkdir(parents=True); image.write_bytes(b'png')
            self.assertEqual(sorted(app.wallpaper_usage(root)[digest]), ['one', 'two'])
            (root/'two/home/apx/.config/apx/appearance.json').write_text('{}')
            self.assertEqual(app.wallpaper_usage(root), {digest:['one']})
            (root/'one/registration.json').unlink()
            self.assertEqual(app.wallpaper_usage(root), {})
