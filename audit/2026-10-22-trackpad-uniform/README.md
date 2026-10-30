# Uniform 35/100 trackpad cursor — 2026-10-22

Owner requested 35/100 in every Environment persistently and clarified the
perceived smoothness delay happens during the first seconds entering Hub.
Persisted raw sensitivity -0.30 (UI35) and explicit adaptive profile in Hub,
faculdade, hytale, minecraft and steam independent preference files. Added that
preference to the independent seed/pinned inventory so new Environments start
at35 too. Settings helper now preserves explicit adaptive profile when saving
cursor sensitivity. Existing UI remains adjustable; this is an owner-requested
uniform current/default choice, not a lock or a cross-Environment settings sync.
Scroll/workspace preferences and pointer power are unchanged.

Source/live paths show no delayed acceleration activation service: these values
load directly in compositor Lua configuration independently of shell polling.
Boot/re-entry perceived delay is not reproduced or explained yet. Do not claim
this change proves a startup-delay fix. No reboot/session restart performed.

Seven pointer/gesture tests and seven seed tests pass. Live Hub apply succeeds,
configerrors empty, five saved profiles verified and recheck zero pending.
Backup /var/lib/apx/backups/20261022T084259Z-controls-followup. Evidence:
audit/2026-10-22-trackpad-uniform/. No package/lifecycle change, commit or push.

