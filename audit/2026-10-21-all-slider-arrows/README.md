# Arrow keys across settings sliders — 2026-10-21

Owner accepted Trackpad keyboard adjustment and requested the same for the other
sliders, including sound, brightness and mouse. MenuSlider now defaults to direct
Left/Right by one and Shift+Left/Right by five; Up/Down and Tab retain navigation.
This includes combined/separate volume, screen brightness, microphone and mouse.
Standalone ControlSlider (personalization opacity) uses the same convention and
emits moved on keyboard updates. No value/range or hardware settings were changed
by deployment. Media timeline seeking retains its native player-specific keys.

Mouse writes now preserve focus and queue the newest held-arrow value, protecting
optimistic state from stale status replies. Mouse drag captures released value
before model rebinding. Microphone volume has its own latest-value write queue;
status polling cannot overwrite pending/in-flight changes. Existing volume and
screen-brightness write queues remain in use.

Validation: 11 native Qt results pass against actual shared MenuSlider, settings
cards, mouse/gesture/microphone queue functions and standalone ControlSlider.
Includes one/five-point steps, bounds, held-key final value, microphone busy
writes, opacity updates and retained gesture drag/keyboard behavior. Full native
shell parse and 15-frame smooth fixture pass; seven seed tests pass. Applied
source/independent seed/five graphical homes with runtime/recovery pins; recheck
zero pending files. Backup /var/lib/apx/backups/20261021T225817Z-controls-followup.
Evidence: audit/2026-10-21-all-slider-arrows/.
No package install, hardware adjustment, lifecycle action, commit or push.

