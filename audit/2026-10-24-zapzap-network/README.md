# Faculdade Internet failure — 2026-10-24

Owner reports ZapZap cannot access the site. Host HTTPS worked; Faculdade DNS,
ICMP and HTTPS timed out. Packet headers on wlan0 showed inbound Internet replies
with TTL=1. Existing APX NAT and forwarding were present. Adding one hop only to
wlan0 source-NAT reply connections restored Faculdade ping, DNS and WhatsApp HTTPS
(HTTP 200). This is a physical-pilot network compatibility exception, not a new
production architecture. No account, cookie, profile, or isolation policy changed.

Source: config/environment-network-recovery-v1/reply-hop-pilot.nft. Fragment
appended to /etc/nftables.conf (enabled existing nftables service). Full config
passed nft -c; only the dedicated table applied live. No service restart/reboot.
Rollback: restore nftables.conf.before to /etc/nftables.conf and run
`nft delete table ip apx_reply_hop_v1`. ZapZap UI/account recovery awaits owner
reload; underlying site reachability confirmed. No commit/push.
