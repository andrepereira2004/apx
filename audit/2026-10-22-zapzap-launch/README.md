# ZapZap repair, consistent file selection, installation checks — 2026-10-22

ZapZap failed because freshly installed Python PyQt bindings required Qt_6.12,
while the accepted desktop uses Qt6.11.2. Its AUR dependency transaction used
pacman-S without completing pending repository updates. Restored four cached,
signed matching dependencies in faculdade only: python-pyqt6 to6.11.0-3,
qt6-positioning/webchannel to6.11.2-1 and qt6-webengine to6.11.2-1. Qt6-base,
QuickShell, GPU packages and other Environments' packages were not upgraded.
Import checks and actual ZapZap windows pass. The test runner initially omitted
XDG_SESSION_TYPE, causing an artificial xcb abort; the real Wayland startup works.

Added an Environment-local, root-owned pretransaction package-coherence check
for pacman/AUR transactions and the same hook/helper to future-creation runtime.
Partial transactions with pending repository upgrades are refused before package
changes. Complete plans pass; the existing three Host-coupled NVIDIA holds remain
allowed. No automatic broad upgrade was submitted. apx-install now validates
available PyQt/QtWebEngine imports rather than equating files with a runnable app.
Five coherence tests and six installer tests pass, including future-root hook
contents; live incomplete/complete-plan checks pass without installing packages.

All five homes and future sessions prefer Qt's xdgdesktopportal theme and GTK
portals, with Thunar for inode/directory. Hub's missing explicit folder default
was added without changing browser associations. Native Qt-to-GTK portal chooser
was verified with a synthetic empty folder, with no file selected/sent. Shared
chooser CSS uses APX colours/font and restrained headers/navigation. A currently
running app cannot acquire a new Qt theme from an environment update. ZapZap was
still reusing its old tray process; installed an Environment-local zapzap wrapper
and normally shut down/reopened the old process through its documented SIGTERM
bridge. New process/window and QT_QPA_PLATFORMTHEME/GTK_USE_PORTAL were verified.
No message/account/profile was deleted. This is the common default, not a claim
that applications hardcoding custom file dialogs can be universally overridden;
a native selector is not a normal Thunar window. New/updated supported apps use
the common picker; already running applications need normal restart.

Deploy scripts: deploy-zapzap-integration-20261022.py,
deploy-package-coherence-20261022.py, deploy-notifications-chooser-20261022.py,
deploy-zapzap-launcher-20261022.py under scripts/physical-pilot/.
Backups recorded in audit/2026-10-22-zapzap-launch/ and
 audit/2026-10-22-notifications-chooser/. Package repair command/inventory is
scripts/physical-pilot/repair-zapzap-20261022.py. No Host packages modified.

