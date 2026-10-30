-- APX environment desktop. This deliberately follows the HUB's visual profile.
-- Refer to the wiki for more information.
-- https://wiki.hypr.land/Configuring/Start/

-- Please note not all available settings / options are set here.
-- For a full list, see the wiki

-- You can (and should!!) split this configuration into multiple files
-- Create your files separately and then require them like this:
-- require("myColors")


------------------
---- MONITORS ----
------------------

-- See https://wiki.hypr.land/Configuring/Basics/Monitors/
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = 1.25,
})

-- An Environment-local choice made in QuickShell; no Host display settings.
local monitorLayout = "/home/apx/.config/hypr/apx-monitors.lua"
local monitorLayoutFile = io.open(monitorLayout, "r")
if monitorLayoutFile then
    monitorLayoutFile:close()
    dofile(monitorLayout)
end


---------------------
---- MY PROGRAMS ----
---------------------

-- Set programs that you use
local terminal    = "/usr/bin/kitty --directory /home/apx"


-------------------
---- AUTOSTART ----
-------------------

-- See https://wiki.hypr.land/Configuring/Basics/Autostart/

-- Autostart necessary processes (like notifications daemons, status bars, etc.)
-- Or execute your favorite apps at launch like this:
--
hl.on("hyprland.start", function ()
  hl.exec_cmd("/home/apx/.local/bin/apx-input-startup-audit-v1")
  hl.exec_cmd("/home/apx/.local/bin/apx-shell-v1")
end)


-------------------------------
---- ENVIRONMENT VARIABLES ----
-------------------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Environment-variables/

-- Apply Environment-local language preferences to applications launched by Hyprland.
local localeFile = io.open("/home/apx/.config/apx/locale.env", "r")
if localeFile then
    local localeKeys = { LANG = true, LANGUAGE = true, LC_MESSAGES = true,
        LC_TIME = true, LC_NUMERIC = true, LC_MONETARY = true }
    for line in localeFile:lines() do
        local key, value = line:match("^([A-Z_]+)=([%w_%.@:%-]+)$")
        if key and localeKeys[key] then hl.env(key, value) end
    end
    localeFile:close()
end

hl.env("XDG_DATA_DIRS", "/home/apx/.local/share/flatpak/exports/share:/var/lib/flatpak/exports/share:/usr/local/share:/usr/share")
-- Qt applications use the same themed native file chooser as other apps.
hl.env("QT_QPA_PLATFORMTHEME", "xdgdesktopportal")
hl.env("GTK_USE_PORTAL", "1")
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")


-----------------------
----- PERMISSIONS -----
-----------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Permissions/
-- Please note permission changes here require a Hyprland restart and are not applied on-the-fly
-- for security reasons

-- hl.config({
--   ecosystem = {
--     enforce_permissions = true,
--   },
-- })

-- hl.permission("/usr/(bin|local/bin)/grim", "screencopy", "allow")
-- hl.permission("/usr/(lib|libexec|lib64)/xdg-desktop-portal-hyprland", "screencopy", "allow")
-- hl.permission("/usr/(bin|local/bin)/hyprpm", "plugin", "allow")


-----------------------
---- LOOK AND FEEL ----
-----------------------

-- Refer to https://wiki.hypr.land/Configuring/Basics/Variables/
hl.config({
    general = {
        gaps_in  = 5,
        gaps_out = 20,

        border_size = 2,

        col = {
            active_border   = "rgba(ffffffff)",
            inactive_border = "rgba(26343aff)",
        },

        -- Set to true to enable resizing windows by clicking and dragging on borders and gaps
        resize_on_border = false,

        -- Please see https://wiki.hypr.land/Configuring/Advanced-and-Cool/Tearing/ before you turn this on
        allow_tearing = false,

        layout = "dwindle",
    },

    decoration = {
        rounding       = 10,
        rounding_power = 2,

        -- Change transparency of focused and unfocused windows
        active_opacity   = 1.0,
        inactive_opacity = 1.0,

        shadow = {
            enabled      = true,
            range        = 4,
            render_power = 3,
            color        = 0xee1a1a1a,
        },

        blur = {
            enabled   = true,
            size      = 3,
            passes    = 1,
            vibrancy  = 0.1696,
        },
    },

    animations = {
        enabled = true,
    },
})

