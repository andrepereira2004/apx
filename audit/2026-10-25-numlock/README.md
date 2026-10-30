# Remember Num Lock and final lock greeting position — 2026-10-25

Owner clarifies: remember the chosen Num Lock state, not always enabled. Replaced
today's fixed true with shared authenticated keyboard.load/save boolean preference
and independent local caches. Non-consuming Num Lock release binding saves actual
main-keyboard state (including while locked); startup/config reload restores it.
No polling/new daemon/device access. Broker private state keyboard.json uses atomic
replacement and fsync, within existing service sandbox. Seed has no personal state.
Source/seed/five homes/runtime/recovery pins synchronized; check0pending. Broker
updated with existing bounded restart/socket refresh adapter and inode-preserving
client updates. Initial observed main-keyboard state was false and retained.
Live compositor-launched helper save/restore both exit0, authenticated operations
accepted, configerrors empty. Direct namespace-entered test correctly rejected by
process-lineage authorization; no weakening applied. Four new persistence/validation
unit tests,8contract,9physical broker,7seed tests pass; peer tests recorded separately.
Actual key release, Environment switch and full power cycle not exercised; owner
physical acceptance remains pending. Details:docs/numlock-state-2026-10-25.md and
audit/2026-10-25-numlock/. Backups:20261025T171746Z-radio-power and
20261025T171800Z-controls-followup under /var/lib/apx/backups; initialization
inventory in audit initialized-state.json. Supersedes always-on policy below.

Owner final greeting placement: BELOW the always-visible password field, y=-72;
time/date retained, no APX/layout/instructions. Applied source/seed/five homes;
backup20261025T171600Z-controls-followup. Actual lock visual check pending.
No firmware/boot/auth changes, reboot, commit or push.

# Num Lock default and visible password field — 2026-10-25

Owner requests Num Lock enabled across Environment entry and power cycles.
Enabled native input.numlock_by_default in Lua and fallback config, preserving
each independent local configuration. Source, seed, five homes and runtime/
recovery digest pins synchronized; deploy recheck0pending. Active Hyprland
reports bool=true/set=true; both keyboards numLock=true, configerrors empty.
Seven desktop-seed tests pass. Actual reboot/switch not performed; startup
persistence is configured, owner physical acceptance pending. Backup:
/var/lib/apx/backups/20261025T171134Z-controls-followup. Bounded deploy/rollback:
scripts/physical-pilot/deploy-numlock-20261025.py. Native option documented at
https://wiki.hypr.land/configuring/core/config-options/ . No firmware change.

Owner also clarifies password field must always remain visible. Restored
fade_on_empty=false and Palavra-passe placeholder in source/seed/five homes;
other minimal labels/date/greeting retained. Recheck0pending. Backup:
/var/lib/apx/backups/20261025T171132Z-controls-followup. Supersedes hidden-field
behavior below. No actual lock, reboot, commit or push.

