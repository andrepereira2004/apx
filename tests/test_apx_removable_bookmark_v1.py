import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-removable-bookmark-v1'
loader = importlib.machinery.SourceFileLoader('usb_bookmark', str(SOURCE))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)


class UsbBookmarks(unittest.TestCase):
    def test_insert_and_unplug_preserve_other_bookmarks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bookmarks'
            original = 'file:///home/apx/Documents Documentos\nfile:///home/apx/Applications Aplicações\n'
            path.write_text(original + 'file:///media/apx-usb PEN USB\n')
            self.assertTrue(m.refresh(path, present=False))
            self.assertEqual(path.read_text(), original)
            self.assertTrue(m.refresh(path, present=True))
            self.assertEqual(path.read_text(), original + m.URI + ' PEN USB\n')
            self.assertFalse(m.refresh(path, present=True))
            self.assertTrue(m.refresh(path, present=False))
            self.assertEqual(path.read_text(), original)

    def test_disconnected_does_not_create_empty_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bookmarks'
            self.assertFalse(m.refresh(path, present=False))
            self.assertFalse(path.exists())

    def test_linked_bookmark_file_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'original'; target.write_text('preservar')
            path = Path(directory) / 'bookmarks'; path.symlink_to(target)
            with self.assertRaises(ValueError): m.refresh(path, present=True)
            self.assertEqual(target.read_text(), 'preservar')