-- Default curves and animations, see https://wiki.hypr.land/Configuring/Advanced-and-Cool/Animations/
hl.curve("easeOutQuint",   { type = "bezier", points = { {0.23, 1},    {0.32, 1}    } })
hl.curve("easeInOutCubic", { type = "bezier", points = { {0.65, 0.05}, {0.36, 1}    } })
hl.curve("linear",         { type = "bezier", points = { {0, 0},       {1, 1}       } })
hl.curve("almostLinear",   { type = "bezier", points = { {0.5, 0.5},   {0.75, 1}    } })
hl.curve("quick",          { type = "bezier", points = { {0.15, 0},    {0.1, 1}     } })
-- Overlay fade matches the 160ms OutCubic QuickShell menu transition.
hl.curve("apxMenuOutCubic", { type = "bezier", points = { {0.215, 0.61}, {0.355, 1} } })

-- Workspace release glides to rest without overshoot; finger tracking stays 1:1.
hl.curve("apxWorkspaceGlide", { type = "bezier", points = { {0.22, 1}, {0.36, 1} } })

-- Soft window entrance with a small, damped overshoot.
hl.curve("apxSoftWindowOpen", { type = "spring", mass = 1, stiffness = 220, dampening = 18 })

-- Default springs
hl.curve("easy",           { type = "spring", mass = 1, stiffness = 238.1191, dampening = 24.21279333 })

hl.animation({ leaf = "global",        enabled = true,  speed = 10,   bezier = "default" })
hl.animation({ leaf = "border",        enabled = true,  speed = 5.39, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows",       enabled = true,  speed = 2.8, bezier = "apxMenuOutCubic" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 2.8, bezier = "apxMenuOutCubic", style = "popin 96%" })
-- Keep tiled layout reflow in step with window entrances; avoid the inherited spring.
hl.animation({ leaf = "windowsMove", enabled = true, speed = 2.4, bezier = "apxMenuOutCubic" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.8, bezier = "apxMenuOutCubic", style = "popin 96%" })
hl.animation({ leaf = "fadeIn", enabled = true, speed = 2.8, bezier = "apxMenuOutCubic" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 1.8, bezier = "apxMenuOutCubic" })
hl.animation({ leaf = "fade",          enabled = true,  speed = 3.03, bezier = "quick" })
hl.animation({ leaf = "layers",        enabled = true,  speed = 3.81, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 3.0, bezier = "apxMenuOutCubic", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 2.2, bezier = "apxMenuOutCubic", style = "fade" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 2.0, bezier = "apxMenuOutCubic" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.8, bezier = "apxMenuOutCubic" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 4.2, bezier = "apxWorkspaceGlide", style = "slide" })
hl.animation({ leaf = "workspacesIn", enabled = true, speed = 4.2, bezier = "apxWorkspaceGlide", style = "slide" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 4.2, bezier = "apxWorkspaceGlide", style = "slide" })
hl.animation({ leaf = "zoomFactor",    enabled = true,  speed = 7,    bezier = "quick" })

-- Floating dialogs must not change the border or geometry of the tiled parent.
hl.window_rule({
    name = "apx-single-window-no-border",
    match = { float = false, workspace = "w[tv1]" },
    border_size = 0,
})

-- Ref https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/
-- "Smart gaps" / "No gaps when only"
-- uncomment all if you wish to use that.
-- hl.workspace_rule({ workspace = "w[tv1]", gaps_out = 0, gaps_in = 0 })
-- hl.workspace_rule({ workspace = "f[1]",   gaps_out = 0, gaps_in = 0 })
-- hl.window_rule({
--     name  = "no-gaps-wtv1",
--     match = { float = false, workspace = "w[tv1]" },
--     border_size = 0,
--     rounding    = 0,
-- })
-- hl.window_rule({
--     name  = "no-gaps-f1",
--     match = { float = false, workspace = "f[1]" },
--     border_size = 0,
--     rounding    = 0,
-- })

-- See https://wiki.hypr.land/Configuring/Layouts/Dwindle-Layout/ for more
hl.config({
    dwindle = {
        preserve_split = true, -- You probably want this
    },
})

-- See https://wiki.hypr.land/Configuring/Layouts/Master-Layout/ for more
hl.config({
    master = {
        new_status = "master",
    },
})

-- See https://wiki.hypr.land/Configuring/Layouts/Scrolling-Layout/ for more
hl.config({
    scrolling = {
        fullscreen_on_one_column = true,
    },
})

----------------
----  MISC  ----
----------------

hl.config({
    misc = {
        focus_on_activate = true,
        -- QuickShell normally paints the rotating landscape layer. Keep the
        -- compositor fallback plain black while that layer restarts.
        force_default_wallpaper = 0,
        background_color = 0xff000000,
        disable_hyprland_logo   = true,
        disable_splash_rendering = true,
    },
})


---------------
---- INPUT ----
---------------

hl.config({
    input = {
        kb_layout  = "pt",
        kb_variant = "",
        kb_model   = "pc105",
        kb_options = "terminate:ctrl_alt_bksp",
        kb_rules   = "",

        follow_mouse = 1,

        sensitivity = 0, -- -1.0 - 1.0, 0 means no modification.

        touchpad = {
            -- Content follows the fingers: dragging two fingers upward moves
            -- down through the page, matching the owner's requested direction.
            natural_scroll = true,
            disable_while_typing = false,
        },
    },
})

hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace"
})

