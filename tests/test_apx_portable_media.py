import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import apx_removable_catalog as catalog
import apx_portable_profile as profile
spec=importlib.util.spec_from_file_location('portable_usb_test',ROOT/'scripts/portable/apx-portable-media.py')
media=importlib.util.module_from_spec(spec);spec.loader.exec_module(media)


class PortableMediaTests(unittest.TestCase):
    def tree(self):
        return {'blockdevices':[dict(name='/dev/sdz',type='disk',tran='usb',rm=True,serial='USBNEW123',mountpoints=[None],children=[
            dict(name='/dev/sdz1',type='part',fstype='exfat',uuid='A123-B456',mountpoints=[None])])]}

    def test_new_usb_does_not_require_pilot_uuid(self):
        self.assertEqual(media.admitted_volumes(self.tree()),(('A123-B456','exfat','USB-A123-B456','USBNEW123'),))
        tree=self.tree();tree['blockdevices'][0]['children'][0].update(fstype='ntfs',uuid='1234567890ABCDEF')
        self.assertEqual(media.admitted_volumes(tree),(('1234567890ABCDEF','ntfs','USB-1234567890ABCDEF','USBNEW123'),))

    def test_system_disks_and_mounted_data_are_never_claimed(self):
        for change in ('internal','nonremovable','mounted','host-partition'):
            tree=self.tree();disk=tree['blockdevices'][0]
            if change=='internal':disk['tran']='nvme'
            elif change=='nonremovable':disk['rm']=False
            elif change=='mounted':disk['children'][0]['mountpoints']=['/boot']
            else:disk['children'].append(dict(type='part',fstype='ext4',uuid='A123-B789',mountpoints=['/']))
            with self.subTest(change=change):self.assertEqual(media.admitted_volumes(tree),())

    def test_identity_filesystem_and_serial_must_be_valid(self):
        for field,value in [('uuid','../../root'),('fstype','crypto_LUKS'),('type','crypt')]:
            tree=self.tree();tree['blockdevices'][0]['children'][0][field]=value
            self.assertEqual(media.admitted_volumes(tree),())
        tree=self.tree();tree['blockdevices'][0]['serial']=None
        self.assertEqual(media.admitted_volumes(tree),())

    def test_duplicate_uuid_is_refused(self):
        tree=self.tree();tree['blockdevices'][0]['children']*=2
        with self.assertRaisesRegex(ValueError,'ambiguous'):media.admitted_volumes(tree)

    def test_usb_already_mounted_by_apx_remains_admitted(self):
        tree=self.tree();tree['blockdevices'][0]['children'][0]['mountpoints']=['/run/apx/removable-media-v1/USB-A123-B456']
        self.assertEqual(len(media.admitted_volumes(tree)),1)

    def test_public_catalogue_rejects_links_path_injection_and_writable_data(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'volumes.json';p.write_text(json.dumps({'A123-B456':{'name':'USB-A123-B456','label':'USB A123-B456'}}))
            p.chmod(0o644)
            self.assertEqual(catalog.read(p),{'A123-B456':('USB-A123-B456','USB A123-B456')})
            p.chmod(0o666)
            with self.assertRaises(ValueError):catalog.read(p)
            p.chmod(0o644);p.write_text(json.dumps({'A123-B456':{'name':'../../root','label':'USB A123-B456'}}))
            with self.assertRaises(ValueError):catalog.read(p)
            link=Path(temp)/'link';link.symlink_to(p)
            with self.assertRaises(ValueError):catalog.read(link)

    def test_portable_profile_requires_root_owned_regular_record(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'install.json'
            self.assertFalse(profile.installed(p))
            p.write_text(json.dumps(dict(schema=1,profile='portable-graphical-v1')));p.chmod(0o600)
            self.assertTrue(profile.installed(p))
            link=Path(temp)/'link';link.symlink_to(p)
            with self.assertRaises(ValueError):profile.installed(link)
            p.chmod(0o666)
            with self.assertRaises(ValueError):profile.installed(p)

    def test_generic_usb_request_has_syntax_and_backend_authorization_separate(self):
        from apx_host_services_v3_contract import request_bytes,parse_request,HostServicesV3ContractError
        self.assertEqual(parse_request(request_bytes('media.unmount',{'uuid':'A123-B456'}))[2],{'uuid':'A123-B456'})
        self.assertEqual(parse_request(request_bytes('media.unmount',{'uuid':'1234567890ABCDEF'}))[2],{'uuid':'1234567890ABCDEF'})
        for value in ('/dev/sda1','APX_ROOT','../A123-B456'):
            with self.assertRaises(HostServicesV3ContractError):request_bytes('media.unmount',{'uuid':value})


if __name__=='__main__':unittest.main()
