import importlib.util
import importlib.machinery
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HELPER = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-folder-color-v1'
spec = importlib.util.spec_from_loader('folder_color', importlib.machinery.SourceFileLoader('folder_color', str(HELPER)))
color = importlib.util.module_from_spec(spec)
spec.loader.exec_module(color)


class FolderColors(unittest.TestCase):
    def test_color_reset_preserves_contents(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'XDG_CACHE_HOME': directory}):
            folder = Path(directory) / 'Pasta com espaços'; folder.mkdir()
            document = folder / 'documento.txt'; document.write_text('preservar')
            color.set_color(folder, '#79baff')
            self.assertEqual((folder / color.MARKER).read_text().strip(), '#79baff')
            color.set_color(folder, '')
            self.assertFalse((folder / color.MARKER).exists())
            self.assertEqual(document.read_text(), 'preservar')

    def test_rejects_symlink_marker_and_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory); victim = folder / 'original'; victim.write_text('preservar')
            (folder / color.MARKER).symlink_to(victim)
            with self.assertRaises(ValueError): color.set_color(folder, '#79baff')
            self.assertEqual(victim.read_text(), 'preservar')
            link = folder / 'link'; link.symlink_to(folder, target_is_directory=True)
            with self.assertRaises(ValueError): color.folder(link)

    def test_invalid_names_and_colors(self):
        for name in ('', '..', '.', 'a/b', 'a\0b'):
            with self.assertRaises(ValueError): color.valid_name(name)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError): color.set_color(directory, '#123456')

class FolderTags(unittest.TestCase):
    def test_tags_roundtrip_and_reset(self):
        with tempfile.TemporaryDirectory() as directory:
            color.set_tags(directory, ' faculdade, projetos, faculdade, investigação ')
            self.assertEqual(color.read_tags(directory), ['faculdade', 'projetos', 'investigação'])
            color.set_tags(directory, '')
            self.assertEqual(color.read_tags(directory), [])
            self.assertFalse((Path(directory) / color.TAGS_MARKER).exists())

    def test_tag_changes_invalidate_only_own_thumbnail(self):
        import hashlib
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'XDG_CACHE_HOME': directory}):
            folder = Path(directory) / 'Projeto'; folder.mkdir()
            cache = Path(directory) / 'thumbnails/normal'; cache.mkdir(parents=True)
            name = hashlib.md5(folder.as_uri().encode(), usedforsecurity=False).hexdigest() + '.png'
            own = cache / name; own.write_bytes(b'cached')
            unrelated = cache / 'other.png'; unrelated.write_bytes(b'preservar')
            color.set_tags(folder, 'faculdade')
            self.assertFalse(own.exists())
            self.assertEqual(unrelated.read_bytes(), b'preservar')
            own.write_bytes(b'cached')
            color.set_tags(folder, '')
            self.assertFalse(own.exists())

    def test_tags_reject_unsafe_markers_and_invalid_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            victim = path / 'documento'; victim.write_text('preservar')
            (path / color.TAGS_MARKER).symlink_to(victim)
            with self.assertRaises(ValueError): color.set_tags(path, 'faculdade')
            self.assertEqual(victim.read_text(), 'preservar')
            self.assertEqual(color.read_tags(path), [])
            with self.assertRaises(ValueError): color.set_tags(path, 'a' * 65)