-- Example per-device config
-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Devices/ for more
hl.device({
    name        = "epic-mouse-v1",
    sensitivity = -0.5,
})


---------------------
---- KEYBINDINGS ----
---------------------

local mainMod = "SUPER" -- Sets "Windows" key as main modifier
-- Recover pointer/focus on the laptop without closing windows or disabling HDMI.
hl.bind("SUPER + CTRL + Home", hl.dsp.exec_cmd("/home/apx/.local/bin/apx-laptop-action-v1 display-home"))

-- Example binds, see https://wiki.hypr.land/Configuring/Basics/Binds/ for more
hl.bind(mainMod .. " + Q", hl.dsp.exec_cmd(terminal))
hl.bind("CTRL + SHIFT + Escape", hl.dsp.exec_cmd("/home/apx/.local/bin/apx-task-manager"))
local closeWindowBind = hl.bind(mainMod .. " + C", hl.dsp.window.close())
-- closeWindowBind:set_enabled(false)
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd("quickshell -c apx ipc call host openEnvironments"))
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen())
hl.bind(mainMod .. " + A", hl.dsp.exec_cmd("quickshell -c apx ipc call host toggleControls"))
hl.bind(mainMod .. " + D", hl.dsp.exec_cmd("quickshell -c apx ipc call host toggleCalendar"))
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd("quickshell -c apx ipc call host toggleBattery"))
-- SUPER+Q is local. SUPER+H asks the capability-aware shell to open its
-- terminal action, using the broker for this active graphical Environment.
hl.bind(mainMod .. " + H", hl.dsp.exec_cmd("quickshell -c apx ipc call host openTerminal"))
-- Executor- and IPC-independent escape: Hyprland handles this dispatcher
-- internally even if its runtime sockets or the APX shell are unavailable.
hl.bind(mainMod .. " + M", hl.dsp.exit())
hl.bind(mainMod .. " + V", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd("quickshell -c apx ipc call host openApplications"))
-- Open or focus the file manager as the current Environment's desktop user.
-- The owner retains this binding even though Fn+F7 emits the same chord.
hl.bind(mainMod .. " + P", hl.dsp.exec_cmd("quickshell -c apx ipc call host openFiles"))
hl.bind(mainMod .. " + J", hl.dsp.layout("togglesplit"))    -- dwindle only

-- Move focus with mainMod + arrow keys
hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }))

