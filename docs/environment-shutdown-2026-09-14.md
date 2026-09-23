# Owner-requested shutdown from any normal Environment

Owner explicitly requested “Encerrar” in all Environment control centres.
This is an accepted narrow exception to Hub-only machine controls: an admitted
active normal graphical workload may prepare/confirm/cancel only poweroff.
Reboot, suspend, GPU changes and other Environment lifecycle operations remain
unavailable through the workload hardware endpoint.

The existing generation-authorized hardware bridge carries the existing power
protocol. Every mutation proves active identity and QuickShell ancestry; tokens
are additionally bound to Environment generation and shell PID/start time. The
same existing two-step power service logic enforces TTL, token hashing, peer UID,
rate limiting, update/inhibitor checks and exclusive reservation. A periodic tick
expires owned confirmations even without new requests. No confirmation is sent
by the deployment or tests; the physical machine stays running.

The existing power runner first quiesces the Hub launch supervisor, then validates
and recovers the active workload using its canonical graphical recovery path,
then recovers Hub and refuses shutdown if any machine survives. Existing Host
power runner transition locking, update and inhibitor checks remain. Unsupported
roles and stale registrations fail closed. The common UI confirmation remains.

This pilot change is experimental. Validate prepare/cancel and negative paths
without shutting down this active owner session. Final physical shutdown needs
owner execution. Restore backed-up service/runner/shell and restart only the
hardware service for rollback; do not roll back while a confirmation is pending.
