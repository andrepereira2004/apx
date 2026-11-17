from pathlib import Path
import importlib.util
import tempfile
import threading
import unittest
import zipfile
import tarfile

SOURCE = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/lib/apx/apx_compression.py'
spec = importlib.util.spec_from_file_location('apx_compression', SOURCE)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class CompressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
    def world(self, name='World'):
        world = self.root/name; world.mkdir()
        (world/'level.dat').write_bytes(b'Bedrock test metadata')
        (world/'db').mkdir(); (world/'db/CURRENT').write_bytes(b'MANIFEST-000001\n')
        (world/'levelname.txt').write_text('APX World')
        return world
    def pack(self, name='Pack'):
        pack = self.root/name; pack.mkdir()
        (pack/'manifest.json').write_text('{"format_version":2,"header":{"name":"APX test"},"modules":[]}')
        (pack/'textures').mkdir(); (pack/'textures/sample.txt').write_text('APX')
        return pack
    def test_generic_zip_and_tar_preserve_selected_folder_and_spaces(self):
        source=self.root/'sample folder';source.mkdir();(source/'sample file.txt').write_text('APX\n')
        for kind in ('zip','tar','tar.gz','tar.xz'):
            output=self.root/('archive'+m.EXTENSIONS[kind]);m.create_archive([source],output,kind)
            if kind=='zip':
                with zipfile.ZipFile(output) as z:self.assertEqual(z.read('sample folder/sample file.txt'),b'APX\n')
            else:
                with tarfile.open(output) as t:self.assertEqual(t.extractfile('sample folder/sample file.txt').read(),b'APX\n')
    def test_mcworld_places_world_contents_at_archive_root(self):
        world=self.world();output=self.root/'world.mcworld';m.create_archive([world],output,'mcworld')
        with zipfile.ZipFile(output) as z:
            self.assertIn('level.dat',z.namelist());self.assertIn('db/CURRENT',z.namelist())
            self.assertNotIn('World/level.dat',z.namelist())
            self.assertEqual(z.read('levelname.txt'),b'APX World')
    def test_existing_nested_zip_is_repacked_instead_of_double_zipped(self):
        source=self.root/'world.zip'
        with zipfile.ZipFile(source,'w') as z:
            z.writestr('outer/inner/level.dat',b'data');z.writestr('outer/inner/db/CURRENT',b'current')
        output=self.root/'world.mcworld';m.create_archive([source],output,'mcworld')
        with zipfile.ZipFile(output) as z:self.assertEqual(set(z.namelist()),{'level.dat','db/CURRENT'})
    def test_mcpack_places_manifest_at_root(self):
        source=self.pack();output=self.root/'pack.mcpack';m.create_archive([source],output,'mcpack')
        with zipfile.ZipFile(output) as z:self.assertIn('manifest.json',z.namelist());self.assertEqual(z.read('textures/sample.txt'),b'APX')
    def test_mcaddon_contains_individually_valid_mcpack_containers(self):
        source=self.pack();output=self.root/'addon.mcaddon';m.create_archive([source],output,'mcaddon')
        with zipfile.ZipFile(output) as outer:
            self.assertEqual(outer.namelist(),['Pack.mcpack'])
            with outer.open('Pack.mcpack') as stream,zipfile.ZipFile(stream) as inner:self.assertIn('manifest.json',inner.namelist())
    def test_mcaddon_accepts_packaged_world_and_pack(self):
        world=self.world();pack=self.pack()
        w=self.root/'world.mcworld';p=self.root/'pack.mcpack'
        m.create_archive([world],w,'mcworld');m.create_archive([pack],p,'mcpack')
        output=self.root/'addon.mcaddon';m.create_archive([w,p],output,'mcaddon')
        with zipfile.ZipFile(output) as z:self.assertEqual(set(z.namelist()),{'world.mcworld','pack.mcpack'})
    def test_wrong_minecraft_structure_is_not_published(self):
        source=self.root/'Java world';source.mkdir();(source/'level.dat').write_text('data');(source/'region').mkdir()
        output=self.root/'wrong.mcworld'
        with self.assertRaisesRegex(ValueError,'Bedrock'):m.create_archive([source],output,'mcworld')
        self.assertFalse(output.exists())
        with self.assertRaisesRegex(ValueError,'manifest.json'):m.create_archive([source],self.root/'wrong.mcpack','mcpack')
    def test_existing_output_is_preserved(self):
        source=self.world();output=self.root/'existing.zip';output.write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):m.create_archive([source],output,'zip')
        self.assertEqual(output.read_bytes(),b'preserve')
    def test_cancel_during_large_file_removes_partial_archive(self):
        source=self.root/'large.bin';source.write_bytes(b'x'*(3*1024*1024));cancel=threading.Event();output=self.root/'cancel.zip'
        def report(*args):cancel.set()
        with self.assertRaises(m.Cancelled):m.create_archive([source],output,'zip',cancel,report)
        self.assertFalse(output.exists());self.assertEqual(list(self.root.glob('.apx-compress-*.part')),[])
    def test_zip_path_traversal_is_refused(self):
        source=self.root/'bad.zip'
        with zipfile.ZipFile(source,'w') as z:z.writestr('../level.dat',b'data')
        with self.assertRaisesRegex(ValueError,'caminho'):m.create_archive([source],self.root/'bad.mcworld','mcworld')
    def test_output_inside_selected_folder_is_refused(self):
        source=self.world()
        with self.assertRaisesRegex(ValueError,'destino'):m.create_archive([source],source/'inside.zip','zip')
    def test_formats_and_names_do_not_accumulate_extensions(self):
        self.assertEqual(m.with_extension('world.zip','mcworld'),'world.mcworld')
        self.assertEqual(m.with_extension('world.tar.gz','mcpack'),'world.mcpack')
        self.assertEqual(m.extension_for_name('WORLD.MCWORLD'),'mcworld')
        self.assertEqual(m.suggest_format([self.world()]),'mcworld')
    def test_publish_refuses_racing_existing_output(self):
        source=self.root/'finished.part';source.write_bytes(b'new');target=self.root/'archive.zip';target.write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):m.publish_no_replace(source,target)
        self.assertEqual(target.read_bytes(),b'preserve')

    def test_existing_addon_zip_is_repacked_and_inner_packages_checked(self):
        pack=self.pack();p=self.root/'pack.mcpack';m.create_archive([pack],p,'mcpack')
        source=self.root/'addon.zip'
        with zipfile.ZipFile(source,'w') as z:z.write(p,'outer/pack.mcpack')
        output=self.root/'addon.mcaddon';m.create_archive([source],output,'mcaddon')
        with zipfile.ZipFile(output) as z:self.assertEqual(z.namelist(),['pack.mcpack'])

    def test_bad_inner_pack_does_not_create_addon(self):
        source=self.root/'invalid.mcpack'
        with zipfile.ZipFile(source,'w') as z:z.writestr('outer/manifest.json','{}')
        with self.assertRaisesRegex(ValueError,'manifest.json'):
            m.create_archive([source],self.root/'invalid.mcaddon','mcaddon')
