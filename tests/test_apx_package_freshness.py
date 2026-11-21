from pathlib import Path
import hashlib,io,json,sys,tarfile,tempfile,unittest,zipfile
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import apx_package_freshness as app

def make_package(path,name='brave-bin',version='1:1.0.0-1'):
 with tarfile.open(path,'w:zst') as archive:
  for name,data in {'.PKGINFO':f'pkgname = {name}\npkgver = {version}\narch = x86_64\nprovides = brave=1.0.0\nsize = 3\nbuilddate = 0\n'.encode(),'usr/bin/brave':b'APX launcher','opt/brave-bin/brave':b'old browser'}.items():
   item=tarfile.TarInfo(name);item.size=len(data);item.mode=0o755;archive.addfile(item,io.BytesIO(data))

class FreshnessTests(unittest.TestCase):
 def test_stable_metadata_rejects_prerelease(self):
  for value in ({'draft':False,'prerelease':True,'tag_name':'v2.0.0'},{'draft':False,'prerelease':False,'tag_name':'nightly'}):
   with mock.patch.object(app,'fetch',return_value=json.dumps(value).encode()):
    with self.assertRaises(app.FreshnessError):app.latest_release('brave/brave-browser')
 def test_assets_require_digest_and_supplier_url(self):
  release=dict(tag_name='v2.0.0',assets=[dict(name='browser.zip',digest='sha256:'+'a'*64,browser_download_url='https://evil.example/browser.zip')])
  with self.assertRaises(app.FreshnessError):app.github_asset(release,'brave/brave-browser','browser.zip')
 def test_new_brave_retains_integration_and_updates_metadata(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp);make_package(p/'old.zst')
   with zipfile.ZipFile(p/'new.zip','w') as z:z.writestr('brave',b'new browser');z.writestr('chrome-sandbox',b'sandbox')
   app.rebuild_brave(p/'old.zst',p/'new.zip',p/'new.zst','2.0.0')
   self.assertEqual(app.package_info(p/'new.zst')['pkgver'],'1:2.0.0-1')
   with tarfile.open(p/'new.zst','r:*') as archive:
    self.assertEqual(archive.extractfile('usr/bin/brave').read(),b'APX launcher')
    self.assertEqual(archive.extractfile('opt/brave-bin/brave').read(),b'new browser')
    self.assertEqual(archive.getmember('opt/brave-bin/chrome-sandbox').mode,0o4755)
 def test_no_stale_fallback_when_network_fails(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp);old=p/'brave-bin-old.pkg.tar.zst';make_package(old)
   manifest=p/'brave-bin-v1.json';before=json.dumps(dict(filename=old.name,sha256=hashlib.sha256(old.read_bytes()).hexdigest()));manifest.write_text(before)
   with mock.patch.object(app,'latest_release',side_effect=OSError('offline')):
    with self.assertRaises(OSError):app.ensure_current_package('brave-bin',old,p)
   self.assertEqual(manifest.read_text(),before)
 def test_current_brave_is_not_rebuilt(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp);old=p/'brave-bin-current.pkg.tar.zst';make_package(old)
   (p/'brave-bin-v1.json').write_text(json.dumps(dict(filename=old.name,sha256=hashlib.sha256(old.read_bytes()).hexdigest())))
   with mock.patch.object(app,'latest_release',return_value=dict(tag_name='v1.0.0')),mock.patch.object(app,'download',side_effect=AssertionError('unexpected download')):
    self.assertEqual(app.ensure_current_package('brave-bin',old,p),old)
 def test_brave_archive_refuses_parent_traversal(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp);make_package(p/'old.zst')
   with zipfile.ZipFile(p/'bad.zip','w') as z:z.writestr('../escape',b'bad')
   with self.assertRaises(app.FreshnessError):app.rebuild_brave(p/'old.zst',p/'bad.zip',p/'new.zst','2.0.0')

 def test_office_vendor_package_retains_expected_package_identity(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp);make_package(p/'old.zst','gridcraft','1.0.0-1')
   make_package(p/'vendor.zst','ai.storyteller.gridcraft','2.0.0-1')
   app.repackage_office(p/'old.zst',p/'vendor.zst',p/'new.zst','gridcraft','2.0.0')
   self.assertEqual(app.package_info(p/'new.zst')['pkgname'],'gridcraft')
   self.assertEqual(app.package_info(p/'new.zst')['pkgver'],'2.0.0-1')
