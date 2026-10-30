import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-rofi-files-v1'
loader = importlib.machinery.SourceFileLoader('rofi_files', str(PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)


class FileSearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        self.old = m.HOME
        m.HOME = self.home

    def tearDown(self):
        m.HOME = self.old
        self.temp.cleanup()

    def test_home_files_view_hides_application_catalogue_only(self):
        apps = self.home / 'Applications'; apps.mkdir()
        (apps / 'sample.desktop').write_text('[Desktop Entry]\nType=Application\nName=Sample\n')
        docs = self.home / 'Documents'; docs.mkdir()
        nested = docs / 'Applications'; nested.mkdir()
        rows = m.json_directory(str(self.home))['entries']
        self.assertNotIn(str(apps), [row['path'] for row in rows])
        self.assertEqual([row['path'] for row in m.json_directory(str(docs))['entries'] if row['label'] == 'Applications'], [str(nested)])
        self.assertTrue((apps / 'sample.desktop').is_file())

    def test_folder_tags_are_searchable_in_direct_and_recursive_views(self):
        import json
        parent = self.home / 'Projetos'; parent.mkdir()
        folder = parent / 'Trabalho'; folder.mkdir()
        (folder / '.apx-folder-tags').write_text(json.dumps(['faculdade', 'investigação']))
        for rows in (list(m.entries(parent)), list(m.entries(self.home, recursive=True))):
            matches = [label for path, label, _ in rows if path == folder]
            self.assertEqual(len(matches), 1)
            self.assertIn('faculdade', matches[0])
            self.assertIn('investigação', matches[0])
        (folder / '.apx-folder-tags').write_text('invalid json')
        self.assertEqual(m.folder_tags(folder), [])

    def test_tags_only_search_excludes_hidden_and_linked_folders(self):
        import json
        folder = self.home / 'Projeto'; folder.mkdir()
        (folder / '.apx-folder-tags').write_text(json.dumps(['faculdade']))
        hidden = self.home / '.Oculta'; hidden.mkdir()
        (hidden / '.apx-folder-tags').write_text(json.dumps(['faculdade']))
        (self.home / 'Ligação').symlink_to(folder, target_is_directory=True)
        rows = list(m.tagged_entries(self.home))
        self.assertEqual([path for path, _, _ in rows], [folder])
        self.assertIn('#faculdade', rows[0][1])
        self.assertEqual(rows[0][2], 'apx-folder-tagged')

    def test_tags_search_can_use_explicit_external_local_root(self):
        import contextlib, io, json, os
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as external:
            root = Path(external)
            (root / '.apx-folder-tags').write_text(json.dumps(['usb']))
            output = io.StringIO()
            with patch('sys.argv', ['helper', '--tags-only', '--root', str(root)]), patch.dict(os.environ, {'ROFI_DATA': '', 'ROFI_INFO': '', 'ROFI_RETV': '0'}), contextlib.redirect_stdout(output):
                m.main()
            self.assertIn('#usb', output.getvalue())
            self.assertIn(str(root), output.getvalue())
            state = json.dumps({'directory': str(root), 'tags_only': True})
            with patch('sys.argv', ['helper', '--tags-only', '--root', str(root)]), patch.dict(os.environ, {'ROFI_DATA': state, 'ROFI_INFO': str(root), 'ROFI_RETV': '1'}), patch.object(m, 'spawn') as launch:
                m.main()
            launch.assert_called_once_with(['thunar', str(root)])

    def test_standard_search_includes_tags_without_fake_tag_search_folder(self):
        import contextlib, io, json, os
        from unittest.mock import patch
        folder = self.home / 'Projeto'; folder.mkdir()
        (folder / '.apx-folder-tags').write_text(json.dumps(['faculdade']))
        output = io.StringIO()
        with patch('sys.argv', ['helper']), patch.dict(os.environ, {'ROFI_DATA': '', 'ROFI_INFO': '', 'ROFI_RETV': '0'}), contextlib.redirect_stdout(output):
            m.main()
        rows = output.getvalue()
        self.assertIn('#faculdade', rows)
        self.assertNotIn('search-tags', rows)
        self.assertNotIn('Pesquisar por etiquetas', rows)
        self.assertIn('\x1fmeta\x1fProjeto faculdade', rows)

    def test_rofi_selected_label_argument_does_not_break_folder_navigation(self):
        import contextlib, io, json, os
        from unittest.mock import patch
        folder = self.home / 'Pasta com espaços'; folder.mkdir()
        (folder / 'documento.txt').touch()
        output = io.StringIO()
        with patch('sys.argv', ['helper', 'Pasta com espaços  ·  #faculdade']), patch.dict(os.environ, {'ROFI_RETV': '1', 'ROFI_INFO': str(folder), 'ROFI_DATA': ''}), contextlib.redirect_stdout(output):
            m.main()
        state_line = next(line for line in output.getvalue().splitlines() if line.startswith('\0data'))
        self.assertEqual(json.loads(state_line.split('\x1f', 1)[1])['directory'], str(folder))
        self.assertIn('documento.txt', output.getvalue())
        self.assertNotIn('Pesquisar nas subpastas', output.getvalue())
        with patch('sys.argv', ['helper', 'documento.txt']), patch.dict(os.environ, {'ROFI_RETV': '1', 'ROFI_INFO': str(folder / 'documento.txt'), 'ROFI_DATA': ''}), patch.object(m, 'spawn') as launch:
            m.main()
        launch.assert_called_once_with(['xdg-open', str(folder / 'documento.txt')])

    def test_nested_files_and_folder_navigation(self):
        folder = self.home / 'Artigos'
        folder.mkdir()
        article = folder / 'Ensaio com espaços.pdf'
        article.touch()
        rows = list(m.entries(self.home))
        self.assertEqual(rows[0], (folder, 'Artigos', 'folder'))
        self.assertNotIn(article, [p for p, _, _ in rows])
        self.assertIn((article, 'Ensaio com espaços.pdf  ·  Artigos', 'text-x-generic'), list(m.entries(self.home, recursive=True)))
        self.assertEqual(list(m.entries(folder))[0], (self.home, 'Pasta anterior', 'go-up'))
        self.assertEqual(m.current_directory(str(folder)), folder)

    def test_hidden_files_and_external_symlinks_excluded(self):
        (self.home / '.private').mkdir()
        (self.home / '.private/secret').touch()
        (self.home / '.hidden').touch()
        with tempfile.TemporaryDirectory() as external:
            outside = Path(external) / 'outside'
            outside.touch()
            (self.home / 'link').symlink_to(outside)
            self.assertEqual(list(m.entries(self.home)), [])
            self.assertEqual(m.current_directory(external), self.home)

    def test_symlink_loop_not_traversed(self):
        (self.home / 'loop').symlink_to(self.home, target_is_directory=True)
        (self.home / 'document.txt').touch()
        rows = list(m.entries(self.home, recursive=True))
        self.assertEqual(sum(p.name == 'document.txt' for p, _, _ in rows), 1)

    def test_deep_paths_keep_relative_labels_and_safe_file_links(self):
        folder = self.home / 'Backup' / 'Sistema' / 'Documentos'
        folder.mkdir(parents=True)
        document = folder / 'Ensaio.pdf'
        document.touch()
        internal = folder / 'Ligação.pdf'
        internal.symlink_to(document)
        with tempfile.TemporaryDirectory() as external:
            outside = Path(external) / 'segredo.pdf'
            outside.touch()
            (folder / 'Externa.pdf').symlink_to(outside)
            (folder / 'Pasta externa').symlink_to(Path(external), target_is_directory=True)
            direct = list(m.entries(folder))
            recursive = list(m.entries(self.home, recursive=True))
        self.assertIn((document, 'Ensaio.pdf', 'text-x-generic'), direct)
        self.assertIn((internal, 'Ligação.pdf', 'text-x-generic'), direct)
        self.assertIn((document, 'Ensaio.pdf  ·  Backup/Sistema/Documentos', 'text-x-generic'), recursive)
        self.assertIn(internal, [path for path, _, _ in recursive])
        for rows in (direct, recursive):
            self.assertNotIn('Externa.pdf', [path.name for path, _, _ in rows])
            self.assertNotIn('segredo.pdf', [path.name for path, _, _ in rows])

    def test_json_lists_only_requested_directory_without_reading_large_files(self):
        import os
        from unittest.mock import patch
        folder = self.home / 'Downloads'; folder.mkdir()
        nested = folder / 'Backup'; nested.mkdir()
        (nested / 'Não carregar.txt').touch()
        large = folder / 'Grande.zip'
        with large.open('wb') as stream:
            stream.truncate(20 * 1024 ** 3)
        original_open = Path.open
        scans = []
        original_scan = os.scandir
        def guarded_open(path, *args, **kwargs):
            if path == large:
                raise AssertionError('Large archive contents must not be read')
            return original_open(path, *args, **kwargs)
        def scan(path):
            scans.append(Path(path))
            return original_scan(path)
        with patch.object(Path, 'open', guarded_open), patch.object(os, 'scandir', scan), patch.object(os, 'walk', side_effect=AssertionError('No recursive traversal')):
            page = m.json_directory(folder)
        self.assertEqual(scans, [folder])
        self.assertEqual([row['label'] for row in page['entries']], ['Pasta anterior', 'Backup', 'Grande.zip'])
        self.assertEqual(page['entries'][-1]['icon'], 'package-x-generic')
        self.assertEqual(page['entries'][-1]['kind'], 'file')
        self.assertNotIn('Não carregar.txt', [row['label'] for row in page['entries']])

    def test_default_script_home_does_not_load_descendants(self):
        import contextlib, io, os
        from unittest.mock import patch
        folder = self.home / 'Downloads'; folder.mkdir()
        (folder / 'Dentro.txt').touch()
        output = io.StringIO()
        with patch('sys.argv', ['helper']), patch.dict(os.environ, {'ROFI_DATA': '', 'ROFI_INFO': '', 'ROFI_RETV': '0'}), contextlib.redirect_stdout(output):
            m.main()
        self.assertIn('Downloads', output.getvalue())
        self.assertNotIn('Dentro.txt', output.getvalue())

    def test_json_external_directory_and_open_external_link_are_rejected(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as external:
            root = Path(external)
            file = root / 'documento.txt'; file.touch()
            link = self.home / 'Externo.txt'; link.symlink_to(file)
            with self.assertRaises(ValueError):
                m.json_directory(root)
            with patch.object(m, 'spawn') as launch:
                m.open_entry(str(link))
            launch.assert_not_called()

    def test_application_shortcut_names_and_external_targets(self):
        folder = self.home / 'Applications'
        folder.mkdir()
        with tempfile.TemporaryDirectory() as external:
            target = Path(external) / 'strange-name.desktop'
            target.write_text('[Desktop Entry]\nType=Application\nName=Friendly App\nIcon=app-icon\nExec=/usr/bin/true\n')
            shortcut = folder / target.name
            shortcut.symlink_to(target)
            self.assertIn((shortcut, 'Friendly App', 'app-icon'), list(m.entries(folder)))
            target.write_text(target.read_text() + 'NoDisplay=true\n')
            self.assertIsNone(m.desktop_entry(shortcut))
            self.assertNotIn(shortcut, [p for p, _, _ in m.entries(folder)])


if __name__ == '__main__':
    unittest.main()
