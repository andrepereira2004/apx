# Physical APX network recovery, 2026-10-13

Scope: owner-authorized live host recovery and recurrence mitigation. Experimental
physical-pilot mechanism, not a production architecture claim.

Observed failure: Faculdade host0 lost DHCP at 16:16, leaving 169.254/16 and no
default route. Host ve-apx-ge9b0898 entered failed after repeated networkd
reconfiguration/netlink timeouts near suspend/resume. Host Wi-Fi and Google HTTPS
worked. Exact trigger of the reconfiguration loop remains unproven.

Immediate recovery: restart systemd-networkd on Host; renew host0 in Faculdade.
Validated workload default route and Google HTTP/2 200.

Persistent mitigation files:
- /usr/lib/apx/apx-network-recovery-v1.py
- /etc/systemd/system/apx-network-recovery-v1.service
- /etc/systemd/system/apx-network-recovery-v1.timer

Repository sources are scripts/physical-pilot/apx-network-recovery-v1.py and
config/environment-network-recovery-v1/. Every 30 seconds inspect networkctl JSON.
Only failed ve-apx-* interfaces trigger recovery; no DNS/Internet probes or
external dependencies. Restart host networkd once and renew host0 for running
APX nspawn containers. Timeout is bounded; cooldown is 120 seconds, stored under
/run and cleared on reboot. Logs use journalctl -u apx-network-recovery-v1.
A healthy network is left alone. Recovery does not relax nftables isolation.
It can briefly interrupt host connections. Unit stops after 90 seconds.

Permissions: prior /etc/systemd/network/20-wired.network.d was 0700, causing
networkd permission-denied warnings; changed directory to 0755. Content preserved.

Validation: three unit tests, systemd-analyze verify, live healthy service execution,
actual DHCP renewal command, Google HTTPS from inside Faculdade. Full physical
suspend/resume recurrence acceptance remains pending; no deliberate suspension.

Reversal:
    systemctl disable --now apx-network-recovery-v1.timer
    rm /etc/systemd/system/apx-network-recovery-v1.timer
    rm /etc/systemd/system/apx-network-recovery-v1.service
    rm /usr/lib/apx/apx-network-recovery-v1.py
    systemctl daemon-reload
If reverting directory permissions is required, chmod 0700
/etc/systemd/network/20-wired.network.d restores the prior unreadable state.
Do not remove other existing network settings. No package change, commit or push.
