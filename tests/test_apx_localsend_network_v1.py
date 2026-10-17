from pathlib import Path
import importlib.util
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('localsend_network', ROOT / 'scripts/physical-pilot/apx-localsend-network-v1.py')
network = importlib.util.module_from_spec(spec)
spec.loader.exec_module(network)
GEN = 'e9b08983-4740-4b85-8580-862c4a1d4c54'


class LocalSendNetworkTests(unittest.TestCase):
    def setUp(self):
        self.config = dict(schema=1, enabled=True, environment='faculdade', generation=GEN, peer='192.168.1.100')
        self.active = dict(name='faculdade', generation=GEN, role='graphical-base', unit='apx-graphical-faculdade-e9b08983.service')
        self.record = dict(name='faculdade', generation=GEN, role='graphical-base', state='running')
        self.interfaces = [dict(ifname='wlan0', addr_info=[dict(family='inet', local='192.168.1.106', prefixlen=24)])]
        self.route = dict(dev='wlan0', prefsrc='192.168.1.106')
        self.defaults = [dict(gateway='192.168.1.1')]

    def test_active_generation_only(self):
        self.assertEqual(network.selection(self.config, self.active, self.record), ('faculdade', GEN, '192.168.1.100'))
        for key, value in [('generation', 'a9b08983-4740-4b85-8580-862c4a1d4c54'), ('name', 'steam'), ('role', 'hub'), ('unit', 'ssh.service')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                network.selection(self.config, dict(self.active, **{key: value}), self.record)

    def test_stopped_registration_rejected(self):
        with self.assertRaises(ValueError):
            network.selection(self.config, self.active, dict(self.record, state='stopped'))

    def test_non_lan_peers_and_extra_authority_rejected(self):
        for peer in ['127.0.0.1', '169.254.1.1', '8.8.8.8', '::1', '192.168.1.100; flush ruleset']:
            with self.subTest(peer=peer), self.assertRaises(ValueError):
                network.selection(dict(self.config, peer=peer), self.active, self.record)
        with self.assertRaises(ValueError):
            network.selection(dict(self.config, arbitrary_command='true'), self.active, self.record)

    def test_direct_physical_subnet(self):
        self.assertEqual(network.validate_lan('192.168.1.100', self.route, self.interfaces, self.defaults), ('wlan0', '192.168.1.106'))

    def test_host_gateway_broadcast_and_other_subnet_rejected(self):
        for peer in ['192.168.1.106', '192.168.1.1', '192.168.1.0', '192.168.1.255', '192.168.2.100']:
            with self.subTest(peer=peer), self.assertRaises(ValueError):
                network.validate_lan(peer, self.route, self.interfaces, self.defaults)

    def test_routed_and_virtual_peers_rejected(self):
        for route in [dict(self.route, gateway='192.168.1.1'), dict(self.route, dev='ve-apx-other'), dict(self.route, dev='wlan0" accept')]:
            with self.subTest(route=route), self.assertRaises(ValueError):
                network.validate_lan('192.168.1.100', route, self.interfaces, self.defaults)

    def test_rules_limit_both_egress_and_receiving_peer(self):
        state = [{'chain': {'name': 'environment_forward'}}]
        rendered = network.render('apx_ge9b0898_egress_v1', 've-apx-ge9b0898', 'wlan0', '192.168.1.100', '192.168.1.106', '192.168.21.202', state)
        permits = [line for line in rendered.splitlines() if line.endswith(' accept') and line.startswith('add rule')]
        self.assertEqual(len(permits), 3)
        outgoing = [line for line in permits if 'ip daddr' in line]
        self.assertEqual(len(outgoing), 2)
        self.assertTrue(all('ip daddr 192.168.1.100' in line and 'oifname "wlan0"' in line for line in outgoing))
        self.assertIn('oifname "ve-apx-ge9b0898" ip saddr 192.168.1.100 tcp dport 53317 accept', rendered)
        self.assertIn('tcp dport 53317 drop comment "APX LocalSend receive guard"', rendered)
        self.assertIn('tcp sport 53317 ct state established accept', rendered)
        self.assertIn('ip saddr 192.168.1.100 ip daddr 192.168.1.106 tcp dport 53317 dnat ip to 192.168.21.202:53317', rendered)
        self.assertNotIn('udp', rendered)
        self.assertNotIn('flush ruleset', rendered)

    def test_existing_jump_is_not_duplicated(self):
        state = [{'chain': {'name': name}} for name in ['environment_forward', network.FORWARD, network.NAT]]
        state.append({'rule': {'chain': 'environment_forward', 'expr': [{'jump': {'target': network.FORWARD}}]}})
        rendered = network.render('apx_ge9b0898_egress_v1', 've-apx-ge9b0898', 'wlan0', '192.168.1.100', '192.168.1.106', '192.168.21.202', state)
        self.assertNotIn('insert rule', rendered)
        self.assertNotIn('add chain', rendered)
        self.assertEqual(rendered.count('flush chain'), 2)

    def test_invalid_nft_tokens_rejected(self):
        for table in ['filter', 'apx_x_egress_v1;flush ruleset']:
            with self.assertRaises(ValueError):
                network.render(table, 've-apx-ge9b0898', 'wlan0', '192.168.1.100', '192.168.1.106', '192.168.21.202', [])

    def test_missing_or_disabled_opt_in_revokes(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(network, 'CONFIG', Path(directory) / 'absent'), patch.object(network, 'revoke') as revoke:
                network.reconcile()
                revoke.assert_called_once_with()
            path = Path(directory) / 'config.json'
            path.touch()
            with patch.object(network, 'CONFIG', path), patch.object(network, 'trusted_json', return_value={'enabled': False}), patch.object(network, 'revoke') as revoke:
                network.reconcile()
                revoke.assert_called_once_with()

    def test_validation_failure_revokes_previous_access(self):
        with patch('sys.argv', ['helper']), patch.object(network.os, 'geteuid', return_value=0), patch.object(network, 'reconcile', side_effect=ValueError('generation changed')), patch.object(network, 'revoke') as revoke:
            self.assertEqual(network.main(), 2)
            revoke.assert_called_once_with()

    def test_untrusted_file_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'config.json'
            path.write_text('{}')
            path.chmod(0o644)
            with self.assertRaises(ValueError):
                network.trusted_json(path)
            link = Path(directory) / 'link.json'
            link.symlink_to(path)
            with self.assertRaises(OSError):
                network.trusted_json(link)


if __name__ == '__main__':
    unittest.main()
