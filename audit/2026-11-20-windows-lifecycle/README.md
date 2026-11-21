# Windows lifecycle/return repair — installed 2026-11-20

Source/behavior: ../../docs/native-windows-return-and-current-slot-2026-11-20.md.

Deployment plan SHA-256:
`a1d2ef38d179f6b30149acb0e7d1467093b6537e1c9937a1d977ec66c1978d7b`.
Single-use plan; it must fail after installation. No partition, firmware or
reboot operation is part of this deployment. Guest writes replace only the
three named return-integration assets on verified clean p3/p5 NTFS volumes.

Backup: `/var/lib/apx/backups/20261120T221440Z-windows-return-slot`.
Deployment initially stopped before writes because blkid -p exposes
PART_ENTRY_UUID instead of PARTUUID. The same bug in the actual wipe wrapper
was corrected and tested before installation. Socket permission recovery after
broker restart was applied for Hytale's existing mapped uid; subsequent
identity.get requests succeeded without relaunching its desktop.

Validation:

- 112 native Python tests pass, including current-layout clear/reuse, Recovery
  preservation, interrupted-delete resume, UUID case normalization and probe.
- PowerShell 7.4.13 parser and executable harness pass with mocked BCDEdit.
  Task registration, Windows ACL execution and guest startup are not exercised
  by this Linux harness; Windows PowerShell 5.1 uses the staged script next login.
- Real installed boot runner --validate-only passed for windows and windows-testes.
- Installed deletion dry-run passes with real GPT, UUIDs and block sizes, cloned
  metadata and mocked firmware deletion/wipes. Electrical admission is mocked
  because the charger is disconnected; the real executor still requires AC.
- Native release enabled() true with no mismatches.
- Switch suite: 30/31 pass; preexisting exact-QML-double-click assertion fails.
  This task changes its retired-helper expectation test, not the prior QML change.
- Physical GPT and firmware match the before snapshot. Both Windows registrations
  remain ready, and no real deletion has been run.

Remaining external acceptance: first login in each Windows and accept the
one-time UAC install; verify task succeeds and normal Restart returns to Linux.
If UAC is cancelled or registration fails, automatic return is not guaranteed.
Deletion can subsequently be selected in the Hub with AC connected. Creation UI
still has only 120/180/250 GiB presets; 77 GiB replacement UI is a separate task.

Portable test tooling is in git-excluded tools/ (PowerShell official GitHub
v7.4.13 release), retained only for local development and later mode cleanup.
