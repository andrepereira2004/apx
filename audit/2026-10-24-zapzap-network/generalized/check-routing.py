"""Run with unshare -n: no live routes, interfaces or firewall are modified."""
from pathlib import Path
import subprocess
import time
import sys

RULES = Path(__file__).resolve().parents[3] / 'config/environment-network-recovery-v1/reply-hop-pilot.nft'

def run(*args, check=True):
    return subprocess.run(args, check=check, capture_output=True, text=True)

children = []
try:
    for _ in range(2):
        children.append(subprocess.Popen(['unshare', '-n', 'sleep', '120']))
    time.sleep(.3)
    client, server = [str(p.pid) for p in children]
    def inside(pid, *args, check=True):
        return run('nsenter', '-t', pid, '-n', '--', *args, check=check)
    for host, peer, pid, address in [
        ('ve-apx-proof', 'client0', client, '192.0.2.2/24'),
        ('uplink-proof', 'server0', server, '198.18.0.2/24'),
    ]:
        run('ip', 'link', 'add', host, 'type', 'veth', 'peer', 'name', peer)
        run('ip', 'link', 'set', peer, 'netns', pid)
        run('ip', 'link', 'set', host, 'up')
        inside(pid, 'ip', 'link', 'set', peer, 'up')
        inside(pid, 'ip', 'link', 'set', 'lo', 'up')
        inside(pid, 'ip', 'addr', 'add', address, 'dev', peer)
    run('ip', 'addr', 'add', '192.0.2.1/24', 'dev', 've-apx-proof')
    run('ip', 'addr', 'add', '198.18.0.1/24', 'dev', 'uplink-proof')
    inside(client, 'ip', 'route', 'add', 'default', 'via', '192.0.2.1')
    run('sysctl', '-qw', 'net.ipv4.ip_forward=1')
    run('nft', 'add', 'table', 'ip', 'test_nat')
    run('nft', 'add', 'chain', 'ip', 'test_nat', 'postrouting', '{ type nat hook postrouting priority srcnat; policy accept; }')
    run('nft', 'add', 'rule', 'ip', 'test_nat', 'postrouting', 'oifname', 'uplink-proof', 'masquerade')
    def ping():
        return inside(client, 'ping', '-n', '-c', '1', '-W', '1', '198.18.0.2', check=False)
    inside(server, 'sysctl', '-qw', 'net.ipv4.ip_default_ttl=1')
    assert ping().returncode != 0, 'TTL1 must fail without correction'
    run('nft', '-f', str(RULES))
    assert ping().returncode == 0, 'TTL1 must pass on arbitrary uplink'
    before = run('nft', 'list', 'table', 'ip', 'apx_reply_hop_v1').stdout
    inside(server, 'sysctl', '-qw', 'net.ipv4.ip_default_ttl=64')
    ordinary = ping()
    assert ordinary.returncode == 0 and 'ttl=63' in ordinary.stdout, ordinary.stdout
    after = run('nft', 'list', 'table', 'ip', 'apx_reply_hop_v1').stdout
    assert before == after, 'TTL64 traffic must not match correction'
    # An established NAT reply to a non-APX interface must still expire.
    run('ip', 'link', 'set', 've-apx-proof', 'name', 'ordinary-proof')
    inside(server, 'sysctl', '-qw', 'net.ipv4.ip_default_ttl=1')
    assert ping().returncode != 0, 'Non-APX route must not receive correction'
    print('PASS: TTL1 failure reproduced; arbitrary uplink repaired; TTL64 unchanged; non-APX excluded')
finally:
    for child in children:
        child.terminate()
        child.wait()
