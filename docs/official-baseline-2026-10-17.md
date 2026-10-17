# Owner-approved APX baseline — 2026-10-17

The owner accepted the currently installed interface and authorized publication of
all relevant accumulated APX structural work and dotfiles. The repository includes
configuration, lifecycle/isolation and installer changes, recovery, network and
authentication integration, application integration, source, tests and dated audit
evidence. Installed games/applications, personal application data and credentials
are not part of this source publication.

The accepted desktop uses the coordinated QuickShell/Rofi animations, common
JetBrains Mono typography and panel alignment, compact bar feedback, workspace
and calendar capsule, and dedicated audio-lines playback capsule. Playback is
removed from Control Centre. See the dated shell documentation for native checks,
backup locations and reversal procedures. Older audit snapshots are historical;
`config/environment-shell-v1` contains the current defaults.

This is the owner's official interface baseline within the experimental physical
pilot. It is not a claim of production readiness or validation on other hardware.

## Publication validation

`python -m unittest discover -s tests -q` executed 1,467 tests in 6.297 seconds:
9 failures, 2 errors, 12 skipped. These unresolved results are recorded below;
they must be assessed before claiming that the complete test suite passes.
No product changes were made solely to satisfy older source assertions during
publication. Earlier native desktop checks remain recorded in dated evidence.

```text
ERROR: test_first_navigation_key_starts_at_first_control (test_apx_battery_menu_actions.BatteryActionTests.test_first_navigation_key_starts_at_first_control)
ERROR: test_popup_click_switches_menu_and_same_button_closes (test_apx_battery_menu_actions.BatteryActionTests.test_popup_click_switches_menu_and_same_button_closes)
FAIL: test_mako_policy_keeps_click_action_corner_and_timeout (test_apx_browser_redirect_v1.BrowserRedirectTests.test_mako_policy_keeps_click_action_corner_and_timeout)
FAIL: test_audio_slider_updates_volume_while_dragging (test_apx_control_center_scale.ControlCenterScaleTests.test_audio_slider_updates_volume_while_dragging)
FAIL: test_control_center_matches_desktop_scale_without_fractional_resampling (test_apx_control_center_scale.ControlCenterScaleTests.test_control_center_matches_desktop_scale_without_fractional_resampling)
FAIL: test_every_keyboard_popup_animates_its_bar_button (test_apx_control_center_scale.ControlCenterScaleTests.test_every_keyboard_popup_animates_its_bar_button)
FAIL: test_popup_opening_uses_one_explicit_forward_animation (test_apx_control_center_scale.ControlCenterScaleTests.test_popup_opening_uses_one_explicit_forward_animation)
FAIL: test_workload_overview_has_room_for_all_actions (test_apx_control_center_scale.ControlCenterScaleTests.test_workload_overview_has_room_for_all_actions)
FAIL: test_native_windows_return_is_internal_and_keeps_password_recovery (test_apx_environment_switch_v1.EnvironmentSwitchV1Tests.test_native_windows_return_is_internal_and_keeps_password_recovery)
FAIL: test_workload_shell_surfaces_return_failure (test_apx_environment_switch_v1.EnvironmentSwitchV1Tests.test_workload_shell_surfaces_return_failure)
FAIL: test_workload_initializes_folders_and_opens_or_focuses (test_apx_file_manager.FileManagerTests.test_workload_initializes_folders_and_opens_or_focuses)
Ran 1467 tests in 6.297s
FAILED (failures=9, errors=2, skipped=12)
```

Staged text was checked for common embedded credential/private-key patterns; no
matches were found. Diff whitespace warnings remain in historical audit evidence,
upstream license text, patch context and several trailing blank lines. Those
artifacts were preserved during publication.
