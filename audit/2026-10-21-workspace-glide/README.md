# Short trackpad labels and workspace glide — 2026-10-21

Owner requested labels exactly Scroll and Workspaces and another refinement of
workspace animation. Visible/accessibility labels shortened. Workspace/In/Out
use a dedicated apxWorkspaceGlide cubic curve (0.22,1;0.36,1), 4.2 animation
units (nominal 420ms), full horizontal slide. Terminal slope is zero, no overshoot;
this lengthens and softens the settle after release. Physical finger tracking,
three-finger gesture, stored sensitivity and other animation curves unchanged.
Physical feel awaits owner feedback; compositor acceptance is not perceptual proof.

Live eval and reload accepted, configerrors empty; animations JSON confirms new
curve. Full native shell parse and existing 15-frame smooth fixture pass; seven
seed tests pass. Source, seed/five homes and pins applied, recheck zero pending.
Backup /var/lib/apx/backups/20261021T225942Z-controls-followup. Original source
copies and animations evidence: audit/2026-10-21-workspace-glide/.
No packages, lifecycle action, commit or push.

