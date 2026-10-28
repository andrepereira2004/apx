# Calendar-style Control Centre navigation

The slow height/opacity page wrapper from the previous attempt was removed from the source, Faculdade and Hytale. Control Centre navigation now uses the Calendar's existing sequence: 90 ms fade/10 px horizontal exit, switch the displayed page, then 190 ms fade/10 px horizontal entrance. The panel itself stays opaque and stationary. Repeated navigation retargets the sequence. Calendar motion, popup opening, workspace strip and the original Battery details behaviour remain as they were before the rejected page wrapper.

Faculdade's shell matches the repository source. Hytale has a targeted version of the change based on its own configured shell; its patch is `hytale-shell.patch`. QuickShell loaded it, and IPC navigation from the main controls to Connectivity was checked visually at rest and mid-transition. The mid-transition capture showed the panel retaining its dark background, with one page in place. Both shell variants passed `qmllint`, `git diff --check` passed, and the active QuickShell log tail contained no component or binding errors.

The unrelated Hytale shell-file recovery limitation from the previous attempt is documented in `../2026-10-28-menu-motion-redesign/RESULT.md`.
