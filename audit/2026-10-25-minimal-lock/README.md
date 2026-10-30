# Minimal lock screen — 2026-10-25

Owner requests only time/date and a time-dependent greeting for André; weekday
separator explicitly changed to |. Removed APX identity, keyboard-layout label
and unlock instructions. Password field fades while empty and appears on typing;
password-only authentication unchanged. Greeting uses local time:06–12 Bom dia,
12–19 Boa tarde, otherwise Boa noite; refresh every minute. Deployed source,
independent seed and five homes; runtime/recovery digest pins synchronized.
Seven desktop-seed tests pass; deployment recheck0pending. Date/greeting helper
executed successfully. No actual lock/unlock or visual acceptance claimed.
Backups:/var/lib/apx/backups/20261025T171011Z-controls-followup and
/var/lib/apx/backups/20261025T171026Z-controls-followup. Deployment/rollback helper:
scripts/physical-pilot/deploy-minimal-lock-20261025.py. No commit/push/reboot.

