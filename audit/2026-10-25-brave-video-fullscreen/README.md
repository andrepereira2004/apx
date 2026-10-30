# Brave HTML video fullscreen investigation — 2026-10-25

Owner reports frozen page/image then sudden switch when entering/exiting YouTube
video fullscreen, explicitly distinct from SUPER+F. No persistent fix deployed.

## Method

`probe.py` runs in active Faculdade with a fresh disposable Brave profile and a
local-only CDP endpoint on an ephemeral loopback port. Existing user browser,
tabs, account and settings are not controlled or copied. First native local
canvas video, then generated H.264720p60 video, then anonymous public YouTube
Big Buck Bunny (aqz-KE-bpKQ). YouTube entry clicks its fullscreen control under
user-gesture CDP evaluation; exit uses document.exitFullscreen. Native Wayland
confirmed. CDP and browser terminate, temporary files/profiles removed afterward.

Collect page requestAnimationFrame gaps, fullscreen events, viewport changes,
request promise durations and selected browser performance counters. These are
page/main-thread measurements, not GPU presentation or visual inspection. Local
canvas has no gap>25ms in8transitions; real decoded local video max16.7ms in8.
Anonymous YouTube reproduces217.2–417.6ms max gaps over8transitions. In an ABAB
run browser counters show substantial script/style/layout work. The page stalling
is reproducible without the owner's profile; this does not prove that YouTube
alone, independent of Chromium/driver/layout interactions, is responsible.

Video playback frame counters in the initial YouTube run remained constant;
continuous streamed playback/codec performance was not established. Conclusions
are limited to the page's fullscreen transition responsiveness. Local decoded
video did advance its counters.

## Experiments rejected or incomplete

- Hide #cinematics (visual ambient layer only, not equivalent to switching the
  official ambient-mode preference off): ABAB median max gaps237.6ms baseline,
  221.9ms candidate; large pauses persist, no convincing causal fix.
- CSS layout/style containment on ytd-watch-flexy: median266.75 vs258.3ms,
  large pauses persist. Not adopted.
- Broad removal of site CSS transitions/animations: run interrupted by page
  state error, no valid comparison. Not adopted.
- Per-test-window compositor no_anim experiment: browser page/player references
  changed during run; invalid/incomplete comparison. No conclusion. Override was
  only on disposable window and disappeared with it; no global animation change.

Empty result files for interrupted experiments are not successful evidence.
Earlier browser bring-up failures (missing DISPLAY default, websocket handshake
wording and title matching) were corrected in the harness before successful
baseline runs; no user configuration changed to work around them. Final harness
selects native Wayland explicitly, as the user's running Brave already does.

## Next useful boundary

No evidence-backed permanent correction yet. Avoid attributing the symptom to
VRR/direct scanout (both already off), claiming the old fixed fullscreen-state
bug applies, disabling hardware acceleration, or changing global animation.
A follow-up can profile the YouTube transition's long tasks and isolate Chromium
behavior on the same page. No user profile, extension, browser flag, package,
service, compositor config or website preference changed in this investigation.
No commit/push/reboot. Test artifacts are repository-only.


## Follow-up: identify long tasks and test official ambient control

Owner asks again whether the remaining delay can be corrected. Active Environment
is now Hytale (generation97014bb7-aa82-41fd-aaff-2833e2e41033); follow-up probes
ran there, independently of previous Faculdade measurements. Existing owner Brave
window was1496x778logical outside fullscreen; disposable test tiled beside it,
so test geometry is not identical to owner's single-window layout.

Added `profile-youtube.py` with CDP CPU profiling and Long Animation Frames
attribution. YouTube's document fullscreenchange/setFullscreen and responsive
MediaQueryList/change queryHandler account for long tasks. Sample handler times
~91–125ms for setFullscreen and~150–202ms for responsive queryHandler; source
bundles are YouTube kevlar modules. This supports page main-thread work as a
contributor, not exclusive attribution of every visual/GPU symptom to YouTube.
Profiler startup introduced large unrelated gaps in initial profile; those
max-gap values must not be compared directly with unprofiled baselines. Follow-up
clears telemetry after profiler startup to avoid including that initialization.

Official Ambient mode menu checkbox was observed true and toggled false in the
throwaway profile (not merely hidden with CSS). Four subsequent transitions still
had page RAF gaps251.8–350ms. This is not a validated fix, so no owner preference
changed. Videos were paused/ready4 during the CPU profile; it measures page
transitions, not uninterrupted real-stream playback performance.

Related upstream report https://github.com/brave/brave-browser/issues/56204
(open at lookup) describes a similar fullscreenchange main-thread stall on macOS,
a different OS/version; it is supporting context, not proof of this Linux cause
or evidence of a current fix. No browser downgrade/flag, extension change,
YouTube preference or compositor setting was deployed. No commit/push/reboot.
A reliable permanent correction remains unavailable from this investigation.
