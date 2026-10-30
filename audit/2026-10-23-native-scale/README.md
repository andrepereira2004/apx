# Native application scaling with monitor size preserved — 2026-10-23

Owner rejected the blanket100% monitor change. Restored faculdade's original
monitor files from the pre-change copies; live output confirmed1920x1080/1.25.
Brave remains native Wayland with its existing app-specific scale untouched.
Added apx-native-scale-v1: local catalogue refresh detects vendor Electron
bundles by sibling resources/app.asar/default_app.asar and generates owned user
desktop overrides. Wrapper requests Wayland only when its session socket is
reachable, retaining arguments and explicit backend choices; custom user entries
are preserved. Vendor updates/removals refresh/remove only managed overrides.
Catalogue now respects user-entry precedence. Existing package hook and session
startup run synchronization, covering future matching native package installs.
No blanket X11 unscaling; Minecraft's accepted native-X11/DPI setup preserved.
Flatpak/AppImage and undetected/legacy X11 applications are not universally fixed.

Source, independent seed and five homes synchronized with runtime/recovery pins;
four behavior tests plus seven seed tests pass, deploy recheck zero pending.
Separate-profile ChatGPT through the installed wrapper verified xwayland=false;
monitor1.25 and Brave native verified simultaneously. Current signed-in ChatGPT
process still needs a complete exit/reopen for backend change; visual acceptance
is pending. No commit/push. Backup20261023T103849Z-controls-followup.
Evidence: audit/2026-10-23-native-scale/verified-live.json.

Reversal: restore helper/catalogue/runtime/seed files using the deployment
backup inventory. Remove only desktop entries with X-APX-Native-Scale=true,
then refresh the application catalogue after reverting its helper invocation.
Do not remove owner overrides. Original monitor snapshots remain beside the
faculdade monitor files as *.before-native-scale-20261023-113156.
