"""Icon persistence crosses Hub/workload boundaries without reading Hub home."""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from test_apx_environment_switch_v1 import load_contract, load_switch_service, load_metadata_runner


class EnvironmentIconTests(unittest.TestCase):
    generation = '12345678-1234-4234-9234-123456789abc'

    def test_contract_roundtrip_and_invalid_icons(self):
        c = load_contract()
        for icon in c.ENVIRONMENT_ICONS:
            raw = c.request_bytes('environment.update-metadata', 'games', self.generation,
                                  description='', display_name='Games', icon=icon)
            self.assertEqual(c.parse_message(raw)['payload']['icon'], icon)
        for icon in ('../x', '', [], None):
            payload = dict(target='games', generation=self.generation, description='', display_name='Games', icon=icon)
            raw = (json.dumps(dict(schema=1, profile=c.PROFILE, operation='environment.update-metadata', payload=payload))+'\n').encode()
            with self.assertRaises(ValueError):
                c.parse_message(raw)
        with self.assertRaises(ValueError):
            c.request_bytes('identity.get', icon='swords')

    def test_saved_icon_survives_private_hub_and_matches_generation(self):
        runner, service = load_metadata_runner(), load_switch_service()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); base.chmod(0o700)
            home = base/'games'; home.mkdir(mode=0o700)
            registration = home/'registration.json'
            record = dict(schema=1, name='games', role='graphical-base', release='hyprland-base-v2',
                          state='stopped', generation=self.generation, display_name='Games', description='')
            registration.write_text(json.dumps(record)); registration.chmod(0o600)
            with mock.patch.object(runner, 'ENVIRONMENTS', base), mock.patch.object(runner, 'NATIVE_ENVIRONMENTS', base/'native'), mock.patch.object(service, 'ENVIRONMENTS', base):
                runner.update_metadata('games', self.generation, 'Games', '', 'swords')
                self.assertEqual(service.selected_environment_icon(record), 'swords')
                self.assertEqual(service.environment_view(record)['icon'], 'swords')
                runner.update_metadata('games', self.generation, 'Renamed', 'New description')
                self.assertEqual(service.selected_environment_icon(record), 'swords')
                self.assertEqual(service.selected_environment_icon(dict(record, generation='different')), 'box')
                with mock.patch.object(service, 'trusted_native_environment', side_effect=FileNotFoundError), mock.patch.object(service.native_v3, 'catalogue', return_value=[]):
                    self.assertEqual(service.catalog()[0]['icon'], 'swords')
                with self.assertRaises(RuntimeError):
                    runner.update_metadata('games', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Games', '', 'pickaxe')
                self.assertEqual(service.selected_environment_icon(record), 'swords')
                iconfile = base/f'.icon-games-{self.generation}.json'
                iconfile.write_text('bad json')
                self.assertEqual(service.selected_environment_icon(record), 'box')
                iconfile.unlink(); iconfile.symlink_to(registration)
                self.assertEqual(service.selected_environment_icon(record), 'box')

    def test_shell_uses_authoritative_catalog_and_identity(self):
        s = (Path(__file__).resolve().parents[1]/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
        self.assertNotIn('apx-environment-icons.ini', s)
        self.assertIn('"--icon", environmentEditIcon', s)
        self.assertIn('iconName: root.activeEnvironmentIcon', s)
        self.assertIn('name: root.activeEnvironmentIcon', s)
        self.assertIn('environmentIcon(environmentIdentity)', s)

    def test_picker_matches_contract_and_all_assets_exist(self):
        root = Path(__file__).resolve().parents[1]
        shell = root/'config/environment-shell-v1/quickshell/apx'
        choices = json.loads(re.search(r'environmentIconChoices: (\[[^\n]+\])', (shell/'shell.qml').read_text())[1])
        self.assertEqual(len(choices), len(set(choices)))
        self.assertEqual(set(choices), load_contract().ENVIRONMENT_ICONS)
        for icon in choices:
            with self.subTest(icon=icon):
                self.assertEqual(ET.parse(shell/'icons/lucide'/f'{icon}.svg').getroot().tag,
                                 '{http://www.w3.org/2000/svg}svg')
