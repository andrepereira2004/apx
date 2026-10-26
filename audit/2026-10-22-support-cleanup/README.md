# Owner-requested support cleanup

Scope: optional test/diagnostic/support software in the five existing APX roots.
Do not equate no reverse package dependency with no user value: explicit user
applications, development tools, multimedia, printing, configuration, authentication
and personal files are retained. No arbitrary orphan/cached-file sweep was done.

Cleanup plan and original package roots:
/var/lib/apx/backups/20261022T204448Z-support-cleanup/.
45 package removals in four workload roots; 198 optional component files removed
across five roots. Pacman previews refused dependency breakage; no force or cascade
flags were used. Optional component paths came from their owning package manifests.
Their libraries remain installed and package integrity passes with explicit
NoExtract policy in each root's pacman options. These are actual executable
removals and upgrade exclusions, not desktop-entry visibility masks.

Remaining runtime tools retain camera/video libraries, Avahi service discovery
libraries, hwloc libraries, core CMake, Xfce libraries and core Rofi. Screenshots,
personal profiles, old snapshots and the independent base were not used as live
application state. No immutable base package selections were changed; future
Environment creation defaults have not been cleaned by this operation.

Validation:

- Each root passes pacman dependency database and affected-package file checks.
- Rerunning cleanup preview yields no remaining selected packages/components.
- `runtime-validation.json`: actual Minecraft FFmpeg synthetic-video processing,
  libv4l2 dynamic loading, and full disjoint catalogue partition all pass. This
  tests software loading/processing, not actual camera or audio hardware capture.
- 40 catalogue/action tests and seven independent-seed integrity tests pass.
- Host terminal uses an authored SVG server/terminal symbol in both its desktop
  entry and unmatched-window fallback. Actual Rofi rendering recorded in
  `host-terminal-icon.png`, without diagnostics; icon deployment recheck empty.
- Original Hub already lacked /usr/bin/rofi. Initial validation incorrectly
  assumed all roots had that binary; it was corrected without installing packages.
  The final run resumed with the original pre-change recovery snapshots.

Icon deployment backup:
/var/lib/apx/backups/20261022T204626Z-controls-followup.
An intermediate failed-run backup set is retained at
/var/lib/apx/backups/20261022T204520Z-support-cleanup; the original set above is
the complete recovery baseline. No session restart, commit or push.
