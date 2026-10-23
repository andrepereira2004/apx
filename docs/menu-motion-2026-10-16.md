# Menu-like application entrances — 2026-10-16

The owner requested smoother Rofi and file-manager opening, resembling the
resident QuickShell menus (160 ms OutCubic, scale 0.96 to 1).

Implemented in the repository, independent shell seed and all five existing
Environment Lua configurations:

- Window entrance: 160 ms OutCubic, popin 96%; opacity uses the same timing.
- Window exit: 120 ms OutCubic, popin 96%, with matching opacity timing.
- Layer opacity: matching 160/120 ms timings; Rofi's exact namespace gets a
  dedicated popin 96% style. Other layers retain fade style.
- Main Thunar windows now animate. Existing modal, file-operation progress and
  portal-picker no-animation/float rules remain.
- Global window movement/resizing spring and workspace animations remain as
  before. Since window entrance timing is shared by Hyprland, the shorter cubic
  entrance also applies to other normal application windows, not just Thunar.

No launch delay, screenshot overlay or extra process is inserted into opening.
Configuration uses the installed Hyprland 0.56.2 Lua syntax. API reference:
https://wiki.hypr.land/configuring/core/animations/ and
https://wiki.hypr.land/configuring/core/rules/layer-rules/ .

The owner changed active Environments during validation; live evidence was
ultimately collected within one Steam session namespace. Configuration verification
reported `config ok`, reload succeeded, and `hyprctl configerrors` was empty.
The Rofi namespace was confirmed as `rofi`; sampled layer alpha reached 1 and a
subsequent files shortcut created a new Thunar window. Alpha polling confirms
mapping/end state, not frame-by-frame visual smoothness; owner visual acceptance
remains necessary. Fourteen work-default tests and changed-file whitespace checks
pass. Repeating the deployment makes no changes.

Evidence: `audit/2026-10-16-menu-motion/`. Deployment:
`scripts/physical-pilot/deploy-menu-motion-20261016.py`. SHA-256 seed/runtime and
recovery pins were refreshed. Exact modified-file backup and inventory:
`/var/lib/apx/backups/20261016T201516Z-menu-motion/`. Restoring those files and
reloading the active compositor restores the previous motion configuration.

## Follow-up: owner accepts Rofi; tiled reflow adjusted

The owner reported that Rofi was perfect but the file-manager transition was not.
Normal window movement was still inheriting the original spring, competing with
the newly shortened entrance when tiles were rearranged. Added explicit
`windowsMove` = 160 ms OutCubic to the seven Lua copies. This updates normal
window layout movement/resizing generally; all Rofi layer definitions and timings
are unchanged and compared against backup. Configuration/reload checks and live
animation query pass, as do 14 focused tests. Owner visual acceptance remains
pending. Sequential screenshots could not sample the sub-second transition.
Backup: `/var/lib/apx/backups/20261016T201803Z-thunar-reflow-motion/`.

## Owner clarification: progressive fade and soft bounce

The owner clarified that the previous entrance felt too snappy. Window entrances
now use a damped spring (mass 1, stiffness 220, dampening 18), with Thunar starting
at 90% size, and a 280 ms OutCubic opacity fade. Other normal windows share the
spring at the existing 96% starting size; layout reflow remains cubic. Rofi layer
configuration is unchanged. Configuration verification/reload and 14 tests pass;
perceived motion awaits owner acceptance. Backup:
`/var/lib/apx/backups/20261016T202015Z-thunar-soft-open/`.
