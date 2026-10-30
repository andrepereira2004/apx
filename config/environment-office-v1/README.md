> Retired on 2026-10-12 after owner-reported rendering/sign-in failures. Faculdade now uses native GridCraft for spreadsheets. This directory records the rejected Wine pilot only.

# Faculdade Microsoft Office pilot — 2026-10-12

This asset is installed only in the owner-authorized Faculdade Environment. It is
not part of the creation seed or Host. Original Microsoft Office 16.0.20326.20144
(pt-pt/en-us) uses the checksum-verified Bottles Soda 11.0-29-experimental runner.
The account must have an appropriate Microsoft 365 licence; activation and editing
remain owner validation steps. See audit/2026-10-12-office-migration.json.

The launcher uses the Windows C: executable identity required by App-V. Passing the
Unix executable path silently exited during cold-launch tests. It repairs only the
prefix's ClickToRunPackageLocker permissions, primes ClickToRunSvc and keeps the
Wine server for a 60-second grace period. No Host or user systemd service is added.
Explicit NVIDIA GLX/EGL selection applies only to these Office launches.

The four environment-local desktop files use this launcher with an app argument,
Microsoft icons, and local Office-document MIME defaults. They carry
X-APX-Office-Managed=true and X-Wine4Office-Managed=false, so automatic manager
shortcut refresh does not replace the pilot launcher. Do not recreate shortcuts in
Wine4Office Manager without preserving this integration. Changing the Soda runner
or Office build requires revalidation of startup, activation, rendering and saving.

The Wine4Office manager is a management utility; its own bundled runner failed
installation and is not the active Office runner. Native Microsoft MSXML6, the
Bottles App-V DLL-copy/licensing adjustments, and signed environment-local 32-bit
libraries were needed. The Office repair/download payload is retained in the prefix
for recovery. This is an experimental per-Environment application installation,
not a native Linux port or a production APX Office support promise.