-- Follow the focused window and pointer to the adjacent display.
hl.bind("SUPER + SHIFT + Left", hl.dsp.exec_cmd("/home/apx/.local/bin/apx-laptop-action-v1 window-left"))
hl.bind("SUPER + SHIFT + Right", hl.dsp.exec_cmd("/home/apx/.local/bin/apx-laptop-action-v1 window-right"))

-- Switch workspaces with mainMod + [0-9]
-- Move active window to a workspace with mainMod + SHIFT + [0-9]
for i = 1, 10 do
    local key = i % 10 -- 10 maps to key 0
    hl.bind(mainMod .. " + " .. key,             hl.dsp.focus({ workspace = i}))
    hl.bind(mainMod .. " + SHIFT + " .. key,     hl.dsp.window.move({ workspace = i }))
end

-- Example special workspace (scratchpad)
hl.bind(mainMod .. " + S",         hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }))

-- Scroll through existing workspaces with mainMod + scroll
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))

-- Move/resize windows with mainMod + LMB/RMB and dragging
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Use only semantic multimedia symbols emitted by firmware while Fn is held.
-- The bridge handles the two semantic brightness codes and Print Screen; it
-- deliberately ignores every raw F1--F12 code. Fn+F8 stays on the separate
-- Host-owned kernel rfkill path and is not leased into an Environment.
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("quickshell -c apx ipc call host volumeUp"),       { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("quickshell -c apx ipc call host volumeDown"),     { locked = true, repeating = true })
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("quickshell -c apx ipc call host volumeMute"),     { locked = true })
hl.bind("XF86AudioMicMute",     hl.dsp.exec_cmd("quickshell -c apx ipc call host microphoneMute"), { locked = true })

local laptopAction = "/home/apx/.local/bin/apx-laptop-action-v1"
hl.bind("XF86Display", hl.dsp.exec_cmd(laptopAction .. " display-cycle"), { locked = true })
hl.bind("XF86Launch1", hl.dsp.exec_cmd(laptopAction .. " apps"), { locked = true })
hl.bind("XF86Calculator", hl.dsp.exec_cmd(laptopAction .. " calculator"), { locked = true })
hl.bind("F13", hl.dsp.exec_cmd(laptopAction .. " apps"), { locked = true })
hl.bind("F16", hl.dsp.exec_cmd(laptopAction .. " calculator"), { locked = true })

local touchpadEnabled = true
local function toggleTouchpad()
    touchpadEnabled = not touchpadEnabled
    hl.device({ name = "elan06fa:00-04f3:31dd-touchpad", enabled = touchpadEnabled })
    if touchpadEnabled then
        hl.exec_cmd("quickshell -c apx ipc call host hotkeyTouchpadOn")
    else
        hl.exec_cmd("quickshell -c apx ipc call host hotkeyTouchpadOff")
    end
end
hl.bind("XF86TouchpadToggle", toggleTouchpad, { locked = true })
hl.bind("F14", toggleTouchpad, { locked = true })
-- Requires playerctl
hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("playerctl next"),       { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),   { locked = true })


--------------------------------
---- WINDOWS AND WORKSPACES ----
--------------------------------

-- See https://wiki.hypr.land/Configuring/Basics/Window-Rules/
-- and https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/

-- Example window rules that are useful

local suppressMaximizeRule = hl.window_rule({
    -- Ignore maximize requests from all apps. You'll probably like this.
    name  = "suppress-maximize-events",
    match = { class = ".*" },

    suppress_event = "maximize",
})
-- suppressMaximizeRule:set_enabled(false)

hl.window_rule({
    -- Fix some dragging issues with XWayland
    name  = "fix-xwayland-drags",
    match = {
        class      = "^$",
        title      = "^$",
        xwayland   = true,
        float      = true,
        fullscreen = false,
        pin        = false,
    },

    no_focus = true,
})

-- Layer rules also return a handle.
-- local overlayLayerRule = hl.layer_rule({
--     name  = "no-anim-overlay",
--     match = { namespace = "^my-overlay$" },
--     no_anim = true,
-- })
-- overlayLayerRule:set_enabled(false)

-- Hyprland-run windowrule
hl.window_rule({
    name  = "move-hyprland-run",
    match = { class = "hyprland-run" },

    move  = "20 monitor_h-120",
    float = true,
})

