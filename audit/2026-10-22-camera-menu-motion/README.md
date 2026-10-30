# Camera trace length and menu opening — 2026-10-22

Owner reported a missing-looking trace and stuttering Control Centre opening.
Real bounded ffplay capture in the active minecraft Environment confirmed the
existing white trace moves around the 88px status capsule. Owner then requested
2.5 times its length: CameraIndicator now covers 15% of the perimeter (from 6%),
with unchanged 2px white stroke and 1800ms lap. Native UI 8/8, rendered pixel
movement and camera-detection tests 2/2 pass. No camera frames saved.

Popup and rounded-mask textures now allocate at final viewport dimensions,
avoiding GPU texture reallocations on every opening/closing frame. Full QML
parse and the existing scroll-motion fixture pass. Three live Control Centre
openings after deployment recorded median frameSwapped gaps of 8,9,8ms and
maximum gaps of 24,19,16ms. These are application frame callbacks, not compositor
presentation. The owner changed active Environment from hytale to minecraft
during diagnosis, so retained before/after files are not a controlled benchmark.
Subjective smoothness remains for owner confirmation.

Applied independent seed and five homes with runtime/recovery digest pins;
deploy --check reports zero pending. Backups: /var/lib/apx/backups/
20261022T184704Z-controls-followup (texture change) and
20261022T184804Z-controls-followup (trace length). Details/evidence:
audit/2026-10-22-camera-menu-motion/. No commit/push.

