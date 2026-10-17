# Appearance preferences — experimental pilot, 2026-10-16

Owner-authorized scope: choose icon colors globally or per Environment, and choose
wallpaper per Environment from Control Centre > More options.

Implementation plan and boundary: extend the existing authenticated Host shared
services v3 broker with typed appearance.load/save operations. The sole global
field is an opaque RGB icon color; the broker owns one private JSON record under
/var/lib/apx/appearance-v1. No file paths, commands or per-Environment data pass
through this global operation. All previously authorized desktop peers may use
these cosmetic operations, like the existing shared-calendar preference paths.
The systemd service gets write access only to this additional state directory.

Each Environment stores its optional icon-color override and chosen wallpaper in
its own home. Inheritance resolves as local override > global color > built-in
color. Wallpaper data remains local; no Home, credentials or settings are copied
between Environments. New Environments receive only the independent versioned
helper/UI seed and inherit the global color through the existing broker.

A user-selected local image is validated and copied into the current Environment's
private appearance data folder. Built-in backgrounds remain selectable. Resetting
wallpaper restores the existing automatic rotation only for that Environment.
Selections apply live and persist across session restarts; global updates are
refreshed within five seconds. Broker unavailability leaves local overrides usable
and reports errors when a global write fails.

This is an experimental extension of the current broker, not a new production
privilege mechanism. Rollback requires restoring the backed-up broker, client,
contract, service unit and seed/UI files, then reloading the service and shell;
new private appearance records can remain inert without affecting recovery.

Owner expanded the scope during implementation: the shared color also has three
boolean targets (icons/highlights, buttons, window surfaces); each style record
is inherited or overridden as a whole. Global schema is now exactly color plus
these three booleans. Terminal and Thunar retain their opacity and readable
foreground; their background RGB is a dark blend of the selected color. Managed
local CSS/Kitty/Rofi overrides preserve unrelated user configuration. Kitty can
reload its local include through SIGUSR1; GTK applications may require reopening.
Rofi uses JetBrains Mono and the same scoped surface/highlight settings; its
accepted animation is outside this change. Add Lucide mouse to sensitivity and
remove the three owner-identified battery explanation/status texts while keeping
power-profile controls and errors.

Further owner scope: compact the main Control Centre into icon-only tiles with
accessible labels/tooltips; add airplane mode, local MPRIS playback controls and
Mako active/history notifications. Airplane mode uses one typed radio.airplane
operation with a boolean, serialized with existing network mutations, operating
only on fixed wlan/bluetooth rfkill classes. No live radio toggle is necessary
for validation. Playback is restricted to named local MPRIS interfaces and three
fixed transport methods. Notification viewing is read-only. No outgoing message
or cloud service is involved. Final owner instruction supersedes optical sizing: all bar icons use the same
17px size and battery glyphs retain standard Lucide stroke-width 2. Rofi animation definitions remain unchanged.

## Scoped appearance, compact controls and ghost personality (2026-10-16)

Installed global/per-Environment style and local wallpaper preferences in all five
existing homes and independent seed. Style schema is color plus icons/buttons/windows
booleans, inherited as a whole; global writes use authenticated Host broker, local
wallpaper/preferences remain in each home. Kitty, Thunar and Rofi receive managed
local styling; GTK may need reopening. Rofi uses JetBrains Mono; accepted animations
are preserved. Compact Control Centre has labelled tooltips, airplane action, local
MPRIS transport and read-only Mako notifications/history. Battery explanatory texts
removed, profile controls/errors retained; sensitivity and Fn OSD use Lucide.

Ghost greeting selects from 3000 distinct combinations (300 authored contextual
bodies and 10 introductions per group), filtered by local date/hour/Environment/
open app classes and compatible MPRIS playback; excludes previous 200 selections
within the shell session. No AI service, network request or background generation.

Owner rejected optical battery sizing. Final explicit requirement: identical
17px bar viewport and standard Lucide stroke-width 2 for all six battery glyphs,
matching other bar icons. No battery-specific sizing remains. Applied and byte
verified across five homes and seed; final backup:
/var/lib/apx/backups/20261016T205516Z-appearance-controls.

Validation: 14 desktop defaults, 7 appearance, 3 ghost, 16 broker, 3 Wi-Fi and
3 bar tests pass. Live authenticated global read/save-same-style roundtrip passed
with no warning; airplane radios were not toggled. Compatible MPRIS players required.
User fullscreen video prevented final bar screenshot without interrupting playback;
visual owner acceptance remains open. No commit or push.

Live broker restart initially left an old inode-bound socket in the active
Minecraft namespace. Fresh endpoint projected at host-services-v3-refresh.sock and
client retries only on ConnectionRefusedError; authentic shell requests accepted
again. Future broker replacement must account for active socket bind mounts;
the deployment script alone does not refresh those endpoints automatically.