-- Owner-accepted adaptive pointer motion and uniform scrolling.
-- Device-specific so external mice retain their own acceleration and scrolling.
hl.device({
    name = "elan06fa:00-04f3:31dd-touchpad",
    accel_profile = "adaptive",
    sensitivity = -0.30,
    scroll_factor = 0.55,
    natural_scroll = true,
})

-- Persisted external-mouse choices from the Control Centre override the base.
local mouseChoice = "/home/apx/.config/hypr/apx-mouse-sensitivity.lua"
local mouseChoiceFile = io.open(mouseChoice, "r")
if mouseChoiceFile then
    mouseChoiceFile:close()
    dofile(mouseChoice)
end

-- Environment-local choices edited by APX Settings.
for _, choice in ipairs({"apx-desktop-preferences.lua", "apx-shortcuts.lua", "apx-display-preferences.lua"}) do
    local path = "/home/apx/.config/hypr/" .. choice
    local file = io.open(path, "r")
    if file then file:close(); dofile(path) end
end

-- Small folder customization controls stay out of the tiled application layout.
hl.window_rule({
    name = "apx-folder-controls",
    match = { title = "^(Cor da pasta|Editar etiquetas)$" },
    float = true,
})

-- Main file-manager windows enter like the resident menus.
-- File dialogs share the soft entrance; progress windows remain immediate.
hl.window_rule({
    name = "apx-thunar-menu-animation",
    match = { class = "^(thunar|Thunar|org.xfce.Thunar)$" },
    animation = "popin 90%",
    border_size = 2,
})

-- APX coordinated motion v2: the launcher rises from the screen bottom.
-- QuickShell menus animate internally and retain their own content transition.
hl.layer_rule({
    name = "apx-rofi-menu-motion",
    match = { namespace = "^rofi$" },
    animation = "slide bottom",
})
hl.window_rule({
    name = "apx-thunar-modal-dialogs",
    match = { class = "^(thunar|Thunar|org.xfce.Thunar)$", modal = true },
    float = true,
    center = true,
    no_anim = false,
    animation = "popin 94%",
})
hl.window_rule({
    name = "apx-thunar-progress-dialog",
    match = { class = "^(thunar|Thunar|org.xfce.Thunar)$", title = "^(File Operation Progress|Progresso da operação do ficheiro)$" },
    float = true,
    no_anim = true,
})

-- Portal file pickers are dialogs, not another tile beside the document.
hl.window_rule({
    name = "apx-portal-file-dialogs",
    match = { class = "^xdg-desktop-portal-gtk$" },
    float = true,
    center = true,
    size = { "monitor_w*0.78", "monitor_h*0.82" },
    no_anim = false,
    animation = "popin 94%",
})

-- Toggle workspace labels while keeping their icon in the bar.
hl.bind(mainMod .. " + W", hl.dsp.exec_cmd("quickshell -c apx ipc call host toggleWorkspaces"))

-- Environment-local trackpad preference from the Control Centre.
local trackpadChoice = "/home/apx/.config/hypr/apx-trackpad-sensitivity.lua"
local trackpadChoiceFile = io.open(trackpadChoice, "r")
if trackpadChoiceFile then
    trackpadChoiceFile:close()
    dofile(trackpadChoice)
end

-- Independent per-Environment scroll and workspace gesture preferences.
local gestureChoice = "/home/apx/.config/hypr/apx-trackpad-gestures.lua"
local gestureChoiceFile = io.open(gestureChoice, "r")
if gestureChoiceFile then
    gestureChoiceFile:close()
    dofile(gestureChoice)
end

-- Smooth fractional scaling for legacy X11 applications such as the Launcher.
hl.config({xwayland={use_nearest_neighbor=false}})

-- Optional Environment-local native X11 density, enabled by compatible app wrappers.
local x11Density = "/home/apx/.config/hypr/apx-x11-density.lua"
local x11DensityFile = io.open(x11Density, "r")
if x11DensityFile then x11DensityFile:close(); dofile(x11Density) end
