# Camera and Fn transient feedback

Camera privacy state is sampled alongside audio every 500 ms from physical
video devices in sysfs; initial sampling is silent. Camera feedback survives
PipeWire failures. It reflects device availability, not application capture.
Owner confirmed camera feedback working before the distinct-icon refinement.

Camera and airplane now have distinct enabled/disabled glyphs; touchpad keeps
its existing touchpad/touchpad-off pair. Idle MediaIsland border removed and
transient feedback ignores stale pointer hover so its resting fill matches the
Environment capsule.

The Fn observer was absent in the live Hub. A 1.5-second QuickShell retry timer
now restarts it after exit, including lock contention during shell reloads.
Live forced-exit test: PID 63094 was replaced automatically by PID 66839.
Read-only touchpad/airplane feedback IPC calls confirmed osd_visible and
island_transient true; no device state changes were requested by validation.
Camera fixture covers absent sysfs, physical node, duplicate metadata node,
privacy disable and virtual-only nodes. Native full-shell compilation passes.
Hardware-profile suite: 11 pass, one pre-existing stale source-string assertion
fails (the expected airplane printf differs in the existing working tree). No unrelated
legacy test changes made. Deployment recheck: zero pending files.
Latest backup: /var/lib/apx/backups/20261021T131226Z-controls-followup.
