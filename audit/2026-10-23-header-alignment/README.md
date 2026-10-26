# Remove complete title-bar sections — 2026-10-23

Owner clarifies removal means the entire top section, not just title text.
Settings/Task Manager now have no titlebar widget and are undecorated. Files
module no longer injects its header and disables decorations. Task Manager
Advanced action moved to the search/services row, preserving its behavior.
Settings status/error handling retained; app identity/window metadata unchanged.
Existing windows reopened in original workspaces; Files Recent location retained.
Live GTK confirms no Settings/Task Manager titlebar and retained Task Manager
Advanced/services controls. Responsive navigation regression passes; seed7pass.
Source/seed/five homes and pins synchronized. Backups:
20261023T150801Z-controls-followup and20261023T150803Z-controls-followup.
Evidence: audit/2026-10-23-header-alignment/no-title-bars.png. No commit/push.
Supersedes preceding title/header designs. Owner visual acceptance pending.

# Responsive Settings navigation and no visible application titles — 2026-10-23

Owner reports slow Settings navigation, then asks to remove visible titles in
Files/Settings/Task Manager. All three header custom-title slots are empty;
window metadata and existing controls remain. Settings page reads now suspend
rendering and run subprocess queries in a bounded2-worker executor; GTK widget
work stays on the main thread, with a loading indication and disabled partial
form. Generation checks discard stale results on navigation/search/close; queued
requests cancelled and executor shut down on close. No transition delay.
Destroyed replaced widgets now clean up their timers/form tracking. Explicit
user write actions retain their existing paths; navigation performs reads only.

Live test:300ms simulated query returns navigation in2.5ms, GTK heartbeat runs,
stale completion ignored, fresh revisit completes. All other14 real read-only
pages finish; measured navigation calls1–10ms. This is navigation latency, not
system-data availability latency. Nine focused tests pass. Source/seed/five homes
and digest pins synced; both deploy checks0pending. Existing app windows reopened
on their original workspaces. Visual acceptance pending. No commit/push.
Backups20261023T150607Z-controls-followup and20261023T150609Z-controls-followup.
Evidence audit/2026-10-23-header-alignment/navigation-results.json and
check-navigation.py. Files deploy no longer writes unrelated Thunar preferences.

# Aligned application headers and Settings navigation inset — 2026-10-23

Owner requests aligned title dividers across Files/Settings/Task Manager and
Settings sidebar icons further right like Files. Removed theme text-button
vertical margins that made Task Manager header59px; computed header heights now
47px in all three. Files header measured through matching standalone GTK widget;
Settings/Task Manager via actual application classes. Settings category content
inset40px (previous14px), preserving219px sidebar and16px icons. Source/seed/five
homes and digest pins synchronized; deployment0pending. Existing Settings/Task
Manager windows reopened on their original workspaces. Evidence:
audit/2026-10-23-header-alignment/measurements.json. Owner acceptance pending.
No commit/push.

