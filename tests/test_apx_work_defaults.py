from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ROOT / "config/work-defaults-v1"
SHELL = ROOT / "config/environment-shell-v1"


class WorkDefaultsTests(unittest.TestCase):
    def test_normal_user_folders_are_environment_local(self) -> None:
        source = (DEFAULTS / "user-dirs.dirs").read_text()
        for name in (
            "Desktop", "Downloads", "Templates", "Public", "Documents",
            "Music", "Pictures", "Videos", "Projects",
        ):
            self.assertIn(f'"$HOME/{name}"', source)
        self.assertNotIn("/var/lib/apx", source)
        self.assertNotIn("/root", source)

    def test_work_defaults_keep_local_file_manager_without_browser(self) -> None:
        source = (DEFAULTS / "mimeapps.list").read_text()
        self.assertNotIn("brave-browser.desktop", source)
        self.assertNotIn("firefox.desktop", source)
        self.assertIn("inode/directory=thunar.desktop", source)
        for forbidden in ("sudo", "machinectl", "/run/apx", "/var/lib/apx"):
            self.assertNotIn(forbidden, source)

    def test_environment_visual_profile_is_the_capability_aware_hub_shell(self) -> None:
        source = (SHELL / "quickshell/apx/shell.qml").read_text()
        for expected in ("#55e6ff", "#246879", "Appearance.fontFamily", "environmentIdentity.role"):
            self.assertIn(expected, source)
        appearance = (SHELL / "quickshell/apx/Appearance.qml").read_text()
        self.assertIn('readonly property string fontFamily: "JetBrains Mono"', appearance)
        self.assertIn("label: root.environmentLabel", source)
        self.assertIn('iconName: "monitor"', source)
        self.assertIn('caption: "Desligar"', (SHELL / "quickshell/apx/ControlDashboard.qml").read_text())

    def test_work_shortcuts_are_local_and_keep_an_emergency_exit(self) -> None:
        source = (SHELL / "hypr/hyprland.lua").read_text()
        self.assertIn('hl.exec_cmd("/home/apx/.local/bin/apx-shell-v1")', source)
        self.assertNotIn("waybar", source.lower())
        self.assertIn("openApplications", source)
        self.assertNotIn("/usr/bin/brave", source)
        self.assertIn('hl.bind(mainMod .. " + E",', source)
        self.assertIn('hl.bind(mainMod .. " + E",', source)
        self.assertIn("openEnvironments", source)
        self.assertIn('hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen())', source)
        self.assertIn('hl.bind(mainMod .. " + P",', source)
        self.assertIn("openFiles", source)
        self.assertNotIn('local fileManager = "/usr/bin/thunar"', source)
        self.assertIn('hl.bind(mainMod .. " + M",', source)
        self.assertIn('hl.bind(mainMod .. " + M", hl.dsp.exit())', source)
        self.assertNotIn("/run/apx/environment-switch-client-v1.py return", source)
        # Matching an existing terminal for scroll tuning grants no launch capability.
        shortcut_source = source.replace('match = { class = "^(kitty|apx-host-console-v1)$" },', '')
        for forbidden in ("apx-hub --switcher", "host-console", "system-power", "coordinated-update"):
            self.assertNotIn(forbidden, shortcut_source)

    def test_environment_shell_launcher_is_single_instance(self) -> None:
        source = (SHELL / "local/bin/apx-shell-v1").read_text()
        self.assertIn("apx-shell-launcher-v1.lock", source)
        self.assertIn("/usr/bin/flock -n 9", source)

    def test_terminal_notifications_expire_and_clear_when_refocused(self) -> None:
        launcher = (SHELL / "local/bin/apx-shell-v1").read_text()
        watcher = (SHELL / "local/bin/apx-notification-focus-v1").read_text()
        mako = (SHELL / "mako/config").read_text()

        self.assertIn("/home/apx/.local/bin/apx-notification-focus-v1", launcher)
        self.assertIn('TERMINAL_APPS = {"kitty", "alacritty"}', watcher)
        self.assertIn('line.startswith("activewindow>>")', watcher)
        self.assertIn('[MAKOCTL, "dismiss", "-n", str(notification_id), "--no-history"]', watcher)
        for app_name in ("kitty", "Alacritty", "alacritty"):
            self.assertIn(f"[app-name={app_name}]", mako)
        self.assertEqual(mako.count("default-timeout=8000"), 3)
        self.assertEqual(mako.split('[app-name="APX Browser"]', 1)[0].count("ignore-timeout=1"), 3)

    def test_terminal_notification_deploy_keeps_shell_launcher_executable(self) -> None:
        deploy = (
            ROOT / "scripts/physical-pilot/deploy-terminal-notification-policy-v1.sh"
        ).read_text()
        executable_install = (
            '/usr/bin/install -o 1000 -g 1000 -m 0700 '
            '"$source_launcher" "$live_launcher"'
        )
        non_executable_install = executable_install.replace("-m 0700", "-m 0600")
        self.assertIn(executable_install, deploy)
        self.assertNotIn(non_executable_install, deploy)

    def test_wallpapers_rotate_on_a_noninteractive_background_layer(self) -> None:
        source = (SHELL / "quickshell/apx/shell.qml").read_text()
        for wallpaper in ("atlantic-coast.png", "alpine-lake.png", "rainforest-stream.png"):
            self.assertIn(wallpaper, source)
            self.assertTrue((SHELL / "apx/wallpapers" / wallpaper).is_file())
        for required in (
            "interval: 15 * 60 * 1000", "model: Quickshell.screens",
            "WlrLayershell.layer: WlrLayer.Background", "mask: Region {}",
            "fillMode: Image.PreserveAspectCrop",
        ):
            self.assertIn(required, source)

    def test_hyprland_fallback_is_plain_black_behind_quickshell(self) -> None:
        lua = (SHELL / "hypr/hyprland.lua").read_text()
        fallback = (SHELL / "hyprland/hyprland.conf").read_text()

        for source in (lua, fallback):
            self.assertIn("force_default_wallpaper = 0", source)
            self.assertIn("disable_hyprland_logo", source)
            self.assertIn("disable_splash_rendering", source)
        self.assertIn("disable_hyprland_logo   = true", lua)
        self.assertIn("disable_splash_rendering = true", lua)
        self.assertNotIn("force_default_wallpaper = -1", lua + fallback)
        self.assertNotIn("disable_hyprland_logo   = false", lua)

    def test_compact_controls_keep_accessible_actions_and_local_files(self) -> None:
        source = (SHELL / "quickshell/apx/shell.qml").read_text()
        dashboard = (SHELL / "quickshell/apx/ControlDashboard.qml").read_text()
        tile = (SHELL / "quickshell/apx/ControlTile.qml").read_text()
        self.assertIn("ControlDashboard {", source)
        self.assertIn("Accessible.name: caption", tile)
        for section in ("connectivity", "brightness"):
            self.assertIn('openControlSection("' + section + '")', dashboard)
        for section in ("wifi", "bluetooth", "audio", "microphone"):
            self.assertIn('openControlSection("' + section + '")', source)
        for action in ("lock", "reboot", "update", "poweroff"):
            self.assertIn('runControlAction("' + action + '")', dashboard)
        self.assertIn('kind: "notifications"; embedded: true', dashboard)
        self.assertNotIn('kind: "media"', dashboard)
        self.assertIn('id: mediaPanel; width: parent.width; kind: "media"', source)
        self.assertIn("function openFiles(): void", source)
        self.assertIn("if (!fileShortcutProcess.running)", source)
        self.assertNotIn("if (!root.isHub && !environmentFilesProcess.running)", source)

    def test_lock_enter_retries_face_or_submits_password(self) -> None:
        lock = (SHELL / "hypr/hyprlock.conf").read_text()
        self.assertIn("ignore_empty_input = false", lock)
        self.assertIn("A autenticar…", lock)
        self.assertNotIn("A VERIFICAR A CARA…", lock)
        self.assertIn("Não foi possível autenticar", lock)
        self.assertIn("cmd[update:300] /home/apx/.local/bin/apx-face-auth-state-v1", lock)
        face_state = (SHELL / "local/bin/apx-face-auth-state-v1").read_text()
        self.assertIn('apx-howdy-camera-', face_state)
        self.assertIn("lock_ancestor", face_state)
        self.assertIn('/usr/lib/howdy/compare.py', face_state)
        self.assertIn('A procurar o teu rosto…', face_state)
        self.assertNotIn('APÓS FALHA', face_state)
        howdy_patch = (ROOT / "config/howdy-v1/howdy-apx/apx-camera-frame-state.patch").read_text()
        self.assertIn("publish_camera_frame_state()", howdy_patch)
        self.assertIn("frame, gsframe = video_capture.read_frame()", howdy_patch)
        self.assertLess(howdy_patch.index("read_frame()"), howdy_patch.rindex("publish_camera_frame_state()"))
        howdy_pkgbuild = (ROOT / "config/howdy-v1/howdy-apx/PKGBUILD").read_text()
        self.assertIn("pkgrel=4", howdy_pkgbuild)
        self.assertIn("apx-camera-frame-state.patch", howdy_pkgbuild)
        self.assertIn('$pkgdir/etc/howdy/config.ini', howdy_pkgbuild)
        pam = (ROOT / "config/howdy-v1/pam/hyprlock").read_text()
        self.assertIn("[success=ok default=1] pam_howdy.so", pam)
        self.assertIn("[success=done default=die] pam_faillock.so authsucc", pam)
        self.assertNotIn("sufficient      pam_howdy.so", pam)
        self.assertIn("pam_howdy runs first", lock)

    def test_bar_uses_floating_pills_with_inset_edges(self) -> None:
        source = (SHELL / "quickshell/apx/shell.qml").read_text()
        bar = source.split("id: bar", 1)[1].split("id: hotkeyOsdWindow", 1)[0]
        self.assertIn("anchors { top: true; left: true; right: true }", bar)
        self.assertIn("margins { left: 8; right: 8 }", bar)
        self.assertIn('color: "transparent"', bar)
        self.assertIn("anchors.left: parent.left\n                anchors.leftMargin: 2", bar)
        self.assertIn("anchors.right: parent.right\n                anchors.rightMargin: 2", bar)

    def test_window_border_distinguishes_keyboard_focus(self) -> None:
        lua = (SHELL / "hypr/hyprland.lua").read_text()
        fallback = (SHELL / "hyprland/hyprland.conf").read_text()
        defaults = (DEFAULTS / "hyprland.conf").read_text()

        self.assertIn("border_size = 2,", lua)
        self.assertIn('active_border   = "rgba(ffffffff)"', lua)
        self.assertIn('inactive_border = "rgba(26343aff)"', lua)
        self.assertNotIn("rgba(33ccffee)", lua)
        self.assertNotIn("rgba(00ff99ee)", lua)
        for source in (fallback, defaults):
            self.assertIn("border_size = 2", source)
            self.assertIn("col.active_border = rgba(ffffffff)", source)
            self.assertIn("col.inactive_border = rgba(26343aff)", source)

    def test_laptop_keys_keep_actions_inside_the_environment(self) -> None:
        source = (SHELL / "hypr/hyprland.lua").read_text()
        helper = (SHELL / "local/bin/apx-laptop-action-v1").read_text()
        self.assertIn("Use only semantic multimedia symbols emitted by firmware while Fn is held", source)
        for key in (
            "XF86AudioMute", "XF86AudioLowerVolume", "XF86AudioRaiseVolume",
            "XF86AudioMicMute", "XF86Display", "XF86TouchpadToggle",
            "XF86Calculator", 'hl.bind("F13"', 'hl.bind("F14"', 'hl.bind("F16"',
        ):
            self.assertIn(key, source)
        for removed in ('"ALT + Tab"', '"CTRL + ALT + Tab"', '"XF86TaskPane"', '"F15"'):
            self.assertNotIn(removed, source)
        for action in ("airplane-status", "display-cycle", "apps", "overview", "calculator", "screenshot"):
            self.assertIn(action, helper)
        for normal_key in ('"Insert"', '"Delete"', '"Home"', '"End"', '"Page_Up"', '"Page_Down"'):
            self.assertNotIn(normal_key, source)
        for forbidden in ("sudo", "machinectl", "/var/lib/apx"):
            self.assertNotIn(forbidden, helper)
        self.assertIn("natural_scroll = true", source)


if __name__ == "__main__":
    unittest.main()
