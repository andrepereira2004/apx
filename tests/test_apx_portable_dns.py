import ipaddress
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import apx_portable_dns as dns


def query(name='example.com',kind=1):
    wire=b''.join(bytes([len(part)])+part.encode() for part in name.split('.'))+b'\0'
    return struct.pack('!6H',42,0x0100,1,0,0,0)+wire+struct.pack('!2H',kind,1)


class PortableDNSTests(unittest.TestCase):
    def test_queries_have_bounded_uncompressed_single_questions(self):
        packet=query()
        self.assertEqual(dns.question(packet),len(packet))
        for packet in [b'',b'\0'*5000,query(kind=252),query(kind=255),query(kind=0),query()[:15],
                       query()[:12]+b'\xc0\x0c'+query()[-4:],
                       struct.pack('!6H',1,0x8100,1,0,0,0)+query()[12:],
                       struct.pack('!6H',1,0x0100,2,0,0,0)+query()[12:]]:
            with self.subTest(packet=packet[:20]),self.assertRaises(ValueError):dns.question(packet)
        for kind in [1,28,16,33,64,65,257]:self.assertEqual(dns.question(query(kind=kind)),len(query(kind=kind)))

    def test_servfail_and_truncation_preserve_only_the_original_question(self):
        packet=query();reply=dns.response_header(packet)
        self.assertEqual(reply[:2],packet[:2]);self.assertEqual(reply[12:],packet[12:])
        self.assertEqual(struct.unpack('!6H',reply[:12]),(42,0x8182,1,0,0,0))
        truncated=dns.response_header(packet,code=0,truncated=True)
        self.assertEqual(struct.unpack('!H',truncated[2:4])[0],0x8380)

    def test_gateway_discovery_never_binds_host_uplink_or_loopback(self):
        def link(name,kind,address,prefix=28):
            return dict(ifname=name,linkinfo=dict(info_kind=kind),addr_info=[dict(family='inet',scope='global',local=address,prefixlen=prefix)])
        values=[link('ve-apx-hub','veth','192.168.3.1'),link('wlan0','wireless','192.168.1.1'),
                link('ve-apx-bad','bridge','192.168.4.1'),link('ve-apx-loop','veth','127.0.0.1'),
                link('ve-apx-pub','veth','8.8.8.1'),link('ve-apx-mask','veth','192.168.4.1',24),
                link('ve-apx-net','veth','192.168.4.0')]
        self.assertEqual(dns.gateways(values),{'ve-apx-hub':('192.168.3.1',ipaddress.IPv4Network('192.168.3.0/28'))})

    def test_peer_admission_rejects_other_networks_gateway_and_broadcast(self):
        import threading
        gateway=object.__new__(dns.Gateway);gateway.address='192.168.3.1';gateway.network=ipaddress.IPv4Network('192.168.3.0/28');gateway.rates={};gateway.rate_lock=threading.Lock()
        for value in ['192.168.3.1','192.168.3.0','192.168.3.15','192.168.4.2','127.0.0.1']:
            self.assertFalse(gateway.admitted((value,1000)))
        for _ in range(32):self.assertTrue(gateway.admitted(('192.168.3.2',1000)))
        self.assertFalse(gateway.admitted(('192.168.3.2',1000)))

    def test_upstream_is_fixed_verified_https_and_bounded(self):
        packet=query();answer=packet[:2]+b'\x81\x80'+packet[4:]
        class Response:
            url=dns.UPSTREAM
            headers=SimpleNamespace(get_content_type=lambda:'application/dns-message')
            def read(self,size):self.size=size;return answer
            def __enter__(self):return self
            def __exit__(self,*args):pass
        response=Response();opener=SimpleNamespace(open=lambda request,timeout:response)
        with patch.object(dns.urllib.request,'build_opener',return_value=opener):
            self.assertEqual(dns.resolve(packet),answer)
        self.assertEqual(response.size,dns.MAX_RESPONSE+1)
        response.url='https://other.example/dns'
        with patch.object(dns.urllib.request,'build_opener',return_value=opener),self.assertRaises(ValueError):dns.resolve(packet)

    def test_dns_profile_does_not_open_other_host_or_lan_ports(self):
        spec=importlib.util.spec_from_file_location('network_dns_rules',ROOT/'scripts/physical-pilot/apx-environment-network-v1.py')
        network=importlib.util.module_from_spec(spec);spec.loader.exec_module(network)
        self.assertNotIn('dport 53',network.ruleset('apx_x_egress_v1','ve-apx-x'))
        portable=network.ruleset('apx_x_egress_v1','ve-apx-x',dns_proxy=True)
        self.assertIn('udp dport 53 accept',portable)
        self.assertIn('tcp dport 53 accept',portable)
        self.assertIn('iifname "ve-apx-x" drop',portable)
        self.assertIn('ip daddr',portable)
        self.assertNotIn('dport 22',portable)

    def test_full_source_verifier_checks_all_base_dependencies_and_no_retired_face_auth(self):
        spec=importlib.util.spec_from_file_location('portable_dependency_check',ROOT/'scripts/portable/install_apx_full.py')
        installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
        sources=installer.verify_sources()
        base=installer.module(ROOT/'scripts/portable/install_apx_arch.py','portable_dns_base')
        self.assertLessEqual(set(base.SOURCES),set(sources))
        self.assertNotIn('src/apx_face_auth.py',base.SOURCES)
        self.assertIn('src/apx_portable_dns.py',base.SOURCES)


if __name__=='__main__':unittest.main()
