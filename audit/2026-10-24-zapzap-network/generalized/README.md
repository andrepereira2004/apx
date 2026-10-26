# General APX reply routing correction — 2026-10-24

Owner requests all apps and networks covered. Replaced wlan0-only workaround
with uplink-independent IPv4 NAT reply handling: after reverse NAT, match the
actual destination route ve-apx-* and raise only TTL1 to2. Covers current/future
APX routed interfaces and all protocols/apps using this NAT path. No interface,
SSID, destination website, app or Environment address is pinned. No firewall
accept verdict added; per-Environment host/private/sibling restrictions retained.
Experimental physical-pilot compatibility exception, not production approval.
Native IPv6 is outside this IPv4 NAT correction; no IPv6 topology enabled.

Existing enabled nftables startup config persists the fragment. Full config
syntax passes; dedicated table applied without restarting services. Isolated
network test reproduces TTL1 failure, verifies arbitrary-uplink recovery, normal
TTL64 unchanged and non-APX routes excluded. Four existing network policy tests
pass. Live Faculdade WhatsApp/Google/example.com all HTTPS200. Physical switching
to another Wi-Fi/Ethernet remains untested. No account/session changes or reboot.
Source config/environment-network-recovery-v1/reply-hop-pilot.nft; evidence and
rollback audit/2026-10-24-zapzap-network/generalized/. No commit/push.

Rollback to the preceding wlan0-specific state: restore nftables.conf.before to
/etc/nftables.conf and load only its apx_reply_hop_v1 table. To remove the correction
entirely, use ../nftables.conf.before and delete table ip apx_reply_hop_v1.

Reproduce isolated validation:
`unshare -n python audit/2026-10-24-zapzap-network/generalized/check-routing.py`
All test interfaces/routes/rules live in isolated network namespaces; child
processes terminate in finally and namespace lifetime ends after execution.
