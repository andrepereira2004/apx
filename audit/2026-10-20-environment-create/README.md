# Environment creation refinement — 2026-10-20

Owner requested a cleaner form inspired by Control Centre, only the intermediate
preset, removal of the included-applications card, smaller controls, then shared
button dimensions across Environment, AI, Battery, Control Centre and Calendar.

Creation uses 460px width, aligned circular icons, labelled name/description
fields, APX/Windows choices, collapsed optional feature customization and one
submit action. The default remains intermediate; Basic/Complete selectors are
removed. Windows space verification/confirmation path is retained. No included
applications summary card remains. Keyboard traversal excludes hidden controls.

Shared Appearance.menuActionHeight=44 and menuActionRadius=14 now drive MenuButton,
ControlTile, dashboard actions, menu selectors, calendar actions/date cells and
Environment lists. Battery profiles use 44px rows with the original profile
availability and hardwareBusy guards. AI action/selector rows reserve the same
height. Multi-line informational cards/fields keep content-appropriate heights.

Native form fixture uses the actual QML components and creation subtree, fake
submission/hardware callbacks and fake appearance state. Six Qt results pass,
covering typing/submission, APX/Windows and storage choices, expandable modules,
keyboard navigation and shared action dimensions. No environment was created.
Six battery action tests, seven seed tests and three icon tests also pass.
Full native shell compilation and smooth-scroll fixture pass. Deployment recheck
zero pending paths; whitespace clean. Current screenshots are in sibling
2026-10-20-menu-button-consistency; before.png and initial-redesign.png here show
the initial redesign before later compact sizing/removal requests.

Applied source, independent seed, five graphical homes and integrity pins.
Latest backup: /var/lib/apx/backups/20261020T225657Z-environments-minimal.
No agent-initiated Environment switch, packages, commit or push.
