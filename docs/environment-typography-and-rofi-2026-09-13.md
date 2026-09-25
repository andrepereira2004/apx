# Common typography and Rofi — 2026-09-13

Owner requested consistent interface typography, a more coherent Rofi appearance
and dismissal by clicking outside. Applied to Hub, Faculdade, Hytale, Minecraft,
Steam and independently pinned defaults for new normal graphical Environments.

GTK 3/4 settings, fontconfig sans-serif/system-ui aliases and the desktop
GSettings font now agree on Adwaita Mono 11. Session activation
sets the desktop font, including the GTK setting consumed by Brave's interface.
QuickShell text and bar components use the same Adwaita Mono, and the whole
interface now deliberately uses that same appearance as an explicit test.
Websites retain author-specified fonts;
no browser profiles, site styles or saved preferences were rewritten. Running
apps that cache typography may require closing and reopening. All five roots
contain the Adwaita font; active Hytale fc-match and GSettings confirm Mono.

Thunar derives its built-in Home shortcut label from the final component of the
home path, so changing only passwd metadata was insufficient. Each workload
home now has a Host-created `Home -> apx` symlink, and the file-manager action
opens that alias with `USER=home`, `LOGNAME=home` and `HOME=/home/Home`. The
technical account and UID remain `apx`/1000. A live Hytale screenshot confirms
the sidebar and location display `Home`; future graphical creation creates the
same alias.

Rofi uses the same dark neutral surfaces, subtle grey outline and light text as
the controls, with a 580px card, compact 22px icons and a quiet selection state.
Search/results remain the focus; inherited low-contrast row text and the default
dashed separator are explicitly overridden. Discovery/cache configuration stays
unchanged, preserving automatic detection of new installed desktop entries.

On Wayland the upstream click-to-exit switch alone is insufficient (see
[upstream discussion](https://github.com/davatorium/rofi/discussions/2266)). The
final solution uses Rofi's native fullscreen transparent surface with the visible
card centred inside it. Four transparent button regions around the card invoke
kb-cancel; the click is consumed instead of reaching the underlying application.
No extra daemon, privileged input observer or global mouse binding is installed.
Button action syntax follows the installed rofi-theme manual. Each string-valued
property occupies its own line to avoid greedy parsing in the installed version.
The discarded experimental QuickShell backdrop/helper was removed from all homes,
source and installed seed manifests before completion.

Validation on active Hytale:
- Inspected actual rendered Rofi card and corrected inherited text contrast.
- A temporary unprivileged Wayland virtual-pointer probe clicked the search box
  and then each of the four outside regions. Inside remained open; all four
  outside clicks closed the menu without selecting a dmenu item. Also verified
  the actual applications launcher closes. No physical-device grants changed.
- Source 51 and installed 49 assets match their respective pinned manifests.
  Installed provisioning successfully generated a fresh independent home with
  typography and native Rofi dismissal defaults.
- Runtime seed suite 35, control-centre layout 8 and file-manager suite 4 pass.
- Physical multi-monitor acceptance remains open; this pilot has one active
  display. Rofi's native fullscreen surface covers its selected display.

Backup: `/var/lib/apx/backups/20260913T163338Z-typography-rofi/`.
Contains original file bytes/ownership/modes, final manifest, cropped screenshot
and click-test results. Entries for removed new experimental files are marked
`after_absent`. Rollback restores originals and removes recorded additions;
restore runtime/seed manifests together and reopen affected applications.
The temporary input binary and screenshot were removed from the user's home.
Rofi now uses Adwaita Mono, the same effective family as the QuickShell menus, with a translucent fullscreen overlay and a darker translucent launcher card. Clicking the transparent area outside the card closes it. Fn+F11 uses a small workspace overview helper so each section is labelled `Workspace X`, followed by indented application rows; selecting a workspace or application performs the corresponding Hyprland action. This avoids the empty workspace token produced by Rofi's native Wayland window mode.

Workspace labels remain numeric in Waybar and Hyprland, matching the `SUPER+1` through `SUPER+9` bindings.
