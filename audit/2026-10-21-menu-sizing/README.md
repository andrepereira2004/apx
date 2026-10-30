# Shared Wi-Fi card sizing

The owner chose the connected Wi-Fi card as the standard: 56 logical pixels,
14px corners, 36px circular icon surface, 16px icon and label at x54.
Shared actions now inherit that height; MenuButton/ControlTile icon layouts align.
Calendar date cells retain 36px height independent of action sizing, and the month
background follows the shared card surface. Live screenshots and status JSON
capture calendar and control menus in Faculdade after deployment.

Six native Qt creation/shared-action results, six battery tests and seven seed
tests pass; full shell compilation and smooth-scroll fixture pass. Deployment
recheck zero pending. No real settings/actions were submitted by validation.
Backup: /var/lib/apx/backups/20261021T094608Z-environments-minimal.
