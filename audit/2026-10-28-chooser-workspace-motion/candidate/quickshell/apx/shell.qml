pragma ComponentBehavior: Bound

import QtQuick
import QtCore
import QtQuick.Window
import QtQuick.Effects
import QtQuick.Controls
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Hyprland
import Quickshell.Widgets
import "GhostLines.js" as GhostLines

ShellRoot {
    id: root

    NotificationToasts { id: notificationToasts }

    // One bar per output; a single shared menu/service state follows its trigger.
    property var selectedBar: null
    readonly property var bar: selectedBar || (barVariants.instances.length ? barVariants.instances[0] : null)
    readonly property var calendarButton: bar ? bar.calendarButton : null
    readonly property var environmentButton: bar ? bar.environmentButton : null
    readonly property var batteryButton: bar ? bar.batteryButton : null
    readonly property var mediaButton: bar ? bar.mediaButton : null
    readonly property var appsButton: bar ? bar.appsButton : null
    readonly property var filesButton: bar ? bar.filesButton : null
    readonly property var controlCenterButton: bar ? bar.controlCenterButton : null


    // Track compositor state directly; empty inactive workspaces stay hidden.
    readonly property var openWorkspaces: Hyprland.workspaces.values.filter(function(workspace) {
        return workspace.id > 0 && (workspace.active || workspace.toplevels.values.length > 0)
    }).sort(function(a, b) { return a.id - b.id })

    FontLoader { source: "file:///home/apx/.local/share/fonts/jetbrains-mono/JetBrainsMono-Regular.ttf" }
    FontLoader { source: "file:///home/apx/.local/share/fonts/jetbrains-mono/JetBrainsMono-Bold.ttf" }

    // Register the trial UI font on reload, including in an existing Qt process.
    FontLoader { source: "file:///home/apx/.local/share/fonts/selawik/selawk.ttf" }
    FontLoader { source: "file:///home/apx/.local/share/fonts/selawik/selawkb.ttf" }
    FontLoader { source: "file:///home/apx/.local/share/fonts/selawik/selawkl.ttf" }
    FontLoader { source: "file:///home/apx/.local/share/fonts/selawik/selawksb.ttf" }
    FontLoader { source: "file:///home/apx/.local/share/fonts/selawik/selawksl.ttf" }


    readonly property bool hasExternalDisplay: {
        for (var i = 0; i < Quickshell.screens.length; ++i) {
            var name = Quickshell.screens[i].name
            if (name && !name.startsWith("eDP-") && !name.startsWith("LVDS-")) return true
        }
        return false
    }
    onHasExternalDisplayChanged: { root.displayLayoutError = "" }
    property string displayLayoutSide: ""
    property string displayLayoutError: ""
    function setDisplayLayout(side) {
        if (displayLayoutProcess.running) return
        root.closePopup()
        displayLayoutProcess.command = ["/home/apx/.local/bin/apx-laptop-action-v1", "display-" + side]
        displayLayoutProcess.running = true
    }
    Process {
        id: displayLayoutProcess
        command: ["/home/apx/.local/bin/apx-laptop-action-v1", "display-status"]
        running: true
        stdout: StdioCollector {
            onStreamFinished: {
                try { root.displayLayoutSide = JSON.parse(text).side || "" } catch (e) {}
            }
        }
        onExited: (code, status) => { root.displayLayoutError = code === 0 ? "" : "Não foi possível alterar os ecrãs." }
    }
    property var pointerDevices: ({mouse:{enabled:true,available:false},trackpad:{enabled:true,available:false}})
    property string pointerPowerError: ""
    function togglePointer(kind) {
        if (pointerPowerProcess.running) return
        pointerPowerError = ""
        pointerPowerProcess.command = ["/home/apx/.local/bin/apx-pointer-power-v1", "toggle", kind]
        pointerPowerProcess.running = true
    }
    Process {
        id: pointerPowerProcess
        command: ["/home/apx/.local/bin/apx-pointer-power-v1", "status"]
        running: true
        stdout: StdioCollector { onStreamFinished: { try { var value = JSON.parse(text); if (JSON.stringify(value) !== JSON.stringify(root.pointerDevices)) root.pointerDevices = value } catch(e) {} } }
        stderr: StdioCollector { onStreamFinished: { if (text.trim().length) root.pointerPowerError = text.trim() } }
        onExited: (code, status) => { if (code !== 0) pointerRefreshTimer.restart() }
    }
    Timer {
        id: pointerRefreshTimer; interval: 500; repeat: true
        running: popup.open && root.popupKind === "controls"
        triggeredOnStart: true
        onTriggered: if (!pointerPowerProcess.running) {
            pointerPowerProcess.command = ["/home/apx/.local/bin/apx-pointer-power-v1", "status"]
            pointerPowerProcess.running = true
        }
    }
    property real pendingMouseSensitivity: NaN
    function setMouseSensitivity(value) {
        mouseSensitivity = Math.max(-100, Math.min(100, Math.round(value * 2 - 100)))
        pendingMouseSensitivity = mouseSensitivity
        mouseSensitivityError = ""
        flushMouseSensitivity()
    }
    function flushMouseSensitivity() {
        if (!Number.isFinite(pendingMouseSensitivity) || mouseSensitivityProcess.running || mouseSensitivityStatusProcess.running) return
        const next = pendingMouseSensitivity
        pendingMouseSensitivity = NaN
        mouseSensitivityProcess.command = ["/home/apx/.local/bin/apx-mouse-sensitivity-v1", "set", String(next)]
        mouseSensitivityProcess.running = true
    }
    function readMouseSensitivity(text) {
        if (!Number.isFinite(pendingMouseSensitivity) && text.trim().length && Number.isFinite(Number(text.trim()))) mouseSensitivity = Number(text.trim())
    }
    Process {
        id: mouseSensitivityStatusProcess
        command: ["/home/apx/.local/bin/apx-mouse-sensitivity-v1", "get"]
        running: true
        stdout: StdioCollector { onStreamFinished: if (!mouseSensitivityProcess.running) root.readMouseSensitivity(text) }
        onExited: Qt.callLater(root.flushMouseSensitivity)
    }
    Process {
        id: mouseSensitivityProcess
        stdout: StdioCollector { onStreamFinished: root.readMouseSensitivity(text) }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.mouseSensitivityError = text.trim() }
        onExited: (code, status) => {
            if (code !== 0) { if (!root.mouseSensitivityError.length) root.mouseSensitivityError = "Não foi possível alterar a sensibilidade."; mouseSensitivityStatusProcess.running = true }
            Qt.callLater(root.flushMouseSensitivity)
        }
    }

    property real pendingTrackpadCursor: NaN
    function setTrackpadSensitivity(value) {
        trackpadSensitivity = Math.max(-100, Math.min(100, Math.round(value * 2 - 100)))
        pendingTrackpadCursor = trackpadSensitivity
        trackpadSensitivityError = ""
        flushTrackpadCursor()
    }
    function flushTrackpadCursor() {
        if (!Number.isFinite(pendingTrackpadCursor) || trackpadSensitivityProcess.running || trackpadSensitivityStatusProcess.running) return
        const next = pendingTrackpadCursor
        pendingTrackpadCursor = NaN
        trackpadSensitivityProcess.command = ["/home/apx/.local/bin/apx-trackpad-sensitivity-v1", "set", String(next)]
        trackpadSensitivityProcess.running = true
    }
    function readTrackpadCursor(text) {
        if (!Number.isFinite(pendingTrackpadCursor) && text.trim().length && Number.isFinite(Number(text.trim()))) trackpadSensitivity = Number(text.trim())
    }
    Process {
        id: trackpadSensitivityStatusProcess
        command: ["/home/apx/.local/bin/apx-trackpad-sensitivity-v1", "get"]
        running: true
        stdout: StdioCollector { onStreamFinished: if (!trackpadSensitivityProcess.running) root.readTrackpadCursor(text) }
        onExited: Qt.callLater(root.flushTrackpadCursor)
    }
    Process {
        id: trackpadSensitivityProcess
        stdout: StdioCollector { onStreamFinished: root.readTrackpadCursor(text) }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.trackpadSensitivityError = text.trim() }
        onExited: (code, status) => {
            if (code !== 0) { if (!root.trackpadSensitivityError.length) root.trackpadSensitivityError = "Não foi possível alterar a sensibilidade."; trackpadSensitivityStatusProcess.running = true }
            Qt.callLater(root.flushTrackpadCursor)
        }
    }

    property var trackpadGestures: ({scroll:55,workspaces:100})
    property var pendingTrackpadGestures: ({})
    property string trackpadGesturesError: ""
    function readTrackpadGestures(text) {
        try {
            const value = JSON.parse(text)
            if (Number.isFinite(value.scroll) && Number.isFinite(value.workspaces)) {
                for (const kind of Object.keys(pendingTrackpadGestures)) value[kind] = pendingTrackpadGestures[kind]
                trackpadGestures = value
            }
        } catch (error) {}
    }
    function setTrackpadGesture(kind, value) {
        const raw = Math.max(25, Math.min(200, Math.round(25 + value * 1.75)))
        const next = Object.assign({}, trackpadGestures)
        next[kind] = raw
        trackpadGestures = next
        const pending = Object.assign({}, pendingTrackpadGestures)
        pending[kind] = raw
        pendingTrackpadGestures = pending
        trackpadGesturesError = ""
        flushTrackpadGestures()
    }
    function flushTrackpadGestures() {
        if (trackpadGesturesProcess.running || trackpadGesturesStatusProcess.running) return
        const kinds = Object.keys(pendingTrackpadGestures)
        if (!kinds.length) return
        const kind = kinds[0], raw = pendingTrackpadGestures[kind]
        const remaining = Object.assign({}, pendingTrackpadGestures)
        delete remaining[kind]
        pendingTrackpadGestures = remaining
        trackpadGesturesProcess.command = ["/home/apx/.local/bin/apx-trackpad-gestures-v1", "set", kind, String(raw)]
        trackpadGesturesProcess.running = true
    }
    Process {
        id: trackpadGesturesStatusProcess
        command: ["/home/apx/.local/bin/apx-trackpad-gestures-v1", "get"]
        running: true
        stdout: StdioCollector { onStreamFinished: if (!trackpadGesturesProcess.running) root.readTrackpadGestures(text) }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.trackpadGesturesError = text.trim() }
        onExited: Qt.callLater(root.flushTrackpadGestures)
    }
    Process {
        id: trackpadGesturesProcess
        stdout: StdioCollector { onStreamFinished: root.readTrackpadGestures(text) }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.trackpadGesturesError = text.trim() }
        onExited: (code, status) => {
            if (code !== 0) { if (!root.trackpadGesturesError.length) root.trackpadGesturesError = "Não foi possível alterar os gestos."; trackpadGesturesStatusProcess.running = true }
            Qt.callLater(root.flushTrackpadGestures)
        }
    }

    property color cyan: "#55e6ff"
    property color cyanDim: "#246879"
    // Keep the bar and menus consistently readable while retaining a modest
    // amount of the background through both surfaces.
    // Background alpha is independent of foreground and animation opacity.
    property color panel: Appearance.backgroundColor("#101117", "menus")
    property color popupPanel: Appearance.backgroundColor("#101117", "menus")
    // Opaque RGB, identical to Hyprland's inactive window outline.
    property color shellBorder: "#343947"
    property color card: "#f21b1e22"
    property color textMain: "#d9dcea"
    property color textDim: "#a4abc0"
    // Control-centre actions use the same near-background surfaces as the
    // other menus. Cyan is reserved for state and emphasis, not large fills.
    readonly property color controlButtonSurface: Appearance.tintButtons ? Appearance.surface : "#1b1d26"
    readonly property color controlButtonHover: Appearance.tintButtons ? Appearance.hover : "#292d3a"
    readonly property color controlButtonActive: Appearance.tintButtons ? Appearance.active : "#353a4a"
    readonly property color controlButtonOutline: Appearance.tintButtons ? Appearance.border : "#414654"
    readonly property var wallpaperSources: [
        "file:///home/apx/.config/apx/wallpapers/atlantic-coast.png",
        "file:///home/apx/.config/apx/wallpapers/alpine-lake.png",
        "file:///home/apx/.config/apx/wallpapers/rainforest-stream.png"
    ]
    readonly property url currentWallpaper: Appearance.wallpaper.length ? Appearance.wallpaper : root.wallpaperSources[root.wallpaperIndex]
    property int wallpaperIndex: Math.floor(Date.now() / 900000) % wallpaperSources.length
    property var environmentIdentity: ({ name: "", display_name: "", role: "" })
    property string environmentSwitchError: ""
    property bool environmentSwitchPending: false
    property bool startupCover: true
    property bool startupBarRendered: false
    readonly property bool startupReady: identityReady && sessionKindReady && startupBarRendered
    onStartupReadyChanged: if (startupReady) startupCover = false
    property bool environmentSwitchDispatched: false
    onEnvironmentSwitchPendingChanged: if (!environmentSwitchPending) environmentSwitchDispatched = false
    property int environmentSwitchProgress: 0
    property var environmentCatalog: []
    property var pendingEnvironmentCatalog: null
    property var environmentStorageState: ({ available_bytes: 0, total_bytes: 0, sizes: ({}) })
    property string selectedEnvironmentName: ""
    property string selectedEnvironmentGeneration: ""
    property bool environmentCreateOpen: false
    property bool environmentEditOpen: false
    property bool environmentDeleteConfirm: false
    property bool nativeRecoveryDiscardConfirm: false
    property int environmentDeleteFocusIndex: 0
    property string environmentDraftName: ""
    property string environmentDraftDescription: ""
    property string environmentEditTitle: ""
    property string environmentEditDescription: ""
    property string environmentEditIcon: "box"
    readonly property var environmentIconChoices: ["box", "monitor", "terminal", "book-open", "swords", "shield-check", "globe", "folder", "cpu", "music", "camera", "paintbrush", "pickaxe", "hexagon", "zap", "satellite-dish", "calculator", "calendar-days", "book-a", "keyboard", "mouse", "touchpad", "gpu", "hard-drive", "usb", "video", "audio-lines", "mic", "leaf", "scale", "ghost", "package", "package-open", "folder-open", "square-stack", "layout-dashboard", "layout-grid", "settings", "lock-keyhole", "plane", "gamepad-2", "joystick", "trophy", "dice-5", "target", "rocket", "puzzle", "medal"]
    function environmentIcon(item) {
        return item && environmentIconChoices.indexOf(item.icon) >= 0 ? item.icon : "box"
    }
    readonly property string activeEnvironmentIcon: isHub ? "graph-star" : environmentIcon(environmentIdentity)
    property string environmentSystemKind: "arch"
    property int environmentNativeWindowsSizeGib: 120
    property var nativeCreationPreview: ({})
    property string nativeV3Confirmation: ""
    onEnvironmentDraftNameChanged: nativeCreationPreview = ({})
    onEnvironmentDraftDescriptionChanged: nativeCreationPreview = ({})
    onEnvironmentNativeWindowsSizeGibChanged: nativeCreationPreview = ({})
    Process {
        id: nativeCreationPreviewProcess
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var value = JSON.parse(text)
                    if (value.target === root.environmentDraftName && value.size_gib === root.environmentNativeWindowsSizeGib)
                        root.nativeCreationPreview = value
                } catch (error) { root.environmentSwitchError = "Não foi possível ler a preparação Windows." }
            }
        }
        stderr: StdioCollector { onStreamFinished: { if (text.trim()) root.environmentSwitchError = text.trim() } }
    }
    property string environmentDesktopPreset: "intermediate"
    property bool environmentCreateCustomizeOpen: false
    property string environmentFeatureDrawer: ""
    property string environmentFeatureInfo: ""
    property var environmentSelectedModules: ({})
    readonly property var environmentModuleCatalog: [
        { key: "system", label: "Núcleo do sistema", detail: "Arranque, certificados e comandos essenciais.", programs: "BASE · base, ca-certificates, iproute2, less, nano", mib: 420, deps: [] },
        { key: "cli-aur", label: "Terminal e instalação", detail: "Terminal, ajuda, Git e compilação de pacotes AUR.", programs: "BASE · Alacritty, Foot, Git, man, sudo, base-devel", mib: 260, deps: ["system"] },
        { key: "graphical", label: "Ambiente gráfico", detail: "Janelas, bloqueio, menu de aplicações e barra APX.", programs: "BASE · Hyprland, Hyprlock, Rofi, QuickShell", mib: 520, deps: ["system"] },
        { key: "desktop-integration", label: "Integração do desktop", detail: "Notificações, portais, segredos e aplicações Flatpak.", programs: "BASE · Mako, Flatpak, Polkit, GNOME Keyring", mib: 170, deps: ["graphical"] },
        { key: "locale-input", label: "Português, fontes e teclado", detail: "Acentos, layout do teclado, fontes e diretórios pessoais.", programs: "BASE · Noto Fonts, xkeyboard-config, xdg-user-dirs", mib: 190, deps: ["system"] },
        { key: "network", label: "Wi-Fi e Internet", detail: "Acesso à Internet e controlo de redes pela APX.", programs: "BASE · integração APX, iproute2, iputils", mib: 70, deps: ["system"] },
        { key: "bluetooth", label: "Bluetooth", detail: "Ligar, emparelhar e esquecer dispositivos Bluetooth.", programs: "BASE · controlo Bluetooth mediado pela APX", mib: 35, deps: ["system"] },
        { key: "audio", label: "Som e microfone", detail: "Reprodução, gravação e controlos de volume.", programs: "BASE · PipeWire, WirePlumber", mib: 125, deps: ["system"] },
        { key: "graphics", label: "Aceleração gráfica e monitores", detail: "OpenGL/Vulkan e suporte para ecrãs internos e externos.", programs: "BASE · Mesa, Vulkan Radeon, NVIDIA HDMI/DisplayPort", mib: 390, deps: ["graphical"] },
        { key: "power", label: "Bateria e brilho", detail: "Estado da bateria, brilho do ecrã e teclado iluminado.", programs: "BASE · controlos de hardware mediados pela APX", mib: 30, deps: ["graphical"] },
        { key: "devices-storage", label: "USB, telemóvel e discos", detail: "Montagem assistida de discos, MTP, câmaras e partilhas SMB.", programs: "BASE · UDisks, udiskie, GVFS, MTP, SMB", mib: 120, deps: ["system"] },
        { key: "files", label: "Ficheiros, imagens e arquivos", detail: "Navegar em pastas, pré-visualizar imagens e abrir arquivos.", programs: "BASE · Thunar, File Roller, Ristretto, Tumbler", mib: 115, deps: ["desktop-integration", "devices-storage"] },
        { key: "web-documents", label: "Internet e documentos PDF", detail: "Navegação web e leitura de documentos PDF.", programs: "INSTALA · Brave, Evince", mib: 360, deps: ["desktop-integration", "network"] },
        { key: "multimedia", label: "Vídeo, áudio e codecs", detail: "Reproduzir formatos multimédia comuns.", programs: "INSTALA · MPV, FFmpeg, GStreamer codecs", mib: 240, deps: ["desktop-integration", "audio", "graphics"] },
        { key: "office", label: "Documentos, folhas e apresentações", detail: "Suite ArtCraft nativa para Linux, sem Wine ou login Microsoft.", programs: "INSTALA · WordCraft, GridCraft, DeckCraft", mib: 220, deps: ["desktop-integration", "locale-input"] },
        { key: "communication", label: "Câmara e videochamadas", detail: "Ferramentas de diagnóstico para webcam e vídeo.", programs: "INSTALA · v4l-utils", mib: 55, deps: ["desktop-integration", "network", "audio", "graphics"] },
        { key: "iphone-integration", label: "Partilha com iPhone e iPad", detail: "LocalSend para ficheiros, fotos e texto. Requer ligar o dispositivo numa rede autorizada.", programs: "INSTALA · LocalSend", mib: 90, deps: ["desktop-integration", "network"] },
        { key: "printing-scanning", label: "Impressoras e scanners", detail: "Configurar, imprimir e digitalizar documentos.", programs: "INSTALA · CUPS, SANE, Simple Scan, system-config-printer", mib: 145, deps: ["desktop-integration", "network", "devices-storage"] },
        { key: "development", label: "Programação e containers", detail: "Compilar software, desenvolver em várias linguagens e usar containers.", programs: "INSTALA · CMake, Ninja, Node.js, npm, Podman, pip, Rust", mib: 1150, deps: ["cli-aur"] },
        { key: "shortcuts", label: "Atalhos APX", detail: "Abrir rapidamente o controlo, calendário, bateria e Environments.", programs: "BASE · ponte de atalhos SUPER+A/B/D/E", mib: 8, deps: ["graphical"] }
    ]
    readonly property var environmentModuleGroups: [
        { key: "base", label: "1 · SISTEMA E AMBIENTE DE TRABALHO", description: "Terminal, janelas, idioma e integração do desktop", modules: ["system", "cli-aur", "graphical", "desktop-integration", "locale-input"] },
        { key: "hardware", label: "2 · INTERNET, SOM E DISPOSITIVOS", description: "Rede, Bluetooth, áudio, gráficos, bateria e USB", modules: ["network", "bluetooth", "audio", "graphics", "power", "devices-storage"] },
        { key: "daily", label: "3 · APLICAÇÕES DO DIA A DIA", description: "Ficheiros, browser, PDF, vídeo e codecs", modules: ["files", "web-documents", "multimedia"] },
        { key: "extras", label: "4 · TRABALHO E FERRAMENTAS AVANÇADAS", description: "ArtCraft, iPhone, câmara, impressão e programação", modules: ["office", "communication", "iphone-integration", "printing-scanning", "development"] },
        { key: "accessibility", label: "5 · ACESSIBILIDADE E ATALHOS", description: "Atalhos globais para abrir os menus APX", modules: ["shortcuts"] }
    ]
    property bool environmentKeyboardFocus: false
    property int environmentFocusIndex: -1
    property int environmentCreateFocusIndex: -1
    onEnvironmentCreateFocusIndexChanged: {
        if (environmentCreateFocusIndex === 1) revealKeyboardMenuItem(environmentNameInput.parent)
        else if (environmentCreateFocusIndex === 2) revealKeyboardMenuItem(environmentDescriptionInput.parent)
    }
    property int environmentEditFocusIndex: -1
    onEnvironmentEditFocusIndexChanged: {
        if (environmentEditFocusIndex === 1) revealKeyboardMenuItem(environmentEditTitleInput.parent)
        else if (environmentEditFocusIndex === 2) revealKeyboardMenuItem(environmentEditDescriptionInput.parent)
    }
    property bool environmentManagementBusy: false
    property bool environmentMetadataBusy: false
    property var environmentManagementState: ({ phase: "idle", progress: 0, message: "" })
    property int environmentProgressReadFailures: 0
    property bool identityReady: false
    // Identity is normally Host-authorized, but a workload can be visible
    // before its active descriptor has finished publishing.  The Host-console
    // socket is mounted only in the official Hub, so it is a safe local role
    // proof during that startup window and never grants Host authority.
    property bool sessionKindReady: false
    property bool sessionHubProof: true
    readonly property bool isHub: identityReady
                                  ? environmentIdentity.role === "hub"
                                  : sessionHubProof
    // Every graphical Environment receives the current Host-installed client
    // as a read-only /run bind. Using one path avoids a stale persistent Hub
    // bridge rejecting newly added creation fields such as --system.
    readonly property string environmentClient: "/run/apx/environment-switch-client-v1.py"
    readonly property string environmentLabel: isHub ? "Hub" : String(environmentIdentity.display_name || environmentIdentity.name || "Environment")
    readonly property int environmentPopupHeight: !isHub ? 214
        : (environmentCreateOpen ? (environmentSystemKind === "windows-native" && nativeCreationPreview.target ? 620 : 540) + (environmentManagementBusy ? 42 : 0)
           : (environmentEditOpen ? 430
           : 200 + Math.max(1, Math.min(5, environmentCatalog.length)) * 51
             + (environmentDeleteConfirm ? 88 : 0) + (environmentManagementBusy ? 42 : 0)
             + (nativeWindowsRecoveryAvailable() ? 100 : 0) + (environmentManagementState.native_v3 ? (environmentManagementState.native_v3_delete_retry ? 180 : 130) : 0)))
    // APX queued main menu switch: never reveal a new page at the old anchor.
    property var pendingPopupRequest: null
    property string popupKind: ""
    property Item popupTarget: null
    property real islandProgress: 0
    property bool popupClosing: false
    property real islandContentOpacity: 1
    readonly property string menuRoute: [popupKind, controlsBrightnessOpen, controlsConnectivityOpen, controlsWifiOpen, controlsBluetoothOpen, controlsAudioOpen, controlsMicrophoneOpen, controlsMoreOpen, controlsAppearanceOpen, controlsActivityKind, shortcutsOpen, powerConfirmOpen, calendarView, calendarEditor, environmentCreateOpen, environmentEditOpen, environmentDeleteConfirm].join(":")
    property var renderedControls: ({controlsBrightnessOpen: false, controlsConnectivityOpen: false, controlsWifiOpen: false, controlsBluetoothOpen: false, controlsAudioOpen: false, controlsMicrophoneOpen: false, controlsMoreOpen: false, controlsAppearanceOpen: false, controlsActivityKind: "", shortcutsOpen: false, powerConfirmOpen: false})
    function syncRenderedControls() {
        renderedControls = {controlsBrightnessOpen: controlsBrightnessOpen, controlsConnectivityOpen: controlsConnectivityOpen, controlsWifiOpen: controlsWifiOpen, controlsBluetoothOpen: controlsBluetoothOpen, controlsAudioOpen: controlsAudioOpen, controlsMicrophoneOpen: controlsMicrophoneOpen, controlsMoreOpen: controlsMoreOpen, controlsAppearanceOpen: controlsAppearanceOpen, controlsActivityKind: controlsActivityKind, shortcutsOpen: shortcutsOpen, powerConfirmOpen: powerConfirmOpen}
    }
    function visibleControlTiles() {
        var result = []
        function visit(item) {
            if (!item || !item.visible) return
            if (item.caption !== undefined) result.push({caption: item.caption, enabled: item.enabled, opacity: item.opacity})
            var children = item.children || []
            for (var i = 0; i < children.length; ++i) visit(children[i])
        }
        visit(menuContent)
        return result
    }
    function visibleMenuFonts() {
        var fonts = []
        function visit(item) {
            if (!item || !item.visible || item.width <= 0 || item.height <= 0) return
            if (item.font !== undefined && item.text !== undefined && String(item.text).length) {
                var key = item.font.family + ":" + item.font.pixelSize
                if (fonts.indexOf(key) < 0) fonts.push(key)
            }
            var children = item.children || []
            for (var i = 0; i < children.length; ++i) visit(children[i])
        }
        visit(menuContent)
        return fonts.sort()
    }
    function renderedControlsAllClosed() {
        return !renderedControls.controlsBrightnessOpen && !renderedControls.controlsConnectivityOpen && !renderedControls.controlsWifiOpen && !renderedControls.controlsBluetoothOpen && !renderedControls.controlsAudioOpen && !renderedControls.controlsMicrophoneOpen && !String(renderedControls.controlsActivityKind || "").length
    }
    property string controlPageRequestedRoute: ""
    property real controlPageProgress: 1
    readonly property real controlPageMotion: controlPageProgress
    readonly property real controlPageBlend: {
        var t = controlPageProgress
        return t * t * (3 - 2 * t)
    }
    property int controlPageDirection: 1
    property real controlPageOffset: 0
    property bool controlPageCapturing: false
    property bool controlPageQueued: false
    property int controlPageGeneration: 0
    property var controlPageCapture: null
    property rect outgoingPageRect: Qt.rect(0, 0, 0, 0)
    function controlDepth(state) {
        if (state.controlsAppearanceOpen || state.shortcutsOpen || state.controlsActivityKind === "trackpad") return 2
        if (state.controlsWifiOpen || state.controlsBluetoothOpen) return 2
        if (state.controlsMoreOpen || state.controlsConnectivityOpen || state.controlsBrightnessOpen || state.controlsAudioOpen || state.controlsMicrophoneOpen || state.controlsActivityKind) return 1
        return 0
    }
    function cancelControlTransition() {
        controlPageGeneration++
        controlPageRequestedRoute = ""
        controlPageAnimation.stop()
        controlPageCapturing = false
        controlPageQueued = false
        controlPageCapture = null
        controlPageProgress = 1
        controlPageOffset = 0
    }
    function startControlTransition() {
        if (controlPageRequestedRoute === menuRoute && controlPageAnimation.running) return
        cancelControlTransition()
        controlPageRequestedRoute = menuRoute
        controlPageDirection = controlDepth(root) >= controlDepth(renderedControls) ? 1 : -1
        controlPageAnimation.restart()
        popupBackground.forceActiveFocus()
        Qt.callLater(function() {
            if (!popup.open || root.popupClosing || !root.menuKeyboardNavigation) return
            var items = root.genericMenuItems()
            if (items.length) root.focusMenuItem(items[0])
        })
    }
    onMenuRouteChanged: Qt.callLater(function() {
        if (!popup.open || root.popupClosing || root.popupAnimationPending || root.islandProgress < .99) {
            root.syncRenderedControls()
            return
        }
        if (root.popupKind !== "controls") {
            root.syncRenderedControls()
            root.islandContentOpacity = 0
            islandContentAnimation.restart()
            return
        }
        islandContentAnimation.stop()
        root.islandContentOpacity = 1
        root.startControlTransition()
    })
    SequentialAnimation {
        id: controlPageAnimation
        ParallelAnimation {
            NumberAnimation { target: root; property: "controlPageProgress"; to: 0; duration: 90; easing.type: Easing.InQuad }
            NumberAnimation { target: root; property: "controlPageOffset"; to: -root.controlPageDirection * 10; duration: 90; easing.type: Easing.InQuad }
        }
        ScriptAction { script: {
            root.syncRenderedControls()
            menuFlick.contentY = 0
            root.controlPageOffset = root.controlPageDirection * 10
        } }
        ParallelAnimation {
            NumberAnimation { target: root; property: "controlPageProgress"; to: 1; duration: 190; easing.type: Easing.OutCubic }
            NumberAnimation { target: root; property: "controlPageOffset"; to: 0; duration: 190; easing.type: Easing.OutCubic }
        }
        onFinished: {
            root.controlPageCapture = null
            Qt.callLater(function() {
                if (!popup.open || root.popupClosing || root.controlPageCapturing || controlPageAnimation.running) return
                var items = root.genericMenuItems()
                if (root.menuKeyboardNavigation && items.length) root.focusMenuItem(items[0])
            })
            if (root.controlPageQueued) Qt.callLater(function() { root.startControlTransition() })
        }
    }

    property rect islandOrigin: Qt.rect(0, 8, 40, 30)
    // Opt-in frame timing; no samples or timers while disabled.
    property bool menuFrameProbeEnabled: false
    property var menuFrameSamples: []
    property bool popupAnimationPending: false
    property bool popupKeyboardRequested: false
    property bool menuKeyboardNavigation: false
    property string animatedBarOpenKind: ""
    property string animatedBarCloseKind: ""
    readonly property int popupLeftMargin: {
        if (!bar) return Appearance.desktopEdgeInset
        var left = bar.margins.left
        var right = left + bar.width - popup.menuWidth
        if (popupKind === "calendar") return left
        if (popupKind === "controls") return Math.max(left, right)
        if (!popupTarget || !bar) return left
        var targetRect = popupTarget.mapToItem(bar.contentItem, 0, 0)
        var targetCenter = left + targetRect.x + popupTarget.width / 2
        return Math.max(left, Math.min(right, Math.round(targetCenter - popup.menuWidth / 2)))
    }
    property var hostState: ({})
    property string clockText: ""
    property string volumeText: "--"
    property int volumeValue: 0
    property int volumePending: -1
    property int volumeInFlight: -1
    property int volumeLastSent: -1
    property bool volumeMuted: false
    property bool apxShortcutsEnabled: true
    property string batteryText: "--"
    readonly property string batteryIconName: {
        var percent = parseInt(batteryText)
        if (batteryStatus === "A carregar") return "battery-charging"
        if (!isFinite(percent)) return "battery"
        if (percent <= 10) return "battery-warning"
        if (percent <= 30) return "battery-low"
        if (percent <= 70) return "battery-medium"
        return "battery-full"
    }
    readonly property string appsIconName: {
        return "layout-grid"
    }
    property string batteryStatus: "Desconhecido"
    property bool batteryDischarging: false
    property real batteryWatts: -1
    property real batteryHealth: -1
    property int batteryMinutes: -1

    function applyBatteryReport(report) {
        var fields = report.trim().split("\n")
        var capacity = Number(fields[0])
        batteryText = fields[0] && isFinite(capacity) && capacity >= 0 && capacity <= 100 ? capacity + "%" : "--"
        var status = fields[1] || "Unknown"
        batteryDischarging = status === "Discharging"
        batteryStatus = status === "Charging" ? "A carregar" : status === "Discharging" ? "A utilizar bateria"
                      : status === "Full" ? "Carga completa" : status === "Not charging" ? "Ligada à corrente" : "Estado indisponível"
        var power = Number(fields[2])
        var energy = Number(fields[3])
        var full = Number(fields[4])
        var design = Number(fields[5])
        batteryWatts = fields[2] && isFinite(power) && power >= 0 ? power / 1000000 : -1
        batteryHealth = full > 0 && design > 0 ? Math.round(full / design * 100) : -1
        batteryMinutes = status === "Discharging" && energy > 0 && power > 0 ? Math.round(energy / power * 60) : -1
    }

    property Item editingMenuSlider: null
    property Item focusedMenuItem: null
    property Item pendingMenuRevealItem: null
    property real menuNavigationColumn: NaN

    component MenuSlider: Slider {
        id: keyboardSlider
        activeFocusOnTab: true
        readonly property Item navigationTarget: parent
        readonly property bool keyboardSelected: activeFocus && root.menuKeyboardNavigation
        readonly property bool keyboardEditing: root.editingMenuSlider === keyboardSlider
        property bool directArrowAdjustment: true
        signal keyboardValueChanged(real nextValue)
        onActiveFocusChanged: {
            if (!activeFocus && keyboardEditing) root.editingMenuSlider = null
        }
        Keys.priority: Keys.BeforeItem
        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                if (!event.isAutoRepeat)
                    root.editingMenuSlider = keyboardEditing ? null : keyboardSlider
                event.accepted = true
            } else if (event.key === Qt.Key_Escape && keyboardEditing) {
                root.editingMenuSlider = null
                event.accepted = true
            } else if ([Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down].indexOf(event.key) >= 0) {
                if (keyboardEditing || (directArrowAdjustment && (event.key === Qt.Key_Left || event.key === Qt.Key_Right))) {
                    var direction = event.key === Qt.Key_Up || event.key === Qt.Key_Right ? 1 : -1
                    keyboardValueChanged(Math.max(from, Math.min(to, Math.round(value) + direction * (directArrowAdjustment ? (event.modifiers & Qt.ShiftModifier ? 5 : 1) : 5))))
                    event.accepted = true
                } else root.navigateGenericMenu(event)
            } else if (event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab) {
                root.editingMenuSlider = null
                root.navigateGenericMenu(event)
            } else {
                // Prevent Slider's native Home/End/Page keys from bypassing Enter.
                event.accepted = true
            }
        }
        Rectangle {
            parent: keyboardSlider.parent
            anchors.fill: parent
            radius: parent.radius
            z: 100
            color: "transparent"
            border.width: keyboardSlider.keyboardEditing ? 2 : 1
            border.color: root.cyan
            visible: keyboardSlider.activeFocus && root.menuKeyboardNavigation
        }
    }

    function genericMenuItems() {
        var result = []
        function visit(item) {
            if (!item.visible || !item.enabled) return
            if (item.activeFocusOnTab && item.width > 0 && item.height > 0) {
                result.push(item)
                return
            }
            for (var i = 0; i < item.children.length; ++i) visit(item.children[i])
        }
        visit(menuContent)
        return result
    }

    function clearPendingMenuFocus() {
        if (focusedMenuItem && focusedMenuItem.keyboardActivationPending !== undefined)
            focusedMenuItem.keyboardActivationPending = false
        focusedMenuItem = null
    }

    function focusMenuItem(item) {
        menuFlick.stopWheel()
        if (focusedMenuItem !== item) clearPendingMenuFocus()
        focusedMenuItem = item
        item.forceActiveFocus(Qt.TabFocusReason)
        ensureMenuItemVisible(item)
        revealKeyboardMenuItem(item)
    }

    // Logical keyboard selection (Environment/Calendar) does not take Qt focus.
    // Reveal it after layout settles without moving focus out of text fields.
    function revealKeyboardMenuItem(item) {
        pendingMenuRevealItem = item
        Qt.callLater(root.flushMenuReveal)
    }

    function flushMenuReveal() {
        var item = pendingMenuRevealItem
        pendingMenuRevealItem = null
        if (item && item.visible && item.enabled && popup.open && root.menuKeyboardNavigation)
            root.ensureMenuItemVisible(item)
    }

    function ensureMenuItemVisible(item) {
        if (!item || !item.visible || menuFlick.height <= 0) return
        menuFlick.stopWheel()
        var target = item.navigationTarget || (item.menuViewportGuard !== undefined ? item.parent : item)
        var point = target.mapToItem(menuFlick.contentItem, 0, 0)
        var maximum = Math.max(0, menuFlick.contentHeight - menuFlick.height)
        var destination = menuFlick.contentY
        var topInset = menuFlick.headerInset || 0
        var availableHeight = menuFlick.height - topInset
        var margin = Math.min(8, Math.max(0, (availableHeight - target.height) / 2))
        // A tall section should reveal its beginning instead of jumping to its end.
        if (target.height > availableHeight)
            destination = point.y - topInset
        else if (point.y < destination + topInset + margin) destination = point.y - topInset - margin
        else if (point.y + target.height > destination + menuFlick.height - margin)
            destination = point.y + target.height - menuFlick.height + margin
        menuFlick.contentY = Math.max(0, Math.min(maximum, destination))
    }

    // Preserve layout and keyboard eligibility while hiding clipped actions.
    function menuViewportState() {
        var result = []
        function visit(item) {
            if (!item.visible) return
            if (item.menuViewportGuard) {
                var guard = item.menuViewportGuard
                result.push({ y: guard.surface.mapToItem(menuFlick.contentItem, 0, 0).y,
                    height: guard.surface.height, opacity: guard.surface.opacity,
                    fully_visible: guard.fullyVisible, pointer_buttons: item.acceptedButtons })
            }
            var children = item.children || []
            for (var i = 0; i < children.length; ++i) visit(children[i])
        }
        visit(menuContent)
        return result
    }

    function menuHeightForCompleteActions(limit) {
        var topPadding = popupBackground.contentInset
        var bottomPadding = popupBackground.contentBottomInset
        var viewport = Math.max(0, limit - topPadding - bottomPadding)
        var scroll = menuFlick.contentY
        var bottom = scroll + viewport
        var top = scroll + (menuFlick.headerInset || 0)
        var surfaces = []
        function visit(item) {
            if (!item.visible || item.continuousScrollContent === true) return
            var surface = item.navigationTarget
                || (item.menuViewportGuard !== undefined ? item.parent : (item.activeFocusOnTab ? item : null))
            if (surface && surface.visible && surfaces.indexOf(surface) < 0
                    && surface.height > 0 && surface.height <= viewport && surface.width > 0)
                surfaces.push(surface)
            var children = item.children || []
            for (var i = 0; i < children.length; ++i) visit(children[i])
        }
        visit(menuContent)
        var rects = surfaces.map(function(surface) {
            var point = surface.mapToItem(menuFlick.contentItem, 0, 0)
            return {x: point.x, y: point.y, width: surface.width, height: surface.height}
        })
        var partial = false
        var lastBottom = -Infinity
        for (var i = 0; i < rects.length; ++i) {
            var rect = rects[i]
            // Nested controls belong to their containing card's complete outline.
            var nested = false
            for (var j = 0; j < rects.length; ++j) {
                var outer = rects[j]
                if (i !== j && outer.x <= rect.x && outer.y <= rect.y
                        && outer.x + outer.width >= rect.x + rect.width
                        && outer.y + outer.height >= rect.y + rect.height
                        && (outer.width > rect.width || outer.height > rect.height)) { nested = true; break }
            }
            if (nested) continue
            var end = rect.y + rect.height
            if (rect.y < bottom - 0.5 && end > bottom + 0.5) partial = true
            if (rect.y >= top - 0.5 && end <= bottom + 0.5) lastBottom = Math.max(lastBottom, end)
        }
        if (!partial || !isFinite(lastBottom)) return limit
        return Math.min(limit, topPadding + lastBottom - scroll + bottomPadding)
    }

    function menuButtonFits(surface) {
        var topInset = menuFlick.headerInset || 0
        var scroll = menuFlick.contentY + topInset
        var viewport = menuFlick.height - topInset
        var layoutHeight = menuFlick.contentHeight
        var localY = surface.y
        if (!popup.open || root.islandProgress < 1 || !surface.visible
                || surface.height > viewport) return true
        var point = surface.mapToItem(menuFlick.contentItem, 0, 0)
        // Let rows pass continuously beneath the title gradient; keep the bottom-card rule.
        return point.y + surface.height <= scroll + viewport + 0.5
    }

    component MenuViewportGuard: QtObject {
        required property var surface
        required property var pointer
        readonly property bool fullyVisible: root.menuButtonFits(surface)
        property Binding opacityBinding: Binding {
            target: surface; property: "opacity"; value: 0
            when: !fullyVisible
            restoreMode: Binding.RestoreBindingOrValue
        }
        property Binding pointerBinding: Binding {
            target: pointer; property: "acceptedButtons"; value: Qt.NoButton
            when: !fullyVisible
            restoreMode: Binding.RestoreBindingOrValue
        }
    }
    Component { id: menuViewportGuardFactory; MenuViewportGuard {} }
    Timer {
        id: menuViewportGuardInstall
        interval: 0
        running: popup.open
        onTriggered: {
            function visit(item) {
                if (item.continuousScrollContent === true) return;
                if (item.menuViewportGuard !== undefined && !item.menuViewportGuard)
                    item.menuViewportGuard = menuViewportGuardFactory.createObject(item, {surface: item.navigationTarget || item.parent, pointer: item})
                var children = item.children || []
                for (var i = 0; i < children.length; ++i) visit(children[i])
            }
            visit(menuContent)
        }
    }

    function menuNavigationRect(item) {
        // Direction follows the actual control; scrolling reveals its whole card.
        var point = item.mapToItem(menuFlick.contentItem, 0, 0)
        return { x: point.x, y: point.y, width: item.width, height: item.height }
    }

    function menuEntryIndex(items, backwards) {
        var best = -1
        var bestY = backwards ? -Infinity : Infinity
        var bestX = backwards ? -Infinity : Infinity
        for (var i = 0; i < items.length; ++i) {
            var item = items[i]
            var target = item.navigationTarget || (item.menuViewportGuard !== undefined ? item.parent : item)
            var point = target.mapToItem(menuFlick.contentItem, 0, 0)
            if (point.y < menuFlick.contentY + (menuFlick.headerInset || 0) - 0.5
                    || point.y + target.height > menuFlick.contentY + menuFlick.height + 0.5) continue
            var rect = menuNavigationRect(item)
            var y = rect.y + rect.height / 2
            var x = rect.x + rect.width / 2
            if (best < 0 || (backwards ? y > bestY + 8 : y < bestY - 8)
                    || (Math.abs(y - bestY) <= 8 && (backwards ? x > bestX : x < bestX))) {
                best = i; bestY = y; bestX = x
            }
        }
        return best >= 0 ? best : (backwards ? items.length - 1 : 0)
    }

    function menuItemIntersectsViewport(item) {
        var rect = menuNavigationRect(item)
        return rect.y + rect.height > menuFlick.contentY + (menuFlick.headerInset || 0)
            && rect.y < menuFlick.contentY + menuFlick.height
    }

    function spatialMenuIndex(rects, current, key, preferredX) {
        var origin = rects[current]
        var horizontal = key === Qt.Key_Left || key === Qt.Key_Right
        var direction = key === Qt.Key_Left || key === Qt.Key_Up ? -1 : 1
        var column = !horizontal && isFinite(preferredX) ? preferredX : origin.x + origin.width / 2
        var best = current
        var bestDistance = Infinity
        var bestOffset = Infinity
        for (var i = 0; i < rects.length; ++i) {
            if (i === current) continue
            var candidate = rects[i]
            var along = horizontal
                ? candidate.x + candidate.width / 2 - origin.x - origin.width / 2
                : candidate.y + candidate.height / 2 - origin.y - origin.height / 2
            var sameRowTolerance = horizontal ? 1 : Math.min(origin.height, candidate.height) * 0.45
            if (along * direction <= sameRowTolerance) continue
            var overlap = horizontal
                ? Math.min(origin.y + origin.height, candidate.y + candidate.height) - Math.max(origin.y, candidate.y)
                : Math.min(origin.x + origin.width, candidate.x + candidate.width) - Math.max(origin.x, candidate.x)
            // Left/right stay in the current row. Up/down can reach an inset row.
            if (horizontal && overlap <= 1) continue
            var distance = Math.abs(along)
            var offset = horizontal
                ? Math.abs(candidate.y + candidate.height / 2 - origin.y - origin.height / 2)
                : Math.abs(candidate.x + candidate.width / 2 - column)
            if (distance < bestDistance - 8 || (Math.abs(distance - bestDistance) <= 8 && offset < bestOffset)) {
                best = i
                bestDistance = distance
                bestOffset = offset
            }
        }
        return best
    }

    function navigateGenericMenu(event) {
        if (controlPageAnimation.running || controlPageCapturing) { event.accepted = true; return }
        if (popupKind === "calendar" || (popupKind === "environments" && isHub)) return
        var tab = event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab
        var arrow = [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right].indexOf(event.key) >= 0
        if (!tab && !arrow) return
        if (arrow && root.controlsAppearanceOpen && personalizationPanel.colorInputActive) return
        // Text fields own cursor movement; only Tab navigates the menu.
        if (arrow && root.wifiPasswordVisible &&
                (wifiUsernameInput.activeFocus || wifiPasswordInput.activeFocus ||
                 wifiDomainInput.activeFocus || wifiCaInput.activeFocus)) return
        var items = genericMenuItems()
        if (!items.length) return
        var current = -1
        for (var i = 0; i < items.length; ++i) if (items[i].activeFocus) current = i
        if (arrow && current >= 0 && items[current].cursorPosition !== undefined
                && items[current].text !== undefined) return
        var backwards = event.key === Qt.Key_Backtab || event.key === Qt.Key_Up || event.key === Qt.Key_Left
        // Wheel scrolling can leave Qt focus on an option outside the viewport.
        if (current >= 0 && !menuItemIntersectsViewport(items[current])) current = -1
        // An opening menu has no previous row: Up must not select the last item.
        if (current < 0 && event.key === Qt.Key_Up) {
            if (menuFlick.contentY > 0) {
                menuKeyboardNavigation = true
                focusMenuItem(items[menuEntryIndex(items, false)])
            }
            event.accepted = true
            return
        }
        menuKeyboardNavigation = true
        var vertical = event.key === Qt.Key_Up || event.key === Qt.Key_Down
        if (!vertical || current < 0 || root.focusedMenuItem !== items[current]) menuNavigationColumn = NaN
        var next = menuEntryIndex(items, backwards)
        if (current >= 0) {
            if (vertical && !isFinite(menuNavigationColumn)) {
                var rect = menuNavigationRect(items[current])
                menuNavigationColumn = rect.x + rect.width / 2
            }
            next = tab ? (current + (event.key === Qt.Key_Backtab ? -1 : 1) + items.length) % items.length
                       : spatialMenuIndex(items.map(menuNavigationRect), current, event.key, menuNavigationColumn)
        }
        if (event.key === Qt.Key_Up && current >= 0 && next === current) {
            // The first action can sit below a heading: reveal the whole menu start.
            pendingMenuRevealItem = null
            menuFlick.stopWheel()
            menuFlick.contentY = 0
            event.accepted = true
            return
        }
        focusMenuItem(items[next])
        event.accepted = true
    }

    Timer {
        interval: 100
        repeat: true
        running: popup.open && root.menuKeyboardNavigation && root.popupKind !== "calendar" && (root.popupKind !== "environments" || !root.isHub)
        onTriggered: {
            if (controlPageAnimation.running || controlPageCapturing) return
            // The action temporarily disables its button; let it regain focus.
            if (root.focusedMenuItem && root.focusedMenuItem.visible && root.focusedMenuItem.keyboardActivationPending === true) return
            var items = root.genericMenuItems()
            for (var i = 0; i < items.length; ++i) if (items[i].activeFocus) return
            if (items.length) {
                var previous = items.indexOf(root.focusedMenuItem)
                root.focusMenuItem(items[previous >= 0 ? previous : 0])
            }
        }
    }
    property var hardwareProfile: ({ platform_profile: "unknown", gpu_profile: "unknown", requested_gpu_profile: "unknown", reboot_required: false })
    property bool batteryDetailsOpen: false
    property bool hardwareBusy: false
    property string platformProfileTarget: ""
    property bool hardwareConfirmOpen: false
    property bool hardwareApplied: false
    property string hardwareToken: ""
    property string hardwareTarget: ""
    property string hardwareMessage: ""
    property string hardwareStatusError: ""
    property string platformProfileError: ""
    property string gpuProfileError: ""
    property bool cameraStateKnown: false
    property bool cameraEnabled: false
    property bool cameraActive: false
    onCameraActiveChanged: {
        if (focusedFullscreen)
            showHotkeyOsd(Qt.resolvedUrl("icons/lucide/camera.svg"), "Câmara",
                          cameraActive ? "Em utilização" : "Utilização terminada", -1)
    }
    property bool microphoneActive: false
    property int microphoneVolume: 0
    property bool microphoneMuted: false
    property string microphoneText: "--"
    property int displayBrightness: 50
    property int displayBrightnessPending: -1
    property int displayBrightnessInFlight: -1
    property int displayBrightnessLastSent: -1
    property int keyboardBrightness: 0
    property int keyboardBrightnessMax: 2
    property string hardwareControlError: ""
    readonly property bool focusedFullscreen: !!(Hyprland.activeToplevel && Hyprland.activeToplevel.wayland && Hyprland.activeToplevel.wayland.fullscreen)
    onFocusedFullscreenChanged: {
        if (focusedFullscreen && cameraActive)
            showHotkeyOsd(Qt.resolvedUrl("icons/lucide/camera.svg"), "Câmara", "Em utilização", -1)
    }
    readonly property bool filesOpen: Hyprland.toplevels.values.some(function(window) {
        return /^(thunar|org\.xfce\.Thunar)$/i.test(String(window.wayland ? window.wayland.appId : window.lastIpcObject.class || ""))
    })
    readonly property bool filesFocused: !!(Hyprland.activeToplevel && /^(thunar|org\.xfce\.Thunar)$/i.test(String(Hyprland.activeToplevel.wayland ? Hyprland.activeToplevel.wayland.appId : Hyprland.activeToplevel.lastIpcObject.class || "")))
    readonly property bool fullscreenOsd: focusedFullscreen && !popup.open
    property bool hotkeyOsdVisible: false
    property real hotkeyOsdOpacity: 0
    property string hotkeyOsdIcon: ""
    property string hotkeyOsdTitle: ""
    property string hotkeyOsdDetail: ""
    property int hotkeyOsdProgress: -1
    property bool airplaneModeKnown: false
    property bool airplaneMode: false
    property bool powerConfirmOpen: false
    property bool powerBusy: false
    property bool powerTransitionActive: false
    property string powerAction: ""
    property bool idleSuspendRequested: false
    property string powerToken: ""
    property string powerMessage: ""
    property date calendarDate: new Date()
    property date currentDate: new Date()
    property string calendarView: "month"
    property var monthNames: ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    property var weekNames: ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
    property var calendarEvents: []
    property var calendarCategories: []
    property var calendarLocalEvents: []
    property var calendarSharedEvents: []
    property var calendarLocalCategories: []
    property var calendarSharedCategories: []
    property bool calendarEditor: false
    property bool calendarDetailsOpen: false
    property bool calendarRemindersOpen: false
    property string calendarPendingView: ""
    property var calendarPendingDate: null
    property int calendarMoveDirection: 1
    property real calendarPageOpacity: 1
    property real calendarPageOffset: 0
    SequentialAnimation {
        id: calendarNavigationAnimation
        ParallelAnimation {
            NumberAnimation { target: root; property: "calendarPageOpacity"; to: 0; duration: 90; easing.type: Easing.InQuad }
            NumberAnimation { target: root; property: "calendarPageOffset"; to: -root.calendarMoveDirection * 10; duration: 90; easing.type: Easing.InQuad }
        }
        ScriptAction { script: {
            if (root.calendarPendingView.length) root.calendarView = root.calendarPendingView
            root.calendarPendingView = ""
            if (root.calendarPendingDate) root.calendarDate = root.calendarPendingDate
            root.calendarPendingDate = null
            root.calendarPageOffset = root.calendarMoveDirection * 10
        } }
        ParallelAnimation {
            NumberAnimation { target: root; property: "calendarPageOpacity"; to: 1; duration: 190; easing.type: Easing.OutCubic }
            NumberAnimation { target: root; property: "calendarPageOffset"; to: 0; duration: 190; easing.type: Easing.OutCubic }
        }
    }
    property string calendarSelectedDateKey: ""
    property var calendarFocusAction: ({ kind: "", key: "" })
    property string editingEventId: ""
    property bool categoryPickerOpen: false
    property bool newCategoryOpen: false
    property string newCategoryName: ""
    property string draftTitle: ""
    property string draftDate: ""
    property string draftTime: "09:00"
    property string draftCategory: ""
    property string draftNotes: ""
    property bool draftShared: false
    property bool draftActive: true
    property var draftReminders: []
    property string draftReminderAmount: "1"
    property string draftReminderUnit: "Horas"
    property string eventError: ""
    property bool controlsConnectivityOpen: false
    property bool controlsWifiOpen: false
    property bool shortcutsOpen: false
    property bool controlsMoreOpen: false
    property bool controlsAppearanceOpen: false
    property string controlsActivityKind: ""
    Binding { target: DesktopActivity; property: "detailsVisible"; value: popup.open && root.popupKind === "media" }
    Binding { target: Appearance; property: "detailsVisible"; value: popup.open && root.popupKind === "controls" && root.controlsAppearanceOpen }
    property string ghostMessage: ""
    property bool workspacesExpanded: true
    property bool ghostGreetingVisible: false
    Timer { id: ghostGreetingTimer; interval: 3000; onTriggered: root.ghostGreetingVisible = false }
    property int trackpadSensitivity: -30
    property string trackpadSensitivityError: ""
    property int mouseSensitivity: 0
    property string mouseSensitivityError: ""
    readonly property var shortcutList: [
        { keys: "Super + R", action: "Abrir aplicações" },
        { keys: "Super + E", action: "Environments" },
        { keys: "Super + A", action: "Central de controlo" },
        { keys: "Super + B", action: "Bateria" },
        { keys: "Super + D", action: "Calendário" },
        { keys: "Super + P", action: "Ficheiros" },
        { keys: "Super + Q", action: "Terminal" },
        { keys: "Super + C", action: "Fechar janela" },
        { keys: "Super + F", action: "Ecrã inteiro" },
        { keys: "Super + V", action: "Alternar janela flutuante" },
        { keys: "Super + 1–9", action: "Ir para área de trabalho" },
        { keys: "Super + Shift + 1–9", action: "Mover janela para área de trabalho" },
        { keys: "Super + S", action: "Área especial" },
        { keys: "Super + Shift + S", action: "Mover janela para área especial" },
        { keys: "Super + Setas", action: "Mudar foco entre janelas" },
        { keys: "Super + Shift + Esquerda/Direita", action: "Mover janela" },
        { keys: "Super + J", action: "Alternar divisão da disposição" },
        { keys: "Super + M", action: "Sair da sessão" },
        { keys: "Super + roda do rato", action: "Mudar área de trabalho" },
        { keys: "Super + arrastar com botão esquerdo", action: "Mover janela" },
        { keys: "Super + arrastar com botão direito", action: "Redimensionar janela" },
        { keys: "Super + Ctrl + Home", action: "Trazer ponteiro para o portátil" },
        { keys: "Teclas de volume e multimédia", action: "Volume e reprodução" },
        { keys: "Ctrl + Shift + Esc", action: "Gestor de tarefas" }
    ]
    property bool controlsBluetoothOpen: false
    property bool controlsBrightnessOpen: false
    property bool controlsAudioOpen: false
    property bool controlsMicrophoneOpen: false
    property string wifiSelectedSsid: ""
    property string wifiPassword: ""
    property string wifiUsername: ""
    property string wifiDomain: ""
    property string wifiCaCert: "/etc/ssl/certs/ca-certificates.crt"
    property string wifiEnterpriseMethod: "PEAP"
    property string wifiMessage: ""
    property bool wifiShowPassword: false
    property bool wifiPasswordVisible: false
    property bool wifiSelectionTap: false
    property string wifiLastNetwork: ""
    property bool wifiManualOff: false
    property string wifiTogglePhase: ""
    property bool wifiOptimisticOverride: false
    property bool wifiOptimisticActive: false
    property string bluetoothMessage: ""
    property string bluetoothPowerPhase: ""
    property bool bluetoothPowerOverride: false
    property bool bluetoothPowerActive: false
    property string bluetoothDevicePendingAddress: ""
    property string bluetoothDevicePendingAction: ""
    property string bluetoothPairSessionId: ""
    property string bluetoothPairAddress: ""
    property string bluetoothPairName: ""
    property string bluetoothPairPhase: ""
    property string bluetoothPairChallenge: ""
    property string bluetoothPairPasskey: ""
    property bool bluetoothShowPin: false
    property string bluetoothPairPin: ""
    property string bluetoothPairResponsePin: ""
    property string bluetoothRemoveAddress: ""
    property string bluetoothRemoveName: ""
    // APX consistent shell v3
    readonly property int menuTitleSize: Appearance.titleSize
    readonly property int menuBodySize: Appearance.bodySize
    readonly property int menuSmallSize: Appearance.bodySize
    readonly property int menuMetaSize: Appearance.metaSize
    readonly property int environmentCreateModuleFocusBase: 9 + environmentModuleGroups.length
    readonly property int environmentCreateSubmitFocusIndex: environmentCreateModuleFocusBase + environmentModuleCatalog.length
    // Hyprland renders the display at 150%. Present the control centre at a
    // 125% physical compromise: readable on the internal panel while keeping
    // every common 16px icon aligned to an integer 20-device-pixel target.
    // Match the desktop scale exactly. Fractionally scaling the whole popup
    // forced SVG icons through an intermediate texture and softened corners.
    readonly property real controlCenterScale: 1

    function two(value) { return value < 10 ? "0" + value : "" + value }

    function dateKey(date) {
        return date.getFullYear() + "-" + two(date.getMonth() + 1) + "-" + two(date.getDate())
    }

    function eventsForDate(date) {
        var key = dateKey(date)
        return calendarEvents.filter(function(event) { return event.date === key })
    }

    function sortedEventsForDate(date) {
        var events = eventsForDate(date).slice()
        events.sort(function(a, b) {
            return (a.time || "00:00").localeCompare(b.time || "00:00")
        })
        return events
    }

    function wifiIsKnown(name) {
        return (hostState.known_networks || []).indexOf(name) >= 0
    }

    function wifiIsOpen(name) {
        return (hostState.open_networks || []).indexOf(name) >= 0
    }

    function wifiIsEnterprise(name) {
        return wifiDetails(name).security === "enterprise"
    }

    function wifiSecurityLabel(name) {
        if (wifiIsKnown(name)) return "Guardadas"
        if (wifiIsOpen(name)) return "Pública"
        if (wifiIsEnterprise(name)) return "EMPRESARIAL"
        return "Privada"
    }

    function wifiDetails(name) {
        var details = hostState.network_details || []
        for (var i = 0; i < details.length; ++i)
            if (details[i].ssid === name) return details[i]
        return ({ ssid: name, signal: 0, security: "unknown", known: false })
    }

    function wifiCurrentSignal() {
        if (!wifiDisplayActive()) return -1
        var details = hostState.network_details || []
        for (var i = 0; i < details.length; ++i) {
            var item = details[i]
            // The backend's unknown-security placeholder carries a zero,
            // not a measured signal; leave that value out of the UI.
            if (item.ssid === hostState.network_name && (item.security !== "unknown" || item.signal_source === "station")
                    && typeof item.signal === "number" && Number.isFinite(item.signal))
                return Math.max(0, Math.min(100, Math.round(item.signal)))
        }
        return -1
    }

    function wifiSignalBars(signal) {
        if (signal >= 75) return "▂▄▆█"
        if (signal >= 50) return "▂▄▆·"
        if (signal >= 25) return "▂▄··"
        return "▂···"
    }

    function wifiConnectivityLabel() {
        var state = hostState.network_connectivity || "unknown"
        if (state === "full") return "● Internet Disponível"
        if (state === "portal") return "⚠ AUTENTICAÇÃO NECESSÁRIA"
        if (state === "limited") return "△ LIGAÇÃO LIMITADA"
        if (state === "none") return "○ SEM INTERNET"
        return "◌ A VERIFICAR INTERNET"
    }

    function wifiConnectivityColor() {
        var state = hostState.network_connectivity || "unknown"
        if (state === "full") return cyan
        if (state === "portal") return "#ffd09a"
        if (state === "limited" || state === "none") return "#ff91a4"
        return textDim
    }

    function beginWifiConnect(name) {
        if (name === hostState.network_name) return
        wifiShowPassword = false
        wifiMessage = ""
        wifiSelectedSsid = name
        wifiPassword = ""
        wifiUsername = ""
        wifiDomain = ""
        wifiPasswordVisible = true
        Qt.callLater(function() {
            if (!root.wifiPasswordVisible || root.wifiSelectedSsid !== name) return
            menuFlick.stopWheel()
            menuFlick.contentY = 0
        })
        if (!wifiIsKnown(name) && !wifiIsOpen(name)) {
            Qt.callLater(function() {
                if (!root.wifiPasswordVisible || root.wifiSelectedSsid !== name) return
                if (root.wifiIsEnterprise(name)) wifiUsernameInput.forceActiveFocus()
                else wifiPasswordInput.forceActiveFocus()
            })
        }
    }

    function wifiAvailableNetworks() {
        return Array.from(new Set(hostState.available_networks || []))
            .filter(function(name) { return name !== hostState.network_name })
    }
    function completeWifiConnection() {
        hostState = Object.assign({}, hostState, {network_name: wifiSelectedSsid})
        cancelWifiPassword()
    }
    function cancelWifiPassword() {
        wifiShowPassword = false
        wifiMessage = ""
        wifiPassword = ""
        wifiUsername = ""
        wifiDomain = ""
        wifiSelectedSsid = ""
        wifiPasswordVisible = false
    }

    function submitWifiPassword() {
        if (wifiCredentialProcess.running || hostActionProcess.running) return
        if (wifiIsKnown(wifiSelectedSsid) || wifiIsOpen(wifiSelectedSsid)) {
            wifiMessage = "A ligar a " + wifiSelectedSsid + "…"
            hostAction("wifi-connect", wifiSelectedSsid)
            return
        }
        var enterprise = wifiIsEnterprise(wifiSelectedSsid)
        if (wifiCredentialProcess.running) return
        // U.Porto publishes a suffix domain; iwd requires an explicit mask.
        // Use the verified U.Porto trust anchor for the FEUP/general profile only.
        var identity = wifiUsername.trim().toLowerCase()
        if (enterprise && wifiSelectedSsid === "eduroam" &&
                (identity.endsWith("@fe.up.pt") || identity.endsWith("@up.pt")) &&
                (wifiDomain.trim() === "up.pt" || wifiDomain.trim() === "*.up.pt")) {
            wifiDomain = "*.up.pt"
            if (wifiCaCert === "/etc/ssl/certs/ca-certificates.crt")
                wifiCaCert = "/etc/ssl/certs/apx-uporto-eduroam.pem"
        }
        if (enterprise && (!wifiUsername.length || !wifiPassword.length || !wifiDomain.length)) {
            wifiMessage = "Introduz utilizador, palavra-passe e domínio do servidor."
            return
        }
        if (!enterprise && wifiPassword.length < 8) {
            wifiMessage = "A palavra-passe deve ter pelo menos 8 caracteres."
            return
        }
        wifiMessage = "A ligar a " + wifiSelectedSsid + "…"
        wifiCredentialProcess.command = ["/run/apx/host-services-client-v3.py", "wifi-connect", wifiSelectedSsid,
                                         enterprise ? "--enterprise-stdin" : "--credential-stdin"]
        wifiCredentialProcess.running = true
    }

    function toggleWifiConnection() {
        if (wifiToggleProcess.running || wifiTogglePhase.length) return
        if (hostState.network_name) {
            wifiLastNetwork = hostState.network_name
            wifiManualOff = true
            wifiTogglePhase = "disconnecting"
            wifiOptimisticOverride = true
            wifiOptimisticActive = false
            wifiToggleProcess.command = ["/run/apx/host-services-ui-v3.py", "wifi-disconnect"]
            wifiToggleProcess.running = true
            return
        }
        var target = wifiLastNetwork
        if (!target.length) {
            var nearby = hostState.available_networks || []
            for (var i = 0; i < nearby.length; ++i) {
                if (wifiIsKnown(nearby[i])) {
                    target = nearby[i]
                    break
                }
            }
        }
        if (target.length) {
            wifiManualOff = false
            wifiTogglePhase = "connecting"
            wifiOptimisticOverride = true
            wifiOptimisticActive = true
            wifiToggleProcess.command = ["/run/apx/host-services-ui-v3.py", "wifi-connect", target]
            wifiToggleProcess.running = true
        } else {
            wifiManualOff = false
            hostAction("wifi-scan")
        }
    }

    property bool wifiPowerOverride: false
    property bool wifiPowerActive: true
    function wifiDisplayPowered() { return wifiPowerOverride ? wifiPowerActive : hostState.wifi_powered !== false }
    function toggleWifiPower() {
        if (wifiPowerProcess.running) return
        cancelWifiPassword()
        wifiMessage = ""
        wifiPowerActive = !wifiDisplayPowered()
        wifiPowerOverride = true
        wifiPowerProcess.command = ["/run/apx/host-services-ui-v3.py", "wifi-power", wifiPowerActive ? "on" : "off"]
        wifiPowerProcess.running = true
    }
    function finishWifiPower(success) {
        // Retire any status request begun before this operation completed.
        // Its stale reply must not briefly undo the immediate icon feedback.
        if (hostStatusProcess.running) hostStatusProcess.running = false
        if (success) hostState = Object.assign({}, hostState, {
            wifi_powered: wifiPowerActive,
            network_name: wifiPowerActive ? hostState.network_name : null
        })
        wifiPowerOverride = false
        if (!success && !wifiMessage.length) wifiMessage = "Não foi possível alterar o Wi-Fi."
        hostStatusProcess.running = true
    }
    Process {
        id: wifiPowerProcess
        stderr: StdioCollector { onStreamFinished: if (text.trim()) root.wifiMessage = text.trim() }
        onExited: (code, status) => root.finishWifiPower(code === 0)
    }

    function wifiDisplayActive() {
        return wifiDisplayPowered() && (wifiOptimisticOverride ? wifiOptimisticActive : !!hostState.network_name)
    }

    function bluetoothDisplayPowered() {
        return bluetoothPowerOverride ? bluetoothPowerActive : hostState.bluetooth_powered === true
    }

    function toggleBluetoothPower() {
        if (bluetoothPowerProcess.running || bluetoothPowerPhase.length) return
        var next = !bluetoothDisplayPowered()
        bluetoothPowerPhase = next ? "turning-on" : "turning-off"
        bluetoothPowerOverride = true
        bluetoothPowerActive = next
        bluetoothPowerProcess.command = ["/run/apx/host-services-ui-v3.py", "bluetooth-power", next ? "on" : "off"]
        bluetoothPowerProcess.running = true
    }

    function bluetoothDeviceAction(operation, device) {
        if (bluetoothDeviceActionProcess.running || bluetoothDevicePendingAddress.length) return
        bluetoothDevicePendingAddress = device.address
        bluetoothDevicePendingAction = operation
        bluetoothDeviceActionProcess.command = ["/run/apx/host-services-ui-v3.py", operation, device.address]
        bluetoothDeviceActionProcess.running = true
    }

    function openControlSection(section) {
        controlsActivityKind = ""
        if (wifiPasswordVisible)
            cancelWifiPassword()
        var wasOpen = section === "connectivity" ? controlsConnectivityOpen
                    : section === "wifi" ? controlsWifiOpen
                    : section === "bluetooth" ? controlsBluetoothOpen
                    : section === "brightness" ? controlsBrightnessOpen
                    : section === "microphone" ? controlsMicrophoneOpen
                    : controlsAudioOpen
        controlsConnectivityOpen = section === "connectivity" ? !wasOpen : ((section === "wifi" || section === "bluetooth") && wasOpen)
        controlsWifiOpen = section === "wifi" && !wasOpen
        controlsBluetoothOpen = section === "bluetooth" && !wasOpen
        controlsBrightnessOpen = section === "brightness" && !wasOpen
        controlsAudioOpen = section === "audio" && !wasOpen
        controlsMicrophoneOpen = section === "microphone" && !wasOpen
        if (controlsWifiOpen && !wifiConnectivityProcess.running) wifiConnectivityProcess.running = true
        if (controlsAudioOpen)
            Qt.callLater(function() { if (root.menuKeyboardNavigation) volumeSlider.forceActiveFocus(); else popupBackground.forceActiveFocus() })
        else if (controlsBrightnessOpen)
            Qt.callLater(function() { if (root.menuKeyboardNavigation) displayBrightnessSlider.forceActiveFocus(); else popupBackground.forceActiveFocus() })
        else if (controlsMicrophoneOpen)
            Qt.callLater(function() { if (root.menuKeyboardNavigation) microphoneSlider.forceActiveFocus(); else popupBackground.forceActiveFocus() })
    }

    function openActivitySection(kind) {
        controlsConnectivityOpen = false; controlsWifiOpen = false; controlsBluetoothOpen = false
        controlsBrightnessOpen = false; controlsAudioOpen = false; controlsMicrophoneOpen = false
        controlsActivityKind = kind
        menuFlick.stopWheel()
        menuFlick.contentY = 0
        if (kind === "airplane") refreshAirplaneDetails()
        else if (kind === "keyboard" && !hardwareProfileProcess.running) hardwareProfileProcess.running = true
        DesktopActivity.refresh()
    }
    function openMoreOptions() { controlsMoreOpen = true; controlsAppearanceOpen = false; menuFlick.contentY = 0 }
    function runControlAction(action) {
        if (action === "lock") { closePopup(); if (!lockProcess.running) lockProcess.running = true }
        else if (action === "files-or-reboot") {
            if (isHub) beginPower("reboot")
            else { closePopup(); if (!environmentFilesProcess.running) environmentFilesProcess.running = true }
        } else if (action === "update") { closePopup(); if (!updateUiProcess.running) updateUiProcess.running = true }
        else if (action === "reboot") beginPower("reboot")
        else if (action === "poweroff") beginPower("poweroff")
        else if (action === "terminal") { closePopup(); if (!hostConsoleProcess.running) hostConsoleProcess.running = true }
        else if (action === "exit") { closePopup(); if (!hostExitProcess.running) hostExitProcess.running = true }
    }

    function controlsAllClosed() {
        return !controlsBrightnessOpen && !controlsConnectivityOpen && !controlsWifiOpen && !controlsBluetoothOpen && !controlsAudioOpen && !controlsMicrophoneOpen && !controlsActivityKind.length
    }

    function bluetoothDevicesUnique() {
        var seen = new Set()
        return (hostState.bluetooth_devices || []).filter(function(device) {
            if (!device || !device.address || seen.has(device.address)) return false
            seen.add(device.address)
            return true
        })
    }
    function bluetoothConnectedDevices() {
        if (!bluetoothDisplayPowered()) return []
        return bluetoothDevicesUnique().filter(function(device) { return device.connected === true })
    }
    function bluetoothKnownDevices() {
        if (!bluetoothDisplayPowered()) return []
        return bluetoothDevicesUnique().filter(function(device) { return device.paired === true && device.connected !== true })
    }
    function bluetoothAvailableDevices() {
        if (!bluetoothDisplayPowered()) return []
        return bluetoothDevicesUnique().filter(function(device) { return device.paired !== true && device.connected !== true })
    }
    function revealBluetoothForm() {
        Qt.callLater(function() {
            menuFlick.stopWheel()
            menuFlick.contentY = 0
            if (root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "pin")
                bluetoothPinInput.forceActiveFocus()
        })
    }
    function applyBluetoothPairResult(payload) {
        bluetoothPairSessionId = payload.session_id || bluetoothPairSessionId
        bluetoothPairPhase = payload.phase || "waiting"
        bluetoothPairChallenge = payload.challenge || ""
        bluetoothPairPasskey = payload.passkey === undefined || payload.passkey === null ? "" : String(payload.passkey)
        bluetoothMessage = payload.message || ""
        if (bluetoothPairPhase === "needs-response") revealBluetoothForm()
        if (bluetoothPairPhase === "completed") {
            bluetoothMessage = payload.message || bluetoothPairName + " emparelhado com sucesso."
            bluetoothPairPin = ""
            hostStatusProcess.running = true
        } else if (bluetoothPairPhase === "failed") {
            bluetoothMessage = payload.message || "Não foi possível emparelhar " + bluetoothPairName + "."
            bluetoothPairPin = ""
            hostStatusProcess.running = true
        }
    }

    function beginBluetoothPair(device) {
        if (bluetoothPairBeginProcess.running || bluetoothPairSessionId.length) return
        bluetoothShowPin = false
        bluetoothMessage = "A iniciar o emparelhamento…"
        bluetoothPairAddress = device.address
        bluetoothPairName = device.name || device.address
        bluetoothPairPhase = "starting"
        bluetoothPairChallenge = ""
        bluetoothPairPasskey = ""
        bluetoothPairPin = ""
        bluetoothPairBeginProcess.command = ["/run/apx/host-services-client-v3.py", "bluetooth-pair", device.address]
        bluetoothPairBeginProcess.running = true
        revealBluetoothForm()
    }

    function respondBluetoothPair(accepted, pin) {
        if (!bluetoothPairSessionId.length || bluetoothPairRespondProcess.running) return
        bluetoothPairResponsePin = pin || ""
        var args = ["/run/apx/host-services-client-v3.py", "bluetooth-pair-respond", bluetoothPairSessionId,
                    "--accept", accepted ? "yes" : "no"]
        if (bluetoothPairResponsePin.length) args.push("--credential-stdin")
        bluetoothPairRespondProcess.command = args
        bluetoothPairRespondProcess.running = true
        bluetoothMessage = accepted ? "A confirmar…" : "A cancelar…"
    }

    function cancelBluetoothPairing() {
        bluetoothShowPin = false
        if (bluetoothPairPhase === "needs-response") {
            respondBluetoothPair(false, "")
            return
        }
        bluetoothPairSessionId = ""
        bluetoothPairAddress = ""
        bluetoothPairName = ""
        bluetoothPairPhase = ""
        bluetoothPairChallenge = ""
        bluetoothPairPasskey = ""
        bluetoothPairPin = ""
        bluetoothMessage = "Emparelhamento cancelado."
    }

    function dismissBluetoothPairing() {
        bluetoothShowPin = false
        bluetoothPairSessionId = ""
        bluetoothPairAddress = ""
        bluetoothPairName = ""
        bluetoothPairPhase = ""
        bluetoothPairChallenge = ""
        bluetoothPairPasskey = ""
        bluetoothPairPin = ""
    }

    function beginBluetoothRemove(device) {
        bluetoothRemoveAddress = device.address
        bluetoothRemoveName = device.name || device.address
        bluetoothMessage = ""
        revealBluetoothForm()
    }

    function confirmBluetoothRemove() {
        if (!bluetoothRemoveAddress.length || bluetoothRemoveProcess.running) return
        bluetoothRemoveProcess.command = ["/run/apx/host-services-client-v3.py", "bluetooth-remove", bluetoothRemoveAddress]
        bluetoothRemoveProcess.running = true
    }

    function beginEvent() {
        editingEventId = ""
        draftTitle = ""
        draftDate = dateKey(calendarDate)
        draftTime = "09:00"
        draftCategory = calendarCategories.length ? calendarCategories[0] : ""
        draftNotes = ""
        draftShared = false
        draftActive = true
        draftReminders = []
        draftReminderAmount = "1"
        draftReminderUnit = "Horas"
        eventError = ""
        categoryPickerOpen = false
        newCategoryOpen = false
        calendarDetailsOpen = false
        calendarRemindersOpen = false
        calendarEditor = true
        menuFlick.contentY = 0
        Qt.callLater(function() { calendarTitleField.focusInput() })
    }

    function beginEditEvent(event) {
        editingEventId = event.id
        draftTitle = event.title || ""
        draftDate = event.date || dateKey(new Date())
        draftTime = event.time || "09:00"
        draftCategory = event.category || ""
        draftNotes = event.notes || ""
        draftShared = event.scope === "shared"
        draftActive = event.active !== false
        draftReminders = (event.reminders || []).slice()
        setReminderDraft(draftReminders.length ? draftReminders[0] : 60)
        eventError = ""
        categoryPickerOpen = false
        newCategoryOpen = false
        calendarDetailsOpen = false
        calendarRemindersOpen = false
        calendarEditor = true
        menuFlick.contentY = 0
        Qt.callLater(function() { calendarTitleField.focusInput() })
    }

    function createCategory() {
        var name = newCategoryName.trim().toUpperCase()
        if (!name) return
        if (calendarCategories.indexOf(name) < 0)
            calendarCategories = calendarCategories.concat([name]).sort()
        draftCategory = name
        newCategoryName = ""
        newCategoryOpen = false
        categoryPickerOpen = false
        persistEvents()
    }

    function toggleReminder(minutes) {
        var reminders = draftReminders.slice()
        var index = reminders.indexOf(minutes)
        if (index >= 0) reminders.splice(index, 1)
        else reminders.push(minutes)
        draftReminders = reminders
    }

    function reminderMultiplier(unit) {
        if (unit === "Semanas") return 10080
        if (unit === "Dias") return 1440
        if (unit === "Horas") return 60
        return 1
    }

    function setReminderDraft(minutes) {
        if (minutes % 10080 === 0) {
            draftReminderAmount = "" + (minutes / 10080)
            draftReminderUnit = "Semanas"
        } else if (minutes % 1440 === 0) {
            draftReminderAmount = "" + (minutes / 1440)
            draftReminderUnit = "Dias"
        } else if (minutes % 60 === 0) {
            draftReminderAmount = "" + (minutes / 60)
            draftReminderUnit = "Horas"
        } else {
            draftReminderAmount = "" + minutes
            draftReminderUnit = "Minutos"
        }
    }

    function addDraftReminder() {
        var amount = parseInt(draftReminderAmount)
        if (!/^\d+$/.test(draftReminderAmount) || amount < 1) {
            eventError = "O lembrete deve ser um número inteiro positivo."
            return
        }
        var minutes = amount * reminderMultiplier(draftReminderUnit)
        if (draftReminders.indexOf(minutes) < 0) {
            var reminders = draftReminders.concat([minutes])
            reminders.sort(function(a, b) { return a - b })
            draftReminders = reminders
        }
        eventError = ""
    }

    function removeDraftReminder(minutes) {
        draftReminders = draftReminders.filter(function(value) { return value !== minutes })
    }

    function reminderLabel(minutes) {
        if (minutes % 10080 === 0) return (minutes / 10080) + " semana" + (minutes / 10080 === 1 ? "" : "s")
        if (minutes % 1440 === 0) return (minutes / 1440) + " dia" + (minutes / 1440 === 1 ? "" : "s")
        if (minutes % 60 === 0) return (minutes / 60) + " hora" + (minutes / 60 === 1 ? "" : "s")
        return minutes + " minuto" + (minutes === 1 ? "" : "s")
    }

    function persistEvents() {
        var local = calendarEvents.filter(function(event) { return event.scope !== "shared" })
        var shared = calendarEvents.filter(function(event) { return event.scope === "shared" })
        var localCategories = []
        local.forEach(function(event) { if (localCategories.indexOf(event.category) < 0) localCategories.push(event.category) })
        var sharedCategories = []
        shared.forEach(function(event) { if (sharedCategories.indexOf(event.category) < 0) sharedCategories.push(event.category) })
        if (!calendarSaveProcess.running) {
            calendarSaveProcess.command = ["/usr/bin/python3", "/home/apx/.config/quickshell/apx/calendar_store.py", "save",
                                           JSON.stringify({ events: local, categories: localCategories })]
            calendarSaveProcess.running = true
        }
        if (!calendarSharedSaveProcess.running) {
            calendarSharedSaveProcess.command = ["/run/apx/host-services-client-v3.py", "calendar-save",
                                                  JSON.stringify({ events: shared, categories: sharedCategories })]
            calendarSharedSaveProcess.running = true
        }
    }

    function saveDraftEvent() {
        if (!draftTitle.trim()) { eventError = "Indica um título."; return }
        if (!draftCategory.trim()) { eventError = "Escolhe ou cria uma categoria."; return }
        if (!/^\d{4}-\d{2}-\d{2}$/.test(draftDate)) { eventError = "Data inválida: usa AAAA-MM-DD."; return }
        if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(draftTime)) { eventError = "Hora inválida: usa HH:MM."; return }
        var parts = draftDate.split("-")
        var testDate = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
        if (dateKey(testDate) !== draftDate) { eventError = "Essa data não existe."; return }
        var event = {
            id: editingEventId || Date.now().toString(),
            title: draftTitle.trim(),
            date: draftDate,
            time: draftTime,
            category: draftCategory.trim(),
            notes: draftNotes.trim(),
            scope: draftShared ? "shared" : "environment",
            active: draftActive,
            reminders: draftReminders.slice()
        }
        if (editingEventId) {
            calendarEvents = calendarEvents.map(function(existing) {
                return existing.id === editingEventId ? event : existing
            })
        } else {
            calendarEvents = calendarEvents.concat([event])
        }
        if (calendarCategories.indexOf(event.category) < 0)
            calendarCategories = calendarCategories.concat([event.category]).sort()
        calendarDate = testDate
        editingEventId = ""
        calendarEditor = false
        persistEvents()
        focusCalendarMenuAfterOpen()
    }

    function toggleEvent(id) {
        var updated = calendarEvents.map(function(event) {
            if (event.id !== id) return event
            var copy = Object.assign({}, event)
            copy.active = !event.active
            return copy
        })
        calendarEvents = updated
        persistEvents()
    }

    function deleteEvent(id) {
        calendarEvents = calendarEvents.filter(function(event) { return event.id !== id })
        persistEvents()
    }

    function sameDay(a, b) {
        return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
    }

    function monthDays() {
        var year = calendarDate.getFullYear()
        var month = calendarDate.getMonth()
        var first = new Date(year, month, 1)
        var mondayOffset = (first.getDay() + 6) % 7
        var days = new Date(year, month + 1, 0).getDate()
        var cells = []
        for (var i = 0; i < mondayOffset; ++i) cells.push(null)
        for (var day = 1; day <= days; ++day) cells.push(new Date(year, month, day))
        while (cells.length % 7 !== 0) cells.push(null)
        return cells
    }

    function weekDays() {
        var base = new Date(calendarDate.getFullYear(), calendarDate.getMonth(), calendarDate.getDate())
        var offset = (base.getDay() + 6) % 7
        var monday = new Date(base.getFullYear(), base.getMonth(), base.getDate() - offset)
        var days = []
        for (var i = 0; i < 7; ++i) days.push(new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() + i))
        return days
    }

    function changeCalendarView(view, date) {
        var previous = calendarPendingView || calendarView
        if (view === previous && !date) return
        calendarNavigationAnimation.stop()
        var order = ["day", "month", "year"]
        calendarMoveDirection = order.indexOf(view) >= order.indexOf(previous) ? 1 : -1
        calendarPendingView = view
        if (date) calendarPendingDate = date
        calendarNavigationAnimation.restart()
    }

    function moveCalendar(direction) {
        var d = calendarPendingDate || calendarDate
        calendarNavigationAnimation.stop()
        calendarMoveDirection = direction
        if ((calendarPendingView || calendarView) === "day")
            calendarPendingDate = new Date(d.getFullYear(), d.getMonth(), d.getDate() + direction)
        else if ((calendarPendingView || calendarView) === "year")
            calendarPendingDate = new Date(d.getFullYear() + direction, d.getMonth(), 1)
        else
            calendarPendingDate = new Date(d.getFullYear(), d.getMonth() + direction, 1)
        calendarNavigationAnimation.restart()
    }

    function calendarTitle() {
        if (calendarView === "year") return "" + calendarDate.getFullYear()
        if (calendarView === "day")
            return two(calendarDate.getDate()) + " " + monthNames[calendarDate.getMonth()] + " " + calendarDate.getFullYear()
        return monthNames[calendarDate.getMonth()] + " " + calendarDate.getFullYear()
    }

    function calendarKeyboardGroups() {
        var groups = [
            [{ kind: "previous", key: "previous" },
             { kind: "next", key: "next" }],
            [{ kind: "view", key: "day" },
             { kind: "view", key: "month" },
             { kind: "view", key: "year" }]
        ]
        var i
        if (calendarView === "month") {
            var days = monthDays()
            var dateActions = []
            for (i = 0; i < days.length; ++i)
                if (days[i] !== null)
                    dateActions.push({ kind: "date", key: dateKey(days[i]) })
            groups.push(dateActions)
        } else if (calendarView === "year") {
            var monthActions = []
            for (i = 0; i < monthNames.length; ++i)
                monthActions.push({ kind: "month", key: "" + i })
            groups.push(monthActions)
        } else {
            var timelineEvents = sortedEventsForDate(calendarDate)
            for (i = 0; i < timelineEvents.length; ++i)
                groups.push([{ kind: "edit", key: timelineEvents[i].id },
                             { kind: "delete", key: timelineEvents[i].id }])
        }
        groups.push([{ kind: "today", key: "today" },
                     { kind: "new", key: "new" }])
        if (calendarView !== "day") {
            var selectedEvents = eventsForDate(calendarDate)
            for (i = 0; i < selectedEvents.length; ++i)
                groups.push([{ kind: "edit", key: selectedEvents[i].id },
                             { kind: "delete", key: selectedEvents[i].id }])
        }
        return groups
    }

    function calendarKeyboardActions() {
        var actions = []
        var groups = calendarKeyboardGroups()
        for (var group = 0; group < groups.length; ++group)
            for (var item = 0; item < groups[group].length; ++item)
                actions.push(groups[group][item])
        return actions
    }

    function calendarActionIsFocused(kind, key) {
        return menuKeyboardNavigation && calendarFocusAction.kind === kind
                && calendarFocusAction.key === String(key)
    }

    function moveCalendarKeyboardFocus(step) {
        var actions = calendarKeyboardActions()
        if (!actions.length) return
        var current = -1
        for (var i = 0; i < actions.length; ++i) {
            if (calendarActionIsFocused(actions[i].kind, actions[i].key)) {
                current = i
                break
            }
        }
        var next = current < 0 ? (step < 0 ? actions.length - 1 : 0)
                               : (current + step + actions.length) % actions.length
        calendarFocusAction = actions[next]
    }

    function calendarKeyboardPosition(groups) {
        for (var group = 0; group < groups.length; ++group)
            for (var item = 0; item < groups[group].length; ++item)
                if (calendarActionIsFocused(groups[group][item].kind,
                                            groups[group][item].key))
                    return ({ group: group, item: item })
        return ({ group: -1, item: -1 })
    }

    function setCalendarKeyboardAction(action) {
        if (!action) return
        calendarFocusAction = action
    }

    function selectCalendarDate(date) {
        calendarDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
        calendarSelectedDateKey = dateKey(calendarDate)
    }

    function calendarDefaultGroupAction(group, preferredItem) {
        if (!group || !group.length) return null
        var currentDateKey = dateKey(calendarDate)
        for (var i = 0; i < group.length; ++i) {
            if (group[i].kind === "date" && group[i].key === currentDateKey)
                return group[i]
            if (group[i].kind === "view" && group[i].key === calendarView)
                return group[i]
            if (group[i].kind === "month"
                    && Number(group[i].key) === calendarDate.getMonth())
                return group[i]
            if (group[i].kind === "today") return group[i]
        }
        return group[Math.max(0, Math.min(group.length - 1, preferredItem))]
    }

    function moveCalendarHorizontal(step) {
        var groups = calendarKeyboardGroups()
        var position = calendarKeyboardPosition(groups)
        if (position.group < 0) {
            setCalendarKeyboardAction({ kind: "date", key: dateKey(calendarDate) })
            return
        }
        var group = groups[position.group]
        var next = position.item + step
        // Horizontal arrows stay inside the current row/subtopic. Calendar
        // dates and months do not wrap into another row or control group.
        if (group[position.item].kind === "date"
                || group[position.item].kind === "month") {
            if (next < 0 || next >= group.length) return
        } else {
            next = (next + group.length) % group.length
        }
        setCalendarKeyboardAction(group[next])
    }

    function moveCalendarVertical(step) {
        var groups = calendarKeyboardGroups()
        var position = calendarKeyboardPosition(groups)
        if (position.group < 0) {
            setCalendarKeyboardAction({ kind: "date", key: dateKey(calendarDate) })
            return
        }
        var action = groups[position.group][position.item]
        var stride = action.kind === "date" ? 7 : (action.kind === "month" ? 3 : 0)
        if (stride > 0) {
            var nextItem = position.item + step * stride
            if (nextItem >= 0 && nextItem < groups[position.group].length) {
                setCalendarKeyboardAction(groups[position.group][nextItem])
                return
            }
        }
        var nextGroup = position.group + step
        if (nextGroup < 0 || nextGroup >= groups.length) return
        setCalendarKeyboardAction(calendarDefaultGroupAction(groups[nextGroup],
                                                             position.item))
    }

    function calendarEventById(id) {
        for (var i = 0; i < calendarEvents.length; ++i)
            if (calendarEvents[i].id === id) return calendarEvents[i]
        return null
    }

    function activateCalendarKeyboardFocus() {
        var action = calendarFocusAction
        if (!action.kind) {
            moveCalendarKeyboardFocus(1)
            return
        }
        if (action.kind === "previous") moveCalendar(-1)
        else if (action.kind === "next") moveCalendar(1)
        else if (action.kind === "view") changeCalendarView(action.key)
        else if (action.kind === "date") {
            var parts = action.key.split("-")
            selectCalendarDate(new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])))
        } else if (action.kind === "month") {
            changeCalendarView("month", new Date(calendarDate.getFullYear(), Number(action.key), 1))
        } else if (action.kind === "today") {
            selectCalendarDate(currentDate)
        } else if (action.kind === "new") beginEvent()
        else if (action.kind === "edit") {
            var event = calendarEventById(action.key)
            if (event) beginEditEvent(event)
        } else if (action.kind === "delete") deleteEvent(action.key)
    }

    function handleCalendarKey(event) {
        if (event.key !== Qt.Key_Escape) menuKeyboardNavigation = true
        if (event.key === Qt.Key_Left) {
            moveCalendarHorizontal(-1)
            event.accepted = true
        } else if (event.key === Qt.Key_Right) {
            moveCalendarHorizontal(1)
            event.accepted = true
        } else if (event.key === Qt.Key_Up) {
            moveCalendarVertical(-1)
            event.accepted = true
        } else if (event.key === Qt.Key_Down) {
            moveCalendarVertical(1)
            event.accepted = true
        } else if (event.key === Qt.Key_Backtab) {
            moveCalendarKeyboardFocus(-1)
            event.accepted = true
        } else if (event.key === Qt.Key_Tab) {
            moveCalendarKeyboardFocus(1)
            event.accepted = true
        } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter
                   || event.key === Qt.Key_Space) {
            activateCalendarKeyboardFocus()
            event.accepted = true
        } else if (event.key === Qt.Key_PageUp || event.key === Qt.Key_PageDown) {
            moveCalendar(event.key === Qt.Key_PageUp ? -1 : 1)
            event.accepted = true
        } else if (event.key === Qt.Key_Home) {
            calendarDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate())
            calendarView = "month"
            calendarFocusAction = ({ kind: "date", key: dateKey(calendarDate) })
            event.accepted = true
        }
    }

    function focusCalendarMenuAfterOpen(selectToday) {
        Qt.callLater(function() {
            if (root.popupKind !== "calendar" || !popup.open || root.calendarEditor) return
            if (selectToday === true) {
                root.calendarDate = new Date(root.currentDate.getFullYear(),
                                             root.currentDate.getMonth(),
                                             root.currentDate.getDate())
                root.calendarView = "month"
            }
            root.calendarFocusAction = ({ kind: "date",
                                          key: root.dateKey(root.calendarDate) })
            calendarMenu.forceActiveFocus()
        })
    }

    function cancelCalendarEditor() {
        calendarEditor = false
        focusCalendarMenuAfterOpen()
    }

    function closePopup() {
        ghostGreetingTimer.stop()
        ghostGreetingVisible = false
        if (!popup.open || popupClosing) return
        if (popupKind === "media" && mediaButton)
            mediaButton.beginHoverHandoff(popupBarPointer.containsMouse && popupBarPointer.hoveredBarTarget === mediaButton)
        popupClosing = true
        cancelControlTransition()
        popupAnimationPending = false
        popupKeyboardRequested = false
        popupOpenAnimation.stop()
        popupCloseAnimation.restart()
    }

    function finishClosePopup() {
        ghostGreetingTimer.stop()
        ghostGreetingVisible = false
        var pending = pendingPopupRequest
        pendingPopupRequest = null
        shortcutsOpen = false
        controlsMoreOpen = false
        controlsAppearanceOpen = false
        controlsActivityKind = ""
        clearPendingMenuFocus()
        editingMenuSlider = null
        popupKeyboardRequested = false
        animatedBarOpenKind = ""
        animatedBarCloseKind = ""
        popupOpenAnimation.stop()
        popup.open = false
        popupClosing = false
        popupAnimationPending = false
        popupKind = ""
        controlsConnectivityOpen = false; controlsWifiOpen = false
        controlsBluetoothOpen = false
        controlsBrightnessOpen = false; controlsAudioOpen = false
        controlsMicrophoneOpen = false
        cancelWifiPassword()
        environmentCreateOpen = false
        environmentEditOpen = false
        environmentDeleteConfirm = false
        environmentKeyboardFocus = false
        calendarFocusAction = ({ kind: "", key: "" })
        if (pending && pending.target) {
            root.togglePopup(pending.kind, pending.target, pending.keyboardRequested)
            if (pending.controlSection === "more") root.openMoreOptions()
            else if (pending.controlSection === "shortcuts") root.shortcutsOpen = true
            else if (pending.controlSection && pending.controlSection.length) root.openControlSection(pending.controlSection)
            root.syncRenderedControls()
        }
    }

    function refreshGhostGreeting() {
        var hour = new Date().getHours()
        ghostMessage = (hour >= 6 && hour < 12 ? "Bom dia" : hour >= 12 && hour < 19 ? "Boa tarde" : "Boa noite") + ", André!"
        ghostGreetingVisible = true
        ghostGreetingTimer.restart()
    }

    function showPopup() {
        cancelControlTransition()
        syncRenderedControls()
        if (root.popupKind === "controls") root.refreshGhostGreeting()
        if (environmentAppsProcess.running) environmentAppsProcess.running = false
        popupOpenAnimation.stop()
        popupAnimationPending = false
        root.flushEnvironmentCatalog()
        popupCloseAnimation.stop()
        popupClosing = false
        if (!popup.open) {
            islandProgress = 0
            if (popupTarget && bar) {
                var point = popupTarget.mapToItem(bar.contentItem, 0, 0)
                islandOrigin = Qt.rect(point.x + bar.margins.left, point.y + bar.margins.top,
                                       popupTarget.width, popupTarget.height)
            }
        }
        islandContentOpacity = 0
        islandContentAnimation.restart()
        menuKeyboardNavigation = false
        menuNavigationColumn = NaN
        pendingMenuRevealItem = null
        environmentKeyboardFocus = false
        popup.open = true
        root.refreshDynamicStatus()
        popupAnimationPending = true
        // Set focus after the card is visible, including on the first opening.
        Qt.callLater(function() {
            if (!popup.open) return
            if (root.popupKind === "calendar") calendarMenu.forceActiveFocus()
            else if (root.popupKind === "environments" && root.isHub) environmentMenu.forceActiveFocus()
            else popupBackground.forceActiveFocus()
        })
    }

    function toggleApplicationLauncher() {
        if (isHub) return
        if (popup.open) closePopup()
        environmentAppsProcess.running = !environmentAppsProcess.running
    }

    function barTargetRect(button) {
        if (!button || !bar) return null
        var point = button.mapToItem(bar.contentItem, 0, 0)
        return {x: point.x + bar.margins.left, y: point.y + bar.margins.top, width: button.width, height: button.height}
    }

    function popupBarTargetAt(x, y) {
        if (!bar || popup.screen !== bar.screen || y < 0 || y >= bar.implicitHeight) return null
        var buttons = [calendarButton, environmentButton, mediaButton, appsButton, filesButton, batteryButton, controlCenterButton]
        for (var i = 0; i < buttons.length; ++i) {
            var button = buttons[i]
            if (!button.visible || !button.enabled) continue
            var point = button.mapToItem(bar.contentItem, 0, 0)
            var left = point.x + bar.margins.left
            if (x >= left && x < left + button.width && y >= point.y && y < point.y + button.height)
                return button
        }
        return null
    }

    function queueControlPage(section) {
        if (!popup.open || root.popupKind === "controls") return false
        root.toggleFocusedPopup("controls")
        if (pendingPopupRequest) pendingPopupRequest.controlSection = section
        return true
    }

    function toggleFocusedPopup(kind) {
        var monitor = Hyprland.focusedMonitor
        if (monitor) {
            for (var i = 0; i < barVariants.instances.length; ++i) {
                var candidate = barVariants.instances[i]
                if (candidate.screen.name === monitor.name && candidate !== root.bar) {
                    root.closePopup()
                    root.selectedBar = candidate
                    break
                }
            }
        }
        var buttons = ({ calendar: calendarButton, environments: environmentButton, applications: appsButton,
                         controls: controlCenterButton, media: mediaButton, battery: batteryButton })
        root.togglePopup(kind, buttons[kind], true)
    }

    function togglePopup(kind, target, keyboardRequested) {
        if (!target) return
        if (popup.open && root.popupKind !== kind) {
            pendingPopupRequest = {kind: kind, target: target, keyboardRequested: keyboardRequested === true}
            root.closePopup()
            return
        }
        pendingPopupRequest = null
        if (environmentAppsProcess.running) environmentAppsProcess.running = false
        var targetBar = target.QsWindow.window
        if (targetBar && targetBar !== root.bar) {
            root.closePopup()
            root.selectedBar = targetBar
        }
        if (popupKind === kind && popup.open) {
            if (popupClosing) return
            popupKeyboardRequested = false
            animatedBarOpenKind = ""
            animatedBarCloseKind = kind
            barAnimationReset.restart()
            root.closePopup()
            return
        }
        animatedBarCloseKind = ""
        animatedBarOpenKind = kind
        popupKeyboardRequested = keyboardRequested === true
        barAnimationReset.restart()
        popupOpenAnimation.stop()
        if (kind === "controls") {
            shortcutsOpen = false
            controlsMoreOpen = false
            controlsAppearanceOpen = false
            controlsActivityKind = ""
            controlsConnectivityOpen = false; controlsWifiOpen = false
            controlsBluetoothOpen = false
            controlsBrightnessOpen = false; controlsAudioOpen = false
            controlsMicrophoneOpen = false
            cancelWifiPassword()
        }
        clearPendingMenuFocus()
        editingMenuSlider = null
        menuFlick.contentY = 0
        popupKind = kind
        popupTarget = target
        showPopup()
        if (kind === "controls")
            hostAction("wifi-scan")
        if (kind === "battery") {
            batteryDetailsOpen = hardwareConfirmOpen || hardwareProfile.reboot_required === true
            loadHardwareProfile()
        }
        if (kind === "environments" && root.isHub) {
            root.environmentCreateOpen = false
            root.environmentEditOpen = false
            root.environmentDeleteConfirm = false
            root.selectedEnvironmentName = ""
            root.selectedEnvironmentGeneration = ""
            root.environmentFocusIndex = -1
            environmentMenuRefreshTimer.restart()
            focusEnvironmentMenuAfterOpen()
        }
        if (kind === "calendar")
            focusCalendarMenuAfterOpen(true)
        else if (kind !== "environments")
            Qt.callLater(function() {
                var items = root.genericMenuItems()
                if (popup.open) popupBackground.forceActiveFocus()
            })
    }

    // Read-only prefetch; lifecycle operations still validate current Host state.
    function refreshEnvironmentMenu() {
        if (!root.isHub) return
        if (!environmentCatalogProcess.running) environmentCatalogProcess.running = true
        if (!environmentStorageProcess.running) environmentStorageProcess.running = true
        if (!environmentManagementStatusProcess.running) environmentManagementStatusProcess.running = true
    }

    function applyEnvironmentCatalog(items) {
        if (JSON.stringify(items) === JSON.stringify(root.environmentCatalog)) return
        root.environmentCatalog = items
        if (!root.environmentSelection()) {
            root.selectedEnvironmentName = ""
            root.selectedEnvironmentGeneration = ""
        }
        root.resetEnvironmentFocus()
    }

    function flushEnvironmentCatalog() {
        if (root.pendingEnvironmentCatalog === null) return
        var items = root.pendingEnvironmentCatalog
        root.pendingEnvironmentCatalog = null
        root.applyEnvironmentCatalog(items)
    }

    function focusEnvironmentMenuAfterOpen() {
        Qt.callLater(function() {
            if (root.popupKind !== "environments" || !popup.open) return
            root.environmentKeyboardFocus = false
            root.environmentFocusIndex = -1
            environmentMenu.forceActiveFocus()
        })
    }

    function environmentSelection() {
        for (var i = 0; i < environmentCatalog.length; ++i)
            if (environmentCatalog[i].name === selectedEnvironmentName) return environmentCatalog[i]
        return null
    }

    function environmentCategoryLabel(category) {
        var labels = {
            "development": "Desenvolvimento",
            "games": "Jogos e lazer",
            "private": "Privado",
            "study": "Estudo",
            "university": "Universidade",
            "work": "Trabalho",
            "general": "Uso geral"
        }
        return labels[String(category || "general")] || "Environment APX"
    }

    function environmentMeta(item) {
        if (!item || item.state === "empty") return "Cria o primeiro espaço para começar"
        return String(item.description || "Sem descrição")
    }

    function environmentStorageLabel(bytes, decimals) {
        var value = Number(bytes || 0) / 1073741824
        if (!(value > 0)) return ""
        var rounded = decimals ? Math.round(value * 10) / 10 : Math.round(value)
        return String(rounded).replace(".", ",") + " GiB"
    }

    function environmentSizeLabel(item) {
        if (!item) return ""
        if (environmentIsNative(item)) {
            var reserved = Number(item.reserved_bytes || 0)
            return reserved > 0 ? environmentStorageLabel(reserved, reserved < 10 * 1073741824) : "Indisponível"
        }
        if (!environmentStorageState.sizes) return ""
        var bytes = Number(environmentStorageState.sizes[item.name] || 0)
        return bytes > 0 ? environmentStorageLabel(bytes, bytes < 10 * 1073741824) : "Indisponível"
    }

    function environmentStorageSummary() {
        var available = Number(environmentStorageState.available_bytes || 0)
        var total = Number(environmentStorageState.total_bytes || 0)
        return total > 0 ? "LIVRE " + environmentStorageLabel(available, false)
                         + " / " + environmentStorageLabel(total, false) : "A MEDIR…"
    }

    function nativeWindowsExists() {
        for (var index = 0; index < environmentCatalog.length; ++index)
            if (environmentIsNative(environmentCatalog[index])) return true
        return false
    }

    function nativeWindowsRecoveryAvailable() {
        return environmentManagementState.native_recovery === true
            && String(environmentManagementState.pending_generation || "").length === 36
    }

    function recoverNativeWindows(action) {
        if (!nativeWindowsRecoveryAvailable() || environmentActionProcess.running) return
        var mode = action === "discard" ? "native-discard" : "native-retry"
        environmentSwitchError = ""
        nativeRecoveryDiscardConfirm = false
        environmentManagementBusy = true
        environmentActionProcess.command = [root.environmentClient, mode,
                                            "--target", "windows",
                                            "--generation", String(environmentManagementState.pending_generation)]
        environmentActionProcess.running = true
    }

    function nativeV3Action(action) {
        if (environmentActionProcess.running || !environmentManagementState.native_v3) return
        var generation = String(environmentManagementState.pending_generation || "")
        var confirmation = action + ":" + generation
        if (nativeV3Confirmation !== confirmation) { nativeV3Confirmation = confirmation; return }
        environmentSwitchError = ""
        environmentActionProcess.command = [root.environmentClient, "native-" + action + "-v3",
            "--target", String(environmentManagementState.pending_target), "--generation", generation]
        environmentActionProcess.running = true
        nativeV3Confirmation = ""
    }

    function environmentIsOpenable(item) {
        return !!item && (item.state === "stopped" || item.state === "ready")
    }

    function environmentIsNative(item) {
        return !!item && item.environment_kind === "native-boot"
    }

    function selectEnvironment(item) {
        if (!environmentIsOpenable(item) || environmentManagementBusy || environmentMetadataBusy) return
        selectedEnvironmentName = item.name
        selectedEnvironmentGeneration = item.generation
        environmentDeleteConfirm = false
    }

    function resetEnvironmentFocus() {
        var selectedIndex = -1
        for (var i = 0; i < environmentCatalog.length; ++i)
            if (environmentCatalog[i].name === selectedEnvironmentName) selectedIndex = i
        if (selectedIndex >= 0) environmentFocusIndex = selectedIndex
        else if (environmentFocusIndex > environmentCatalog.length + 2) environmentFocusIndex = -1
    }

    function moveEnvironmentFocus(direction) {
        if (environmentManagementBusy || environmentMetadataBusy) return
        var rows = environmentCatalog.length
        // The current Environment card is informational only.
        var indices = []
        for (var index = 0; index < rows; ++index)
            if (environmentIsOpenable(environmentCatalog[index])) indices.push(index)
        indices.push(rows)
        if (selectedEnvironmentName.length) {
            indices.push(rows + 1)
            indices.push(rows + 2)
        }
        var position = indices.indexOf(environmentFocusIndex)
        if (position < 0) environmentFocusIndex = indices[direction < 0 ? indices.length - 1 : 0]
        else environmentFocusIndex = indices[Math.max(0, Math.min(indices.length - 1, position + direction))]
        if (position === 0 && direction < 0) {
            // The title/current Environment are above the first actionable row.
            menuFlick.stopWheel()
            pendingMenuRevealItem = null
            menuFlick.contentY = 0
        }
        environmentDeleteConfirm = false
        environmentEditOpen = false
    }

    function moveEnvironmentActionFocus(direction) {
        var rows = environmentCatalog.length
        if (environmentFocusIndex === rows && direction > 0) environmentFocusIndex = rows + 1
        else if (environmentFocusIndex === rows + 1)
            environmentFocusIndex = direction > 0 ? rows + 2 : rows
        else if (environmentFocusIndex === rows + 2 && direction < 0) environmentFocusIndex = rows + 1
        environmentDeleteConfirm = false
    }

    function activateEnvironmentFocus() {
        if (environmentManagementBusy || environmentMetadataBusy) return
        if (environmentFocusIndex === -1) return
        if (environmentFocusIndex < environmentCatalog.length) {
            var item = environmentCatalog[environmentFocusIndex]
            if (!environmentIsOpenable(item)) return
            if (selectedEnvironmentName === item.name) openSelectedEnvironment()
            else selectEnvironment(item)
            return
        }
        if (environmentFocusIndex === environmentCatalog.length) beginEnvironmentCreate()
        else if (environmentFocusIndex === environmentCatalog.length + 1) beginEnvironmentEdit()
        else requestEnvironmentDelete()
    }

    function deleteFocusedEnvironment() {
        if (environmentFocusIndex < environmentCatalog.length) {
            var item = environmentCatalog[environmentFocusIndex]
            if (!environmentIsOpenable(item)) return
            if (selectedEnvironmentName !== item.name) selectEnvironment(item)
        }
        requestEnvironmentDelete()
    }

    function beginEnvironmentCreate() {
        if (environmentManagementBusy || environmentMetadataBusy) return
        environmentCreateOpen = true
        environmentEditOpen = false
        environmentDeleteConfirm = false
        environmentSwitchError = ""
        environmentDraftName = ""
        environmentDraftDescription = ""
        environmentSystemKind = "arch"
        environmentCreateCustomizeOpen = false
        applyEnvironmentPreset("intermediate")
        environmentFeatureDrawer = ""
        environmentFeatureInfo = ""
        environmentCreateFocusIndex = -1
        environmentKeyboardFocus = true
        Qt.callLater(function() { environmentMenu.forceActiveFocus() })
    }

    function requestEnvironmentDelete() {
        if (!selectedEnvironmentName.length || environmentManagementBusy || environmentMetadataBusy) return
        if (environmentDeleteConfirm) destroySelectedEnvironment()
        else {
            environmentDeleteFocusIndex = 0
            environmentDeleteConfirm = true
        }
    }

    function cancelEnvironmentDelete() {
        environmentDeleteConfirm = false
        environmentDeleteFocusIndex = 0
    }

    function cancelEnvironmentCreate() {
        environmentCreateOpen = false
        environmentDraftName = ""
        environmentDraftDescription = ""
        environmentSwitchError = ""
        environmentKeyboardFocus = true
        environmentFocusIndex = -1
        environmentCreateFocusIndex = -1
        environmentFeatureDrawer = ""
        environmentFeatureInfo = ""
        Qt.callLater(function() { environmentMenu.forceActiveFocus() })
    }

    function beginEnvironmentEdit() {
        var selected = environmentSelection()
        if (!selected || environmentManagementBusy || environmentMetadataBusy) return
        environmentCreateOpen = false
        environmentDeleteConfirm = false
        environmentEditOpen = true
        environmentEditTitle = String(selected.display_name || selected.name)
        environmentEditDescription = String(selected.description || "")
        environmentEditIcon = environmentIcon(selected)
        environmentEditFocusIndex = 1
        environmentSwitchError = ""
        Qt.callLater(function() { environmentEditTitleInput.forceActiveFocus() })
    }

    function cancelEnvironmentEdit() {
        if (environmentMetadataBusy) return
        environmentEditOpen = false
        environmentEditTitle = ""
        environmentEditDescription = ""
        environmentEditFocusIndex = -1
        environmentSwitchError = ""
        environmentKeyboardFocus = true
        resetEnvironmentFocus()
        Qt.callLater(function() { environmentMenu.forceActiveFocus() })
    }

    function saveEnvironmentMetadata() {
        var title = environmentEditTitle.trim()
        var description = environmentEditDescription.trim()
        if (!selectedEnvironmentName.length || !selectedEnvironmentGeneration.length
                || environmentMetadataBusy || environmentManagementBusy) return
        if (!title.length) {
            environmentSwitchError = "O título não pode ficar vazio."
            environmentEditFocusIndex = 1
            environmentEditTitleInput.forceActiveFocus()
            return
        }
        environmentSwitchError = ""
        environmentMetadataBusy = true
        environmentMetadataProcess.command = [root.environmentClient, "edit",
                                              "--target", selectedEnvironmentName,
                                              "--generation", selectedEnvironmentGeneration,
                                              "--display-name", title,
                                              "--description", description,
                                              "--icon", environmentEditIcon]
        environmentMetadataProcess.running = true
    }

    function handleEnvironmentEditKey(event) {
        if (event.key === Qt.Key_Escape) cancelEnvironmentEdit()
        else if (event.key === Qt.Key_Up)
            environmentEditFocusIndex = Math.max(0, environmentEditFocusIndex - 1)
        else if (event.key === Qt.Key_Down)
            environmentEditFocusIndex = Math.min(4, environmentEditFocusIndex + 1)
        else if (event.key === Qt.Key_Backtab)
            environmentEditFocusIndex = (environmentEditFocusIndex + 4) % 5
        else if (event.key === Qt.Key_Tab)
            environmentEditFocusIndex = (environmentEditFocusIndex + 1) % 5
        else if (environmentEditFocusIndex === 3 && (event.key === Qt.Key_Left || event.key === Qt.Key_Right)) {
            var choices = environmentIconChoices
            environmentEditIcon = choices[(choices.indexOf(environmentEditIcon) + (event.key === Qt.Key_Left ? choices.length - 1 : 1)) % choices.length]
        }
        else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
            if (environmentEditFocusIndex === 0) cancelEnvironmentEdit()
            else if (environmentEditFocusIndex === 1) environmentEditTitleInput.forceActiveFocus()
            else if (environmentEditFocusIndex === 2) environmentEditDescriptionInput.forceActiveFocus()
            else if (environmentEditFocusIndex === 3) { environmentEditFocusIndex = 4 }
            else saveEnvironmentMetadata()
        } else return
        if (environmentEditFocusIndex === 0 || environmentEditFocusIndex >= 3)
            environmentMenu.forceActiveFocus()
        event.accepted = true
    }

    function environmentModuleIndex(key) {
        for (var index = 0; index < environmentModuleCatalog.length; ++index)
            if (environmentModuleCatalog[index].key === key) return index
        return -1
    }

    function environmentCreateVisibleFocusIndices() {
        var indices = [0, 1, 2, 3, 4]
        if (environmentSystemKind === "windows-native") indices.push(6, 7, 8)
        else {
            indices.push(5)
            if (environmentCreateCustomizeOpen) environmentModuleGroups.forEach(function(group, groupIndex) {
                indices.push(9 + groupIndex)
                if (environmentFeatureDrawer === group.key) group.modules.forEach(function(key) {
                    var moduleIndex = environmentModuleIndex(key)
                    if (moduleIndex >= 0) indices.push(environmentCreateModuleFocusBase + moduleIndex)
                })
            })
        }
        indices.push(environmentCreateSubmitFocusIndex)
        return indices
    }

    function moveEnvironmentCreateFocus(direction, wrap) {
        var indices = environmentCreateVisibleFocusIndices()
        var position = indices.indexOf(environmentCreateFocusIndex)
        if (position < 0) environmentCreateFocusIndex = direction > 0 ? indices[0] : indices[indices.length - 1]
        else environmentCreateFocusIndex = indices[wrap === false
            ? Math.max(0, Math.min(indices.length - 1, position + direction))
            : (position + direction + indices.length) % indices.length]
        environmentMenu.forceActiveFocus()
    }

    function moveEnvironmentCreateHorizontal(direction) {
        var focusIndex = environmentCreateFocusIndex
        if (focusIndex < 0) {
            environmentCreateFocusIndex = direction > 0 ? 3 : 4
        } else if (focusIndex >= 3 && focusIndex <= 4) {
            environmentCreateFocusIndex = 3 + ((focusIndex - 3 + direction + 2) % 2)
        } else if (focusIndex >= 6 && focusIndex <= 8) {
            environmentCreateFocusIndex = 6 + ((focusIndex - 6 + direction + 3) % 3)
        } else if (focusIndex >= environmentCreateModuleFocusBase && focusIndex < environmentCreateSubmitFocusIndex) {
            var moduleIndex = focusIndex - environmentCreateModuleFocusBase
            for (var groupIndex = 0; groupIndex < environmentModuleGroups.length; ++groupIndex) {
                var modules = environmentModuleGroups[groupIndex].modules
                var position = modules.indexOf(environmentModuleCatalog[moduleIndex].key)
                if (position < 0) continue
                var neighbour = position + direction
                if (neighbour >= 0 && neighbour < modules.length
                        && Math.floor(neighbour / 2) === Math.floor(position / 2))
                    environmentCreateFocusIndex = environmentCreateModuleFocusBase + environmentModuleIndex(modules[neighbour])
                break
            }
        }
        environmentMenu.forceActiveFocus()
    }

    function moveEnvironmentCreateVertical(direction) {
        moveEnvironmentCreateFocus(direction, false)
    }

    function activateEnvironmentCreateFocus() {
        var focusIndex = environmentCreateFocusIndex
        if (focusIndex < 0) return
        if (focusIndex === 0) { cancelEnvironmentCreate(); return }
        if (focusIndex === 1) { environmentNameInput.forceActiveFocus(); return }
        if (focusIndex === 2) { environmentDescriptionInput.forceActiveFocus(); return }
        if (focusIndex >= 3 && focusIndex <= 4) {
            environmentSystemKind = ["arch", "windows-native"][focusIndex - 3]
            if (environmentSystemKind === "windows-native" && (!environmentDraftName.length || environmentDraftName === "windows")) environmentDraftName = "windows-2"
            environmentFeatureDrawer = ""
            return
        }
        if (focusIndex === 5 && environmentSystemKind === "arch") {
            environmentCreateCustomizeOpen = !environmentCreateCustomizeOpen
            return
        }
        if (focusIndex >= 6 && focusIndex <= 8 && environmentSystemKind === "windows-native") {
            environmentNativeWindowsSizeGib = [120, 180, 250][focusIndex - 6]
            return
        }
        if (focusIndex >= 9 && focusIndex <= 13) {
            var group = environmentModuleGroups[focusIndex - 9]
            environmentFeatureDrawer = environmentFeatureDrawer === group.key ? "" : group.key
            environmentFeatureInfo = ""
            return
        }
        if (focusIndex >= environmentCreateModuleFocusBase && focusIndex < environmentCreateSubmitFocusIndex) {
            var moduleInfo = environmentModuleCatalog[focusIndex - environmentCreateModuleFocusBase]
            setEnvironmentModule(moduleInfo.key, environmentSelectedModules[moduleInfo.key] !== true)
            return
        }
        if (focusIndex === environmentCreateSubmitFocusIndex) createEnvironment(environmentNameInput.text, environmentDescriptionInput.text)
    }

    function handleEnvironmentCreateKey(event) {
        if (event.key === Qt.Key_Escape) cancelEnvironmentCreate()
        else if (event.key === Qt.Key_Up) moveEnvironmentCreateVertical(-1)
        else if (event.key === Qt.Key_Down) moveEnvironmentCreateVertical(1)
        else if (event.key === Qt.Key_Left) moveEnvironmentCreateHorizontal(-1)
        else if (event.key === Qt.Key_Right) moveEnvironmentCreateHorizontal(1)
        else if (event.key === Qt.Key_Backtab) moveEnvironmentCreateFocus(-1)
        else if (event.key === Qt.Key_Tab) moveEnvironmentCreateFocus(1)
        else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) activateEnvironmentCreateFocus()
        else return
        event.accepted = true
    }

    function environmentPresetKeys(preset) {
        if (preset === "basic") return ["system", "cli-aur"]
        if (preset === "complete") return environmentModuleCatalog.filter(function(item) { return item.key !== "iphone-integration" }).map(function(item) { return item.key })
        return environmentModuleCatalog.filter(function(item) { return item.key !== "office" && item.key !== "development" && item.key !== "iphone-integration" }).map(function(item) { return item.key })
    }

    function applyEnvironmentPreset(preset) {
        var next = {}
        environmentPresetKeys(preset).forEach(function(key) { next[key] = true })
        environmentDesktopPreset = preset
        environmentSelectedModules = next
    }

    function setEnvironmentModule(key, enabled) {
        var next = Object.assign({}, environmentSelectedModules)
        next[key] = enabled
        if (enabled) {
            var changed = true
            while (changed) {
                changed = false
                environmentModuleCatalog.forEach(function(item) {
                    if (next[item.key]) item.deps.forEach(function(dep) {
                        if (!next[dep]) { next[dep] = true; changed = true }
                    })
                })
            }
        } else {
            var removed = true
            while (removed) {
                removed = false
                environmentModuleCatalog.forEach(function(item) {
                    if (!next[item.key]) return
                    for (var index = 0; index < item.deps.length; ++index)
                        if (!next[item.deps[index]]) {
                            next[item.key] = false; removed = true; break
                        }
                })
            }
        }
        environmentSelectedModules = next
        environmentDesktopPreset = "custom"
    }

    function selectedEnvironmentModuleKeys() {
        return environmentModuleCatalog.filter(function(item) {
            return environmentSelectedModules[item.key] === true
        }).map(function(item) { return item.key })
    }

    function environmentEstimatedMib() {
        return environmentModuleCatalog.reduce(function(total, item) {
            return total + (environmentSelectedModules[item.key] ? item.mib : 0)
        }, 0)
    }

    function environmentModuleInfo(key) {
        for (var index = 0; index < environmentModuleCatalog.length; ++index)
            if (environmentModuleCatalog[index].key === key) return environmentModuleCatalog[index]
        return { key: key, label: key, mib: 0, deps: [] }
    }

    function openSelectedEnvironment() {
        if (!selectedEnvironmentName.length || environmentSwitchPending || environmentManagementBusy
                || environmentMetadataBusy) return
        var selected = environmentSelection()
        if (!environmentIsOpenable(selected)) return
        environmentSwitchError = ""
        environmentSwitchProgress = 8
        environmentSwitchPending = true
        popup.open = false
        environmentSwitchProcess.command = [root.environmentClient,
                                            environmentIsNative(selected) ? (selected.native_version === 3 ? "native-open-v3" : "native-open") : "open",
                                            "--target", selectedEnvironmentName]
        if (selected.native_version === 3) environmentSwitchProcess.command.push("--generation", selected.generation)
        for (var i = 0; i < transitionVariants.instances.length; ++i)
            transitionVariants.instances[i].contentItem.update()
    }

    function returnToHub() {
        if (!sessionKindReady || environmentSwitchPending || environmentSwitchProcess.running) return
        environmentSwitchError = ""
        environmentSwitchProgress = 8
        environmentSwitchPending = true
        popup.open = false
        // Prefer the authenticated Host return. If startup has not published
        // identity yet, exiting this workload compositor is the bounded local
        // fallback; the existing Host supervisor then restores Hub.
        environmentSwitchProcess.command = identityReady
                ? [root.environmentClient, "return"]
                : ["/usr/bin/hyprctl", "eval", "hl.dsp.exit()"]
        for (var i = 0; i < transitionVariants.instances.length; ++i)
            transitionVariants.instances[i].contentItem.update()
    }

    function createEnvironment(rawName, rawDescription) {
        var visibleName = rawName === undefined ? environmentDraftName : String(rawName)
        var visibleDescription = rawDescription === undefined
            ? environmentDraftDescription : String(rawDescription)
        var name = visibleName.trim().toLowerCase()
        try { name = name.normalize("NFD").replace(/[\u0300-\u036f]/g, "") }
        catch (error) {}
        name = name.replace(/[^a-z0-9]+/g, "-")
            .replace(/-+/g, "-").replace(/^-|-$/g, "")
        if (/^[0-9]/.test(name)) name = "env-" + name
        if (name.length > 27) name = name.slice(0, 27).replace(/-$/g, "")
        if (name === "hub") name = "hub-env"
        environmentDraftName = name
        if (!name.length) {
            environmentSwitchError = "Escreve um nome para o Environment."
            return
        }
        environmentSwitchError = ""
        if (environmentSystemKind === "windows-native") {
            if (nativeCreationPreviewProcess.running) return
            if (nativeCreationPreview.can_create === true && nativeCreationPreview.target === name
                    && nativeCreationPreview.description === visibleDescription.trim()
                    && nativeCreationPreview.size_gib === environmentNativeWindowsSizeGib) {
                environmentManagementBusy = true
                environmentCreateOpen = false
                environmentActionProcess.command = [root.environmentClient, "native-prepare-v3", "--target", name,
                    "--generation", nativeCreationPreview.plan.new.generation]
                environmentActionProcess.running = true
                return
            }
            nativeCreationPreview = ({})
            nativeCreationPreviewProcess.command = [root.environmentClient, "native-plan", "--target", name,
                "--description", visibleDescription.trim(), "--size-gib", String(environmentNativeWindowsSizeGib)]
            nativeCreationPreviewProcess.running = true
            return
        }
        environmentManagementBusy = true
        // The creation form must leave the scene as soon as the request is
        // accepted. Keeping it rendered behind the catalogue/progress view
        // causes both states to flash while the popup changes height.
        environmentCreateOpen = false
        environmentFeatureDrawer = ""
        environmentFeatureInfo = ""
        environmentCreateFocusIndex = -1
        var requestedPreset = environmentSystemKind === "arch"
            ? (environmentDesktopPreset === "custom" ? "intermediate" : environmentDesktopPreset)
            : "basic"
        var requestedModules = environmentSystemKind === "arch"
            ? selectedEnvironmentModuleKeys()
            : ["system"]
        environmentActionProcess.command = [root.environmentClient, "create", "--target", name,
                                            "--description", visibleDescription.trim(),
                                            "--preset", requestedPreset,
                                            "--modules", requestedModules.join(","),
                                            "--system", environmentSystemKind]
        if (environmentSystemKind === "windows-native")
            environmentActionProcess.command.push("--size-gib", String(environmentNativeWindowsSizeGib))
        environmentActionProcess.running = true
    }

    function destroySelectedEnvironment() {
        if (!selectedEnvironmentName.length || !selectedEnvironmentGeneration.length || environmentManagementBusy
                || environmentMetadataBusy
                ) return
        environmentSwitchError = ""
        environmentManagementBusy = true
        var selected = environmentSelection()
        environmentActionProcess.command = [root.environmentClient,
                                            selected && selected.native_version === 3 ? "native-delete-v3" : "destroy",
                                            "--target", selectedEnvironmentName,
                                            "--generation", selectedEnvironmentGeneration]
        environmentActionProcess.running = true
    }


    function hostAction(operation, target) {
        if (hostActionProcess.running)
            return
        var args = ["/run/apx/host-services-ui-v3.py", operation]
        if (target !== undefined && target !== "")
            args.push(target)
        hostActionProcess.command = args
        hostActionProcess.running = true
    }

    function localAction(args) {
        if (!localActionProcess.running) {
            localActionProcess.command = args
            localActionProcess.running = true
        }
    }

    function showHotkeyOsd(icon, title, detail, progress) {
        hotkeyOsdGoneTimer.stop()
        hotkeyOsdIcon = icon
        hotkeyOsdTitle = title
        hotkeyOsdDetail = detail
        hotkeyOsdProgress = progress === undefined ? -1 : progress
        hotkeyOsdVisible = true
        hotkeyOsdOpacity = 1
        hotkeyOsdHideTimer.interval = title === "Câmara" && focusedFullscreen ? 10000 : 1500
        hotkeyOsdHideTimer.restart()
    }

    property double airplaneWifiSample: 0
    property double airplaneBluetoothSample: 0
    property bool airplaneWifiKnown: false
    property bool airplaneWifiPowered: false
    property bool airplaneBluetoothKnown: false
    property bool airplaneBluetoothPowered: false
    function refreshAirplaneDetails() {
        if (!radioStatusProcess.running) radioStatusProcess.running = true
        if (!airplaneBluetoothStatusProcess.running) airplaneBluetoothStatusProcess.running = true
    }
    function applyRadioState(state) {
        if (state.wifi_powered !== undefined) {
            airplaneWifiPowered = state.wifi_powered === true
            airplaneWifiKnown = true
            airplaneWifiSample = Date.now()
        }
        if (state.airplane_mode === undefined) return
        var next = state.airplane_mode === true
        if (airplaneModeKnown && airplaneMode !== next) {
            showHotkeyOsd(
                next
                    ? Qt.resolvedUrl("icons/lucide/plane.svg")
                    : Qt.resolvedUrl("icons/lucide/plane.svg"),
                "Modo de avião", next ? "Ativado" : "Desativado", -1)
        }
        airplaneMode = next
        airplaneModeKnown = true
    }

    function previewVolume(value) {
        volumeValue = Math.max(0, Math.min(100, Math.round(value)))

        showHotkeyOsd(
            volumeMuted
                ? Qt.resolvedUrl("icons/lucide/volume-x.svg")
                : Qt.resolvedUrl("icons/lucide/volume-2.svg"),
            volumeMuted ? "Som silenciado" : "Volume", volumeValue + "%", volumeValue)

        if (!volumeMuted)
            volumeText = volumeValue + "%"

        // Always keep the newest pointer position.
        volumePending = volumeValue

        // The first movement is applied immediately. There is deliberately
        // no debounce timer here: audio must change while the pointer moves.
        if (!volumeSetProcess.running)
            dispatchVolume()
    }

    function dispatchVolume() {
        if (volumeSetProcess.running || volumePending < 0)
            return

        var nextVolume = volumePending
        volumePending = -1

        // Avoid repeating the exact same physical value.
        if (nextVolume === volumeLastSent)
            return

        volumeInFlight = nextVolume
        volumeLastSent = nextVolume

        volumeSetProcess.command = [
            "/usr/bin/wpctl",
            "set-volume",
            "-l",
            "1",
            "@DEFAULT_AUDIO_SINK@",
            nextVolume + "%"
        ]

        volumeSetProcess.running = true
    }

    function commitVolume(value) {
        // Release uses the same path. It does not unlock or trigger a
        // separate deferred mechanism.
        previewVolume(value)

        if (!volumeSetProcess.running && volumePending >= 0)
            dispatchVolume()
    }

    property int microphonePending: -1
    function dispatchMicrophoneVolume() {
        if (microphoneSetProcess.running || microphonePending < 0) return
        const next = microphonePending
        microphonePending = -1
        microphoneSetProcess.command = ["/usr/bin/wpctl", "set-volume", "-l", "1", "@DEFAULT_AUDIO_SOURCE@", next + "%"]
        microphoneSetProcess.running = true
    }
    Process {
        id: microphoneSetProcess
        onExited: (code, status) => {
            if (root.microphonePending >= 0) Qt.callLater(root.dispatchMicrophoneVolume)
            else if (!microphoneProcess.running) microphoneProcess.running = true
        }
    }

    function commitMicrophoneVolume(value) {
        var nextVolume = Math.round(value)
        microphoneVolume = nextVolume
        if (!microphoneMuted)
            microphoneText = nextVolume + "%"
        showHotkeyOsd(
            microphoneMuted
                ? Qt.resolvedUrl("icons/lucide/mic-off.svg")
                : Qt.resolvedUrl("icons/lucide/mic.svg"),
            "Microfone", microphoneMuted ? "Silenciado" : nextVolume + "%", nextVolume)
        microphonePending = nextVolume
        dispatchMicrophoneVolume()
    }

    function toggleVolumeMute() {
        if (localActionProcess.running) return
        volumeMuted = !volumeMuted
        volumeText = volumeMuted ? "MUTE" : volumeValue + "%"
        showHotkeyOsd(
            volumeMuted
                ? Qt.resolvedUrl("icons/lucide/volume-x.svg")
                : Qt.resolvedUrl("icons/lucide/volume-2.svg"),
            "Som", volumeMuted ? "Silenciado" : "Ativado · " + volumeValue + "%",
            volumeMuted ? 0 : volumeValue)
        localAction(["/usr/bin/wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
    }

    function toggleMicrophoneMute() {
        if (localActionProcess.running) return
        microphoneMuted = !microphoneMuted
        microphoneText = microphoneMuted ? "MUTE" : microphoneVolume + "%"
        showHotkeyOsd(
            microphoneMuted
                ? Qt.resolvedUrl("icons/lucide/mic-off.svg")
                : Qt.resolvedUrl("icons/lucide/mic.svg"),
            "Microfone", microphoneMuted ? "Silenciado" : "Ativado · " + microphoneVolume + "%",
            microphoneMuted ? 0 : microphoneVolume)
        localAction(["/usr/bin/wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "toggle"])
    }

    function applyHardwareControls(state) {
        if (state.display_brightness !== undefined && displayBrightnessPending < 0
                && !displayBrightnessProcess.running && !compactDashboard.brightnessPressed && !displayBrightnessSlider.pressed)
            displayBrightness = Number(state.display_brightness)
        if (state.keyboard_brightness !== undefined)
            keyboardBrightness = Number(state.keyboard_brightness)
        if (state.keyboard_brightness_max !== undefined)
            keyboardBrightnessMax = Number(state.keyboard_brightness_max)
    }

    function previewDisplayBrightness(value) {
        displayBrightness = Math.max(5, Math.min(100, Math.round(value)))
        showHotkeyOsd(
            Qt.resolvedUrl("icons/lucide/sun.svg"),
            "Brilho do ecrã", displayBrightness + "%", displayBrightness)
        displayBrightnessPending = displayBrightness
        if (!displayBrightnessProcess.running && !displayBrightnessDebounce.running)
            displayBrightnessDebounce.start()
    }

    function dispatchDisplayBrightness() {
        if (displayBrightnessProcess.running || displayBrightnessPending < 5) return
        if (displayBrightnessPending === displayBrightnessLastSent) {
            displayBrightnessPending = -1
            return
        }
        hardwareControlError = ""
        displayBrightnessInFlight = displayBrightnessPending
        displayBrightnessLastSent = displayBrightnessPending
        displayBrightnessPending = -1
        displayBrightnessProcess.command = ["/home/apx/.local/libexec/apx-system-power-client-v1.py",
                                            "display-set", String(displayBrightnessInFlight)]
        displayBrightnessProcess.running = true
    }

    function commitDisplayBrightness(value) {
        previewDisplayBrightness(value)
        displayBrightnessDebounce.stop()
        dispatchDisplayBrightness()
    }

    property int displayBrightnessBeforeDim: 70
    function toggleDisplayDim() {
        if (displayBrightnessProcess.running) return
        if (displayBrightness > 5) {
            displayBrightnessBeforeDim = displayBrightness
            commitDisplayBrightness(5)
        } else commitDisplayBrightness(Math.max(6, displayBrightnessBeforeDim))
    }

    function stepDisplayBrightness(delta) {
        commitDisplayBrightness(displayBrightness + delta)
    }

    function cycleKeyboardBrightness() {
        if (keyboardBrightnessProcess.running) return
        hardwareControlError = ""
        keyboardBrightnessProcess.running = true
    }

    function stepVolume(delta) {
        commitVolume(Math.max(0, Math.min(100, volumeValue + delta)))
    }

    function beginPower(action) {
        if (powerBusy) return
        powerBusy = true
        powerAction = action
        powerToken = ""
        powerMessage = "A verificar o Host..."
        powerConfirmOpen = true
        powerTransitionActive = action === "reboot" || action === "poweroff"
        powerPrepareProcess.command = ["/home/apx/.local/libexec/apx-system-power-client-v1.py", "prepare", action]
        powerPrepareProcess.running = true
    }

    function loadHardwareProfile() {
        if (!hardwareProfileProcess.running)
            hardwareProfileProcess.running = true
    }

    function platformLabel(profile) {
        if (profile === "low-power") return "Poupar"
        if (profile === "balanced") return "Equilibrado"
        if (profile === "performance") return "Desempenho"
        return "Indisponível"
    }

    function gpuLabel(profile) {
        if (profile === "hybrid") return "Híbrido"
        if (profile === "nvidia") return "GPU Dedicada"
        return "Indisponível"
    }

    function setPlatformProfile(profile) {
        if (hardwareBusy) return
        hardwareBusy = true
        platformProfileTarget = profile
        platformProfileError = ""
        hardwareMessage = ""
        platformProfileProcess.command = ["/home/apx/.local/libexec/apx-system-power-client-v1.py", "platform-set", profile]
        platformProfileProcess.running = true
    }

    function beginGpuProfile(profile) {
        if (hardwareBusy) return
        hardwareBusy = true
        gpuProfileError = ""
        hardwareApplied = false
        hardwareToken = ""
        hardwareTarget = profile
        hardwareMessage = "A verificar o modo de GPU..."
        hardwareConfirmOpen = true
        gpuPrepareProcess.command = ["/home/apx/.local/libexec/apx-system-power-client-v1.py", "gpu-prepare", profile]
        gpuPrepareProcess.running = true
    }

    function cancelGpuProfile() {
        if (hardwareBusy) return
        if (!hardwareToken.length || hardwareApplied) {
            hardwareConfirmOpen = false
            hardwareApplied = false
            hardwareMessage = ""
            return
        }
        hardwareBusy = true
        gpuCancelProcess.running = true
    }

    function confirmGpuProfile() {
        if (hardwareBusy || !hardwareToken.length) return
        hardwareBusy = true
        hardwareMessage = "A preparar o firmware Lenovo..."
        gpuConfirmProcess.running = true
    }

    function rebootForGpuProfile() {
        hardwareConfirmOpen = false
        hardwareApplied = false
        popupKind = "controls"
        beginPower("reboot")
    }

    function cancelPower() {
        if (powerBusy) return
        if (!powerToken.length) {
            powerConfirmOpen = false
            powerMessage = ""
            return
        }
        powerBusy = true
        powerCancelProcess.running = true
    }

    function confirmPower() {
        if (powerBusy || !powerToken.length) return
        powerBusy = true
        if (powerAction === "suspend") {
            powerMessage = "A bloquear o ecrã e suspender..."
            if (!lockProcess.running) lockProcess.running = true
            suspendLockDelay.restart()
        } else {
            powerMessage = "A fechar o Environment de forma segura..."
            powerConfirmProcess.running = true
        }
    }

    property var dynamicReadMetrics: ({})
    function recordDynamicRead(kind, started) {
        var now = Date.now()
        var reads = Object.assign({}, dynamicReadMetrics)
        reads[kind] = {sample: now, elapsed: now - started}
        dynamicReadMetrics = reads
    }
    function refreshDynamicStatus() {
        Appearance.refresh()
        if (!hostStatusProcess.running) hostStatusProcess.running = true
        if (!volumeProcess.running) volumeProcess.running = true
        if (!microphoneProcess.running) microphoneProcess.running = true
        if (!batteryProcess.running) batteryProcess.running = true
        if (!hardwareProfileProcess.running) hardwareProfileProcess.running = true
        if (!audioStateProcess.running) audioStateProcess.running = true
        if (!radioStatusProcess.running) radioStatusProcess.running = true
    }

    function updateClock() {
        var now = new Date()
        var wasFollowingToday = sameDay(calendarDate, currentDate)
        var dayChanged = !sameDay(currentDate, now)
        currentDate = now
        // Advance the selected day at midnight only while the user was
        // already following today; preserve dates chosen for browsing.
        if (dayChanged && wasFollowingToday)
            calendarDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        function two(value) { return value < 10 ? "0" + value : "" + value }
        clockText = two(now.getDate()) + "/" + two(now.getMonth() + 1) + "/" + now.getFullYear()
                    + " | " + two(now.getHours()) + ":" + two(now.getMinutes())
    }

    Process {
        id: hostStatusProcess
        property double readStarted: 0
        onStarted: readStarted = Date.now()
        onExited: (code, status) => { if (code === 0) root.recordDynamicRead("network", readStarted) }
        command: ["/run/apx/host-services-ui-v3.py", "status"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    // Preserve list models when a reconciliation reports no change.
                    var value = JSON.parse(text)
                    if (JSON.stringify(value) !== JSON.stringify(root.hostState)) root.hostState = value
                    if (root.bluetoothPairPhase === "completed" && (root.hostState.bluetooth_devices || []).some(function(device) { return device.address === root.bluetoothPairAddress && device.connected === true })) {
                        root.dismissBluetoothPairing()
                        root.bluetoothMessage = ""
                    }
                    if (root.hostState.network_name) {
                        root.wifiLastNetwork = root.hostState.network_name
                        root.wifiManualOff = false
                    }
                    if (root.wifiTogglePhase === "disconnecting" && !root.hostState.network_name
                            || root.wifiTogglePhase === "connecting" && root.hostState.network_name) {
                        root.wifiTogglePhase = ""
                        root.wifiOptimisticOverride = false
                    }
                    if (root.bluetoothPowerPhase.length
                            && root.hostState.bluetooth_powered === root.bluetoothPowerActive) {
                        root.bluetoothPowerPhase = ""
                        root.bluetoothPowerOverride = false
                    }
                    if (root.bluetoothDevicePendingAddress.length && !bluetoothDeviceActionProcess.running) {
                        root.bluetoothDevicePendingAddress = ""
                        root.bluetoothDevicePendingAction = ""
                    }
                }
                catch (error) { root.hostState = ({ network_name: "host?", bluetooth_powered: false }) }
            }
        }
    }

    Process {
        id: airplaneBluetoothStatusProcess
        command: ["/run/apx/host-services-client-v3.py", "bluetooth-status"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var state = JSON.parse(text)
                    if (typeof state.powered === "boolean") {
                        root.airplaneBluetoothPowered = state.powered
                        root.airplaneBluetoothKnown = true
                        root.airplaneBluetoothSample = Date.now()
                    }
                } catch (error) {}
            }
        }
    }
    Timer {
        interval: 500; repeat: true
        running: popup.open && root.popupKind === "controls" && root.controlsActivityKind === "airplane"
        triggeredOnStart: true
        onTriggered: root.refreshAirplaneDetails()
    }
    Connections {
        target: DesktopActivity
        function onBusyChanged() {
            if (!DesktopActivity.busy && popup.open && root.controlsActivityKind === "airplane") root.refreshAirplaneDetails()
        }
    }

    Process {
        id: radioStatusProcess
        // rfkill state is kernel-owned and read-only here. Reading sysfs directly
        // also keeps the OSD alive if the host-service socket is replaced while
        // an environment is already running.
        command: ["/usr/bin/bash", "--noprofile", "--norc", "-c",
            "blocked=1; wlan=0; bluetooth=0; wifi_powered=false; "
            + "for directory in /sys/class/rfkill/rfkill*; do "
            + "[ -d \"$directory\" ] || continue; kind=$(<\"$directory/type\"); "
            + "case \"$kind\" in wlan) wlan=1;; bluetooth) bluetooth=1;; *) continue;; esac; "
            + "[ \"$(<\"$directory/soft\")\" = 1 ] || blocked=0; "
            + "if [ \"$kind\" = wlan ] && [ \"$(<\"$directory/soft\")\" = 0 ] && [ \"$(<\"$directory/hard\")\" = 0 ]; then wifi_powered=true; fi; done; "
            + "[ $wlan = 1 ] && [ $bluetooth = 1 ] || exit 1; "
            + "if [ $blocked = 1 ]; then value=true; else value=false; fi; "
            + "printf '{\"airplane_mode\":%s,\"wifi_powered\":%s}\\n' \"$value\" \"$wifi_powered\""]
        stdout: StdioCollector {
            onStreamFinished: {
                try { root.applyRadioState(JSON.parse(text)) }
                catch (error) {}
            }
        }
    }

    Process {
        id: hostActionProcess
        stderr: StdioCollector { onStreamFinished: if (hostActionProcess.command[1] === "wifi-connect" && text.trim()) root.wifiMessage = text.trim() }
        onExited: (code, status) => {
            if (hostActionProcess.command[1] === "wifi-connect" && root.wifiPasswordVisible) {
                if (code === 0) { root.completeWifiConnection() }
                else if (!root.wifiMessage.length || root.wifiMessage.indexOf("A ligar") === 0) root.wifiMessage = "Não foi possível estabelecer a ligação."
            }
            hostStatusProcess.running = true
        }
    }

    Process {
        id: wifiToggleProcess
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.wifiMessage = text.trim() }
        onExited: (exitCode, exitStatus) => {
            if (exitCode !== 0) {
                root.wifiTogglePhase = ""
                root.wifiOptimisticOverride = false
                if (!root.wifiMessage.length) root.wifiMessage = "Não foi possível alterar a ligação Wi-Fi."
            }
            hostStatusProcess.running = true
        }
    }

    Process {
        id: bluetoothPowerProcess
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.bluetoothMessage = text.trim() }
        onExited: (exitCode, exitStatus) => {
            if (exitCode !== 0) {
                root.bluetoothPowerPhase = ""
                root.bluetoothPowerOverride = false
                if (!root.bluetoothMessage.length) root.bluetoothMessage = "Não foi possível alterar o Bluetooth."
            }
            hostStatusProcess.running = true
        }
    }

    Process {
        id: bluetoothDeviceActionProcess
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.bluetoothMessage = text.trim() }
        onExited: (exitCode, exitStatus) => {
            if (exitCode !== 0) {
                root.bluetoothDevicePendingAddress = ""
                root.bluetoothDevicePendingAction = ""
                if (!root.bluetoothMessage.length) root.bluetoothMessage = "Não foi possível alterar o dispositivo."
            }
            hostStatusProcess.running = true
        }
    }

    Process {
        id: bluetoothScanProcess
        command: ["/run/apx/host-services-client-v3.py", "bluetooth-scan"]
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.bluetoothMessage = text.trim() }
        onStarted: root.bluetoothMessage = ""
        onExited: (exitCode, exitStatus) => {
            root.bluetoothMessage = exitCode === 0 ? "" : (root.bluetoothMessage || "Não foi possível procurar dispositivos.")
            hostStatusProcess.running = true
        }
    }

    Process {
        id: bluetoothPairBeginProcess
        stdout: StdioCollector {
            onStreamFinished: {
                try { root.applyBluetoothPairResult(JSON.parse(text)) }
                catch (error) { root.bluetoothPairPhase = "failed"; root.bluetoothMessage = "Resposta de emparelhamento inválida." }
            }
        }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.bluetoothMessage = text.trim() }
        onExited: (exitCode, exitStatus) => {
            if (exitCode !== 0) root.bluetoothPairPhase = "failed"
        }
    }

    Process {
        id: bluetoothPairStatusProcess
        stdout: StdioCollector {
            onStreamFinished: {
                try { root.applyBluetoothPairResult(JSON.parse(text)) }
                catch (error) { root.bluetoothPairPhase = "failed"; root.bluetoothMessage = "Não foi possível atualizar o emparelhamento." }
            }
        }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.bluetoothMessage = text.trim() }
        onExited: (exitCode, exitStatus) => { if (exitCode !== 0) root.bluetoothPairPhase = "failed" }
    }

    Process {
        id: bluetoothPairRespondProcess
        stdinEnabled: true
        onStarted: {
            root.bluetoothShowPin = false
            if (root.bluetoothPairResponsePin.length) write(root.bluetoothPairResponsePin + "\n")
            root.bluetoothPairResponsePin = ""
            root.bluetoothPairPin = ""
        }
        stdout: StdioCollector {
            onStreamFinished: {
                try { root.applyBluetoothPairResult(JSON.parse(text)) }
                catch (error) { root.bluetoothPairPhase = "failed"; root.bluetoothMessage = "Não foi possível confirmar o emparelhamento." }
            }
        }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.bluetoothMessage = text.trim() }
        onExited: (exitCode, exitStatus) => { if (exitCode !== 0) root.bluetoothPairPhase = "failed" }
    }

    Process {
        id: bluetoothRemoveProcess
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.bluetoothMessage = text.trim() }
        onExited: (exitCode, exitStatus) => {
            root.bluetoothMessage = exitCode === 0 ? root.bluetoothRemoveName + " foi esquecido." : (root.bluetoothMessage || "Não foi possível esquecer o dispositivo.")
            root.bluetoothRemoveAddress = ""
            root.bluetoothRemoveName = ""
            hostStatusProcess.running = true
        }
    }

    Process {
        id: wifiCredentialProcess
        stdinEnabled: true
        stderr: StdioCollector {
            onStreamFinished: if (text.trim().length) root.wifiMessage = text.trim()
        }
        onStarted: {
            root.wifiShowPassword = false
            write(root.wifiIsEnterprise(root.wifiSelectedSsid)
                  ? JSON.stringify({kind: "enterprise", method: root.wifiEnterpriseMethod,
                                    identity: root.wifiUsername, password: root.wifiPassword,
                                    domain: root.wifiDomain, ca_cert: root.wifiCaCert}) + "\n"
                  : root.wifiPassword + "\n")
            root.wifiPassword = ""
        }
        onExited: (exitCode, exitStatus) => {
            if (exitCode === 0) {
                root.completeWifiConnection()
            } else if (!root.wifiMessage.length) {
                root.wifiMessage = "Não foi possível estabelecer a ligação."
            }
            hostStatusProcess.running = true
        }
    }

    Process {
        id: wifiConnectivityProcess
        command: ["/run/apx/host-services-ui-v3.py", "wifi-connectivity-check"]
        onExited: hostStatusProcess.running = true
    }
    Process {
        id: wifiPortalProcess
        command: ["/run/apx/host-services-ui-v3.py", "wifi-portal-open"]
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.wifiMessage = text.trim() }
        onExited: (exitCode, exitStatus) => {
            if (exitCode === 0) root.wifiMessage = "Página de autenticação aberta."
            else if (!root.wifiMessage.length) root.wifiMessage = "Não foi possível abrir a página de autenticação."
            hostStatusProcess.running = true
        }
    }

    Process {
        id: localActionProcess
        onExited: {
            volumeProcess.running = true
            microphoneProcess.running = true
            batteryProcess.running = true
            audioStateProcess.running = true
        }
    }

    Process { id: lockProcess; command: ["/home/apx/.local/bin/apx-detached-launch", "/usr/bin/hyprlock"] }
    Timer {
        id: suspendLockDelay
        interval: 500
        repeat: false
        onTriggered: powerConfirmProcess.running = true
    }

    Process {
        id: volumeSetProcess

        onExited: {
            root.volumeInFlight = -1

            // Pointer movement that happened while wpctl was running is
            // represented by volumePending. Send that newest value now,
            // without waiting for release and without any timer.
            if (root.volumePending >= 0)
                root.dispatchVolume()
            else if (!volumeSlider.pressed && !volumeProcess.running)
                volumeProcess.running = true
        }
    }

    Process {
        id: volumeProcess
        property double readStarted: 0
        onStarted: readStarted = Date.now()
        onExited: (code, status) => { if (code === 0) root.recordDynamicRead("volume", readStarted) }
        command: ["/usr/bin/wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]
        stdout: StdioCollector {
            onStreamFinished: {
                var match = text.match(/Volume:\s+([0-9.]+)/)
                if (match && root.volumePending < 0
                        && !volumeSetProcess.running && !volumeSlider.pressed)
                    root.volumeValue = Math.round(parseFloat(match[1]) * 100)

                root.volumeMuted = text.indexOf("MUTED") >= 0

                if (root.volumePending < 0
                        && !volumeSetProcess.running && !volumeSlider.pressed)
                    root.volumeText = match
                            ? (root.volumeMuted ? "MUTE"
                                               : root.volumeValue + "%")
                            : "--"
            }
        }
    }

    Process {
        id: microphoneProcess
        property double readStarted: 0
        onStarted: readStarted = Date.now()
        onExited: (code, status) => { if (code === 0) root.recordDynamicRead("microphone", readStarted) }
        command: ["/usr/bin/wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"]
        stdout: StdioCollector {
            onStreamFinished: {
                var match = text.match(/Volume:\s+([0-9.]+)/)
                if (match && !microphoneSetProcess.running && root.microphonePending < 0) root.microphoneVolume = Math.round(parseFloat(match[1]) * 100)
                root.microphoneMuted = text.indexOf("MUTED") >= 0
                root.microphoneText = match ? (root.microphoneMuted ? "MUTE" : root.microphoneVolume + "%") : "--"
            }
        }
    }

    Process {
        id: batteryProcess
        property double readStarted: 0
        onStarted: readStarted = Date.now()
        onExited: (code, status) => { if (code === 0) root.recordDynamicRead("battery", readStarted) }
        command: ["/usr/bin/bash", "-lc", "for d in /sys/class/power_supply/BAT*; do test -r \"$d/capacity\" || continue; for field in capacity status power_now energy_now energy_full energy_full_design; do if test -r \"$d/$field\"; then tr -d '\\n' < \"$d/$field\"; fi; printf '\\n'; done; exit; done; printf -- '--\\n'"]
        stdout: StdioCollector { onStreamFinished: root.applyBatteryReport(text) }
    }

    Process {
        id: hardwareProfileProcess
        property double readStarted: 0
        command: ["/home/apx/.local/libexec/apx-system-power-client-v1.py", "hardware-status"]
        property string response: ""
        onStarted: { readStarted = Date.now(); response = ""; root.hardwareStatusError = "" }
        stderr: StdioCollector { onStreamFinished: root.hardwareStatusError = text.trim() }
        stdout: StdioCollector { onStreamFinished: hardwareProfileProcess.response = text }
        onExited: (exitCode, exitStatus) => {
            if (exitCode === 0) root.recordDynamicRead("hardware", readStarted)
            // A status request started before a mutation must not undo its UI.
            if (root.hardwareBusy) return
            try {
                if (exitCode !== 0) throw new Error("status failed")
                var result = JSON.parse(response)
                if (!Array.isArray(result.platform_profiles)) throw new Error("invalid status")
                if (JSON.stringify(result) !== JSON.stringify(root.hardwareProfile)) root.hardwareProfile = result
                root.applyHardwareControls(result)
                root.hardwareStatusError = ""
            } catch (error) {
                root.hardwareStatusError = root.hardwareStatusError || "Não foi possível consultar os perfis do Host."
                root.hardwareProfile = ({})
            }
        }
    }

    Process {
        id: platformProfileProcess
        property string response: ""
        onStarted: response = ""
        stderr: StdioCollector { onStreamFinished: root.platformProfileError = text.trim() }
        stdout: StdioCollector { onStreamFinished: platformProfileProcess.response = text }
        onExited: (exitCode, exitStatus) => {
            root.hardwareBusy = false
            try {
                if (exitCode !== 0) throw new Error("command failed")
                var result = JSON.parse(response)
                if (result.platform_profile !== root.platformProfileTarget) throw new Error("profile not applied")
                root.hardwareProfile = Object.assign({}, root.hardwareProfile, result)
                root.applyHardwareControls(result)
                root.hardwareMessage = ""
            } catch (error) {
                root.platformProfileError = root.platformProfileError || "Não foi possível aplicar o modo de energia."
                root.hardwareMessage = root.platformProfileError
            }
            root.platformProfileTarget = ""
        }
    }

    Process {
        id: gpuPrepareProcess
        stderr: StdioCollector { onStreamFinished: root.gpuProfileError = text.trim() }
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var result = JSON.parse(text)
                    root.hardwareToken = result.token || ""
                    root.hardwareMessage = "Mudar para " + root.gpuLabel(result.profile)
                            + " exige reinício. O Environment será fechado e o caminho físico do ecrã poderá mudar."
                } catch (error) {
                    root.hardwareToken = ""
                    root.hardwareMessage = root.gpuProfileError.length
                            ? root.gpuProfileError : "O Host recusou a alteração de GPU."
                }
            }
        }
        onExited: root.hardwareBusy = false
    }

    Process {
        id: gpuConfirmProcess
        command: ["/home/apx/.local/libexec/apx-system-power-client-v1.py", "gpu-confirm", "--token-stdin"]
        stdinEnabled: true
        property string response: ""
        onStarted: { response = ""; root.gpuProfileError = ""; gpuConfirmProcess.write(root.hardwareToken + "\n") }
        stderr: StdioCollector { onStreamFinished: root.gpuProfileError = text.trim() }
        stdout: StdioCollector { onStreamFinished: gpuConfirmProcess.response = text }
        onExited: (exitCode, exitStatus) => {
            root.hardwareBusy = false
            try {
                if (exitCode !== 0) throw new Error("GPU command failed")
                var result = JSON.parse(response)
                if (result.requested_gpu_profile !== root.hardwareTarget || result.reboot_required !== true)
                    throw new Error("GPU profile not staged")
                root.hardwareProfile = result
                root.applyHardwareControls(result)
                root.hardwareToken = ""
                root.hardwareApplied = true
                root.hardwareMessage = "Perfil " + root.gpuLabel(root.hardwareTarget)
                        + " preparado. Reinicie agora ou mais tarde para o aplicar."
            } catch (error) {
                root.hardwareApplied = false
                root.hardwareMessage = root.gpuProfileError || "Não foi possível preparar o perfil de GPU."
            }
        }
    }

    Process {
        id: gpuCancelProcess
        command: ["/home/apx/.local/libexec/apx-system-power-client-v1.py", "gpu-cancel", "--token-stdin"]
        stdinEnabled: true
        onStarted: gpuCancelProcess.write(root.hardwareToken + "\n")
        onExited: {
            root.hardwareBusy = false
            root.hardwareToken = ""
            root.hardwareConfirmOpen = false
            root.hardwareMessage = ""
        }
    }

    Process {
        id: displayBrightnessProcess
        stderr: StdioCollector { onStreamFinished: root.hardwareControlError = text.trim() }
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    root.applyHardwareControls(JSON.parse(text))
                    root.hardwareControlError = ""
                } catch (error) {
                    if (!root.hardwareControlError.length)
                        root.hardwareControlError = "Não foi possível alterar o brilho do ecrã."
                }
            }
        }
        onExited: (exitCode, exitStatus) => {
            if (exitCode !== 0)
                root.showHotkeyOsd(
                    Qt.resolvedUrl("icons/lucide/sun.svg"),
                    "Brilho do ecrã", "Não foi possível alterar", -1)
            root.displayBrightnessInFlight = -1
            if (root.displayBrightnessPending >= 5)
                displayBrightnessDebounce.restart()
        }
    }

    Process {
        id: keyboardBrightnessProcess
        command: ["/home/apx/.local/libexec/apx-system-power-client-v1.py", "keyboard-cycle"]
        stderr: StdioCollector { onStreamFinished: root.hardwareControlError = text.trim() }
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    root.applyHardwareControls(JSON.parse(text))
                    root.hardwareControlError = ""
                } catch (error) {
                    if (!root.hardwareControlError.length)
                        root.hardwareControlError = "Não foi possível alterar a luz do teclado."
                }
            }
        }
    }

    Process {
        id: legionBrightnessKeysProcess
        command: ["/home/apx/.local/bin/apx-legion-brightness-keys-v1.py"]
        // This observer is single-instanced with QuickShell and does not grab
        // either keyboard exclusively.
        running: true
    }

    Timer {
        interval: 1500
        repeat: true
        running: !legionBrightnessKeysProcess.running
        onTriggered: legionBrightnessKeysProcess.running = true
    }

    Process {
        id: calendarLoadProcess
        command: ["/usr/bin/python3", "/home/apx/.config/quickshell/apx/calendar_store.py", "load"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var payload = JSON.parse(text)
                    root.calendarLocalEvents = payload.events || []
                    root.calendarLocalCategories = payload.categories || []
                    root.calendarEvents = root.calendarLocalEvents.concat(root.calendarSharedEvents)
                    root.calendarCategories = root.calendarLocalCategories.concat(root.calendarSharedCategories.filter(function(category) { return root.calendarLocalCategories.indexOf(category) < 0 }))
                } catch (error) {
                    root.calendarEvents = []
                    root.calendarCategories = []
                }
            }
        }
    }

    Process { id: calendarSaveProcess }

    Process {
        id: calendarSharedLoadProcess
        command: ["/run/apx/host-services-client-v3.py", "calendar-load"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var payload = JSON.parse(text)
                    root.calendarSharedEvents = payload.events || []
                    root.calendarSharedCategories = payload.categories || []
                    root.calendarEvents = root.calendarLocalEvents.concat(root.calendarSharedEvents)
                    root.calendarCategories = root.calendarLocalCategories.concat(root.calendarSharedCategories.filter(function(category) { return root.calendarLocalCategories.indexOf(category) < 0 }))
                } catch (error) {
                    root.calendarSharedEvents = []
                    root.calendarSharedCategories = []
                }
            }
        }
    }

    Process { id: calendarSharedSaveProcess }

    Process {
        id: environmentIdentityProcess
        command: ["/run/apx/environment-switch-client-v1.py", "identity"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    root.environmentIdentity = JSON.parse(text)
                    root.identityReady = true
                } catch (error) {
                    root.identityReady = false
                }
            }
        }
    }
    Process {
        id: sessionKindProcess
        command: ["/usr/bin/test", "-S", "/run/apx/host-console-v1.sock"]
        running: true
        onExited: function(exitCode) {
            root.sessionHubProof = exitCode === 0
            root.sessionKindReady = true
        }
    }
    Process {
        id: environmentSwitchProcess
        stderr: StdioCollector {
            onStreamFinished: root.environmentSwitchError = text.trim()
        }
        onExited: function(exitCode) {
            if (exitCode !== 0) {
                root.environmentSwitchPending = false
                if (!root.environmentSwitchError.length)
                    root.environmentSwitchError = "O Host recusou a transição. Tenta novamente."
            }
        }
    }
    Process {
        id: environmentCatalogProcess
        command: [root.environmentClient, "catalog"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var items = JSON.parse(text)
                    if (popup.open && root.popupKind === "environments" &&
                            (root.popupAnimationPending || popupOpenAnimation.running))
                        root.pendingEnvironmentCatalog = items
                    else {
                        root.pendingEnvironmentCatalog = null
                        root.applyEnvironmentCatalog(items)
                    }
                } catch (error) {
                    root.environmentSwitchError = "Não foi possível atualizar os Environments."
                }
            }
        }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.environmentSwitchError = text.trim() }
    }
    Process {
        id: environmentStorageProcess
        command: [root.environmentClient, "storage"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var storage = JSON.parse(text)
                    if (Number(storage.total_bytes || 0) > 0 && Number(storage.available_bytes || 0) >= 0)
                        root.environmentStorageState = storage
                } catch (error) {
                    // Keep the last successful values when a read temporarily fails.
                }
            }
        }
    }
    Process {
        id: environmentManagementStatusProcess
        command: [root.environmentClient, "management-status"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var state = JSON.parse(text)
                    root.environmentManagementState = state
                    root.environmentProgressReadFailures = 0
                    root.environmentManagementBusy = state.busy === true
                    if (state.native_recovery !== true) root.nativeRecoveryDiscardConfirm = false
                    if (state.phase === "complete") {
                        root.environmentSwitchError = ""
                        if ((state.action === "destroy" || state.action === "native-delete-v3") && root.selectedEnvironmentName === state.target) {
                            root.selectedEnvironmentName = ""
                            root.selectedEnvironmentGeneration = ""
                        }
                        root.environmentCreateOpen = false
                        root.environmentDeleteConfirm = false
                        root.environmentDraftName = ""
                        root.environmentDraftDescription = ""
                        if (!environmentCatalogProcess.running) environmentCatalogProcess.running = true
                        if (!environmentStorageProcess.running) environmentStorageProcess.running = true
                    } else if (state.phase === "failed") {
                        root.environmentSwitchError = state.message || "A operação falhou."
                    }
                } catch (error) {
                    root.environmentProgressReadFailures += 1
                    if (root.environmentProgressReadFailures < 5) {
                        environmentManagementStatusRetryTimer.restart()
                    } else {
                        root.environmentSwitchError = "Não foi possível ler o progresso."
                        root.environmentManagementBusy = false
                    }
                }
            }
        }
    }
    Timer {
        id: environmentManagementStatusRetryTimer
        interval: 350
        repeat: false
        onTriggered: if (!environmentManagementStatusProcess.running) environmentManagementStatusProcess.running = true
    }
    Process {
        id: environmentActionProcess
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.environmentSwitchError = text.trim() }
        onExited: function(exitCode) {
            if (exitCode !== 0) root.environmentManagementBusy = false
            if (!environmentManagementStatusProcess.running) environmentManagementStatusProcess.running = true
        }
    }
    Process {
        id: environmentMetadataProcess
        stderr: StdioCollector {
            onStreamFinished: if (text.trim().length) root.environmentSwitchError = text.trim()
        }
        onExited: function(exitCode) {
            root.environmentMetadataBusy = false
            if (exitCode === 0) {
                root.environmentEditOpen = false
                root.environmentEditTitle = ""
                root.environmentEditDescription = ""
                root.environmentEditFocusIndex = -1
                root.environmentSwitchError = ""
                if (!environmentCatalogProcess.running) environmentCatalogProcess.running = true
                Qt.callLater(function() { environmentMenu.forceActiveFocus() })
            } else if (!root.environmentSwitchError.length) {
                root.environmentSwitchError = "Não foi possível guardar o título e a legenda."
            }
        }
    }
    Process { id: environmentFilesProcess; command: ["/home/apx/.local/bin/apx-laptop-action-v1", "files"] }
    Process { id: fileShortcutProcess; command: ["/home/apx/.local/bin/apx-laptop-action-v1", "files"] }
    Process { id: environmentAppsProcess; command: ["/usr/bin/env", "LD_PRELOAD=/home/apx/.local/libexec/apx-rofi-secondary-v1.so", "ROFI_PLUGIN_PATH=/home/apx/.local/lib/rofi", "/usr/bin/rofi", "-modi", "apps,files,system", "-show", "apps", "-me-select-entry", "", "-me-accept-entry", "MousePrimary", "-me-accept-custom", "MouseSecondary", "-kb-cancel", "Escape,Control+g,Control+bracketleft"] }
    Process { id: updateUiProcess; command: root.isHub
        ? ["/home/apx/.local/bin/apx-detached-launch", "/usr/bin/kitty", "--title", "APX Atualizações", "/run/apx/coordinated-update-client-v1.py", "environments-ui"]
        : ["/home/apx/.local/bin/apx-detached-launch", "/usr/bin/kitty", "--title", "APX Atualizações", "/home/apx/.local/bin/apx-environment-update-v1", "--unattended"] }
    Process {
        id: hostConsoleProcess
        command: ["/home/apx/.local/bin/apx-host-console-open"]
    }
    Process {
        id: hostExitProcess
        command: ["/usr/bin/hyprctl", "dispatch", "hl.dsp.exit()"]
    }
    Process {
        id: shortcutStateProcess
        command: ["/home/apx/.local/bin/apx-shortcuts-v1", "status"]
        stdout: StdioCollector { onStreamFinished: root.apxShortcutsEnabled = text.trim() !== "disabled" }
    }
    Process {
        id: shortcutApplyProcess
        stdout: StdioCollector { onStreamFinished: root.apxShortcutsEnabled = text.trim() !== "disabled" }
        onExited: if (!shortcutStateProcess.running) shortcutStateProcess.running = true
    }
    IpcHandler {
        target: "host"
        function notificationRefresh(): void { notificationToasts.refresh() }
        function notificationToastStatus(): string { return JSON.stringify(notificationToasts.status()) }
        function notificationPanelStatus(): string {
            return JSON.stringify({open: popup.open, kind: root.popupKind,
                section: root.controlsActivityKind, bar: !!root.bar,
                target: !!root.controlCenterButton})
        }
        function transitionStatus(): string {
            return JSON.stringify({ startup: root.startupCover, ready: root.startupReady,
                bar_rendered: root.startupBarRendered, identity_ready: root.identityReady,
                environment_identity: root.environmentIdentity, environment_icon: root.activeEnvironmentIcon,
                outgoing: root.environmentSwitchPending, dispatched: root.environmentSwitchDispatched })
        }

        function openShortcuts(): void {
            if (root.queueControlPage("shortcuts")) return
            openControls()
            root.shortcutsOpen = true
            root.controlsMoreOpen = false
        }
        function idleSuspend(): void {
            if (root.powerBusy || root.powerConfirmOpen) return
            root.idleSuspendRequested = true
            root.beginPower("suspend")
        }
        function openTerminal(): void {
            if (!hostConsoleProcess.running)
                hostConsoleProcess.running = true
        }

        function openFiles(): void {
            if (root.isHub) return
            if (!fileShortcutProcess.running)
                fileShortcutProcess.running = true
        }

        function openApplications(): void {
            if (root.isHub) {
                root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/circle-alert.svg"), "Aplicações", "Launcher não instalado no Hub", -1)
                return
            }
            root.toggleApplicationLauncher()
        }

        function toggleApplications(): void { root.toggleApplicationLauncher() }

        function openEnvironments(): void {
            root.environmentKeyboardFocus = false
            root.toggleFocusedPopup("environments")
        }

        function openEnvironmentCreation(): void {
            if (!root.isHub) return
            if (!popup.open || root.popupKind !== "environments") root.toggleFocusedPopup("environments")
            root.beginEnvironmentCreate()
        }


        function prepareShutdown(): void { openControls(); root.beginPower("poweroff") }
        function cancelShutdown(): void { root.cancelPower() }
        function shutdownStatus(): string {
            return JSON.stringify({ open: root.powerConfirmOpen, busy: root.powerBusy, prepared: root.powerToken.length > 0, message: root.powerMessage })
        }

        function hardwareStatus(): string {
            return JSON.stringify({ profile: root.hardwareProfile.platform_profile, pending: root.platformProfileTarget, busy: root.hardwareBusy, error: root.platformProfileError || root.hardwareStatusError })
        }


        function popupStatus(): string {
            return JSON.stringify({ kind: root.popupKind, visible: popup.open,
                                    screen: popup.screen ? popup.screen.name : "",
                                    render_scale: popupBackground.renderScale,
                                    render_texture_scale: popupBackground.textureScale,
                                    render_texture_width: popupBackground.layer.textureSize.width,
                                    render_texture_height: popupBackground.layer.textureSize.height,
                                    bars: barVariants.instances.map(function(b) { return b.screen.name }),
                                    width: popup.menuWidth, height: popup.menuHeight,
                                    island_progress: root.islandProgress, island_closing: root.popupClosing, animation_pending: root.popupAnimationPending,
                                    animation_running: popupOpenAnimation.running,
                                    popup_opacity: popupBackground.opacity,
                                    content_opacity: root.islandContentOpacity, visual_width: popupBackground.width, visual_height: popupBackground.height, visual_x: popupBackground.x, fullscreen: root.focusedFullscreen, camera_active: root.cameraActive, unread_messages: DesktopActivity.notificationEntries.length, menu_title_inset: Appearance.menuTitleInset,
                                    panel_y: popupBackground.y, content_y: menuFlick.y, content_font: Appearance.fontFamily, body_size: Appearance.bodySize, title_size: Appearance.titleSize, visible_fonts: root.visibleMenuFonts(),
                                    airplane_radio_samples: {wifi: root.airplaneWifiSample, bluetooth: root.airplaneBluetoothSample, wifi_powered: root.airplaneWifiPowered, bluetooth_powered: root.airplaneBluetoothPowered},
                                    dynamic_reads: root.dynamicReadMetrics, displayed_controls: root.renderedControls, wifi_powered: root.wifiDisplayPowered(), wifi_connected: root.wifiDisplayActive(), bluetooth_powered: root.bluetoothDisplayPowered(), page_transition: controlPageAnimation.running || root.controlPageCapturing, page_progress: root.controlPageProgress, page_blend: root.controlPageBlend, page_motion: root.controlPageMotion, menu_content_enabled: menuFlick.enabled, transition_input_blocked: controlTransitionShield.enabled, control_tiles: root.visibleControlTiles(), material_animating: panelMaterialFade.running, panel_color: String(popupBackground.color), target_height: popupBackground.targetHeight, settled_height: popupBackground.settledHeight, outgoing_page_opacity: outgoingControlPage.opacity, outgoing_page_visible: outgoingControlPage.visible, outgoing_page_x: outgoingControlPage.x,
                                    pending_kind: root.pendingPopupRequest ? root.pendingPopupRequest.kind : "",
                                    media_width: root.mediaButton ? root.mediaButton.width : 0, media_selected: root.mediaButton ? root.mediaButton.selected : false,
                                    osd_fallback: hotkeyOsdWindow.visible, launcher_running: environmentAppsProcess.running,
                                    ghost_visible: root.ghostGreetingVisible, ghost_message: root.ghostMessage,
                                    ghost_width: root.bar ? root.bar.ghostWidth : 0,
                                    workspaces_expanded: root.workspacesExpanded, workspace_width: root.bar ? root.bar.workspaceWidth : 0,
                                    media_summary_width: root.mediaButton ? root.mediaButton.summaryWidth : 0, media_summary_x: root.mediaButton ? root.mediaButton.summaryX : 0,
                                    bar_targets: ({ calendar: root.barTargetRect(root.calendarButton), controls: root.barTargetRect(root.controlCenterButton), apps: root.barTargetRect(root.appsButton), files: root.barTargetRect(root.filesButton), battery: root.barTargetRect(root.batteryButton), media: root.barTargetRect(root.mediaButton) }),
                                    files_active: root.filesFocused, osd_visible: root.hotkeyOsdVisible, island_transient: root.mediaButton ? root.mediaButton.transientActive : false,
                                    keyboard_items: root.genericMenuItems().length,
                                    keyboard_index: root.genericMenuItems().findIndex(function(item) { return item.activeFocus }),
                                    calendar_view: root.calendarView, calendar_date: root.dateKey(root.calendarDate),
                                    calendar_editor: root.calendarEditor, calendar_navigation_running: calendarNavigationAnimation.running,
                                    calendar_page_opacity: root.calendarPageOpacity, calendar_page_offset: root.calendarPageOffset,
                                    calendar_focus_kind: root.calendarFocusAction.kind,
                                    calendar_focus_key: root.calendarFocusAction.key,
                                    calendar_selected_date: root.calendarSelectedDateKey,
                                    environment_selected_name: root.selectedEnvironmentName,
                                    environment_focus_index: root.environmentFocusIndex,
                                    environment_create_focus_index: root.environmentCreateFocusIndex, environment_edit_focus_index: root.environmentEditFocusIndex,
                                    menu_viewport_cards: root.menuViewportState(),
                                    menu_scroll_y: menuFlick.contentY, menu_viewport_height: menuFlick.height, menu_content_height: menuFlick.contentHeight,
                                    menu_keyboard_navigation: root.menuKeyboardNavigation, environment_keyboard_focus: root.environmentKeyboardFocus,
                                    environment_error: root.environmentSwitchError,
                                    environment_form_name: environmentNameInput.text,
                                    environment_description_length: environmentDescriptionInput.text.length })
        }

        function startMenuFrameProbe(): void { root.menuFrameSamples = []; root.menuFrameProbeEnabled = true }
        function stopMenuFrameProbe(): string {
            root.menuFrameProbeEnabled = false
            return JSON.stringify(root.menuFrameSamples)
        }

        function toggleControls(): void {
            root.toggleFocusedPopup("controls")
        }

        function toggleCalendar(): void {
            root.toggleFocusedPopup("calendar")
        }


        function toggleWorkspaces(): void { root.workspacesExpanded = !root.workspacesExpanded }

        function toggleBattery(): void {
            root.toggleFocusedPopup("battery")
        }

        function openMedia(): void { DesktopActivity.refresh(); root.toggleFocusedPopup("media") }

        function openControls(): void {
            if (root.queueControlPage("")) return
            // APX staged IPC navigation: use the same page transition as pointer actions.
            root.controlsConnectivityOpen = false; root.controlsWifiOpen = false; root.controlsBluetoothOpen = false
            root.controlsBrightnessOpen = false; root.controlsAudioOpen = false; root.controlsMicrophoneOpen = false
            root.controlsMoreOpen = false; root.controlsAppearanceOpen = false
            root.controlsActivityKind = ""; root.shortcutsOpen = false
            root.popupKeyboardRequested = true
            if (popup.open && root.popupKind === "controls" && !root.popupClosing) return
            root.popupKind = "controls"
            root.popupTarget = controlCenterButton
            root.showPopup()
        }
        function openNotifications(): void {
            openControls()
            Qt.callLater(function() { root.openActivitySection("notifications") })
        }

        function openConnectivityControls(): void { openControls(); root.openControlSection("connectivity") }

        function openWifiControls(): void {
            if (root.queueControlPage("wifi")) return
            openControls()
            root.controlsWifiOpen = true
            if (!wifiConnectivityProcess.running) wifiConnectivityProcess.running = true
            root.controlsBluetoothOpen = false
            root.controlsBrightnessOpen = false; root.controlsAudioOpen = false
            root.controlsMicrophoneOpen = false
        }

        function openTrackpadControls(): void {
            openControls()
            root.controlsMoreOpen = true
            root.controlsActivityKind = "trackpad"
            menuFlick.contentY = 0
        }

        function openMoreControls(): void {
            if (root.queueControlPage("more")) return
            openControls()
            root.controlsMoreOpen = true
            root.shortcutsOpen = false
            menuFlick.contentY = 0
        }

        function openBluetoothControls(): void {
            if (root.queueControlPage("bluetooth")) return
            openControls()
            root.controlsConnectivityOpen = false; root.controlsWifiOpen = false
            root.controlsBluetoothOpen = true
            root.controlsBrightnessOpen = false; root.controlsAudioOpen = false
            root.controlsMicrophoneOpen = false
        }

        function openKeyboardControls(): void { openControls(); root.openActivitySection("keyboard") }
        function openAirplaneControls(): void { openControls(); root.openActivitySection("airplane") }
        function openBrightnessControls(): void { openControls(); root.openControlSection("brightness") }

        function openVolumeControls(): void {
            if (root.queueControlPage("audio")) return
            openControls()
            root.controlsConnectivityOpen = false; root.controlsWifiOpen = false
            root.controlsBluetoothOpen = false
            root.controlsAudioOpen = true
            root.controlsMicrophoneOpen = false
            Qt.callLater(function() { if (root.menuKeyboardNavigation) volumeSlider.forceActiveFocus(); else popupBackground.forceActiveFocus() })
        }

        function openMicrophoneControls(): void {
            if (root.queueControlPage("microphone")) return
            openControls()
            root.controlsConnectivityOpen = false; root.controlsWifiOpen = false
            root.controlsBluetoothOpen = false
            root.controlsBrightnessOpen = false; root.controlsAudioOpen = false
            root.controlsMicrophoneOpen = true
            Qt.callLater(function() { if (root.menuKeyboardNavigation) microphoneSlider.forceActiveFocus(); else popupBackground.forceActiveFocus() })
        }

        function openCalendar(): void {
            root.popupKeyboardRequested = true
            root.popupKind = "calendar"
            root.popupTarget = calendarButton
            root.showPopup()
            root.focusCalendarMenuAfterOpen(true)
        }

        function brightnessUp(): void { root.stepDisplayBrightness(5) }
        function brightnessDown(): void { root.stepDisplayBrightness(-5) }
        function volumeUp(): void { root.stepVolume(5) }
        function volumeDown(): void { root.stepVolume(-5) }
        function volumeMute(): void { root.toggleVolumeMute() }
        function microphoneMute(): void { root.toggleMicrophoneMute() }
        function hotkeyApps(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/layout-panel-left.svg"), "Aplicações", "A abrir", -1) }
        function hotkeyAirplaneOff(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/plane-off.svg"), "Modo de avião", "Desativado", -1) }
        function hotkeyAirplaneOn(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/plane.svg"), "Modo de avião", "Ativado", -1) }
        function hotkeyAirplaneUnavailable(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/circle-alert.svg"), "Modo de avião", "Estado indisponível", -1) }
        function hotkeyCalculator(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/calculator.svg"), "Calculadora", "A abrir", -1) }
        function hotkeyCalculatorMissing(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/calculator.svg"), "Calculadora", "Não está instalada", -1) }
        function hotkeyDisplayExtended(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/monitor.svg"), "Ecrãs", "Ambiente estendido", -1) }
        function hotkeyDisplayExternal(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/monitor.svg"), "Ecrãs", "Apenas ecrã externo", -1) }
        function hotkeyDisplayInternal(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/monitor.svg"), "Ecrãs", "Apenas ecrã do portátil", -1) }
        function hotkeyDisplayInternalOnly(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/monitor.svg"), "Ecrãs", "Nenhum ecrã externo", -1) }
        function hotkeyDisplayMirrored(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/monitor.svg"), "Ecrãs", "Imagem duplicada", -1) }
        function hotkeyFailed(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/circle-alert.svg"), "Atalho", "A ação falhou", -1) }
        function hotkeyOverview(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/panels-top-left.svg"), "Janelas abertas", "A mostrar", -1) }
        function hotkeyScreenshot(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/camera.svg"), "Captura de ecrã", "Guardada em Imagens", -1) }
        function hotkeyScreenshotUnavailable(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/circle-alert.svg"), "Captura de ecrã", "Ferramenta não instalada", -1) }
        function hotkeyTouchpadOff(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/touchpad-off.svg"), "Touchpad", "Desativado", -1) }
        function hotkeyTouchpadOn(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/touchpad.svg"), "Touchpad", "Ativado", -1) }
        function hotkeyTouchpadToggled(): void { root.showHotkeyOsd(Qt.resolvedUrl("icons/lucide/touchpad.svg"), "Touchpad", "Estado alterado", -1) }
    }
    Process {
        id: audioStateProcess
        property double readStarted: 0
        onStarted: readStarted = Date.now()
        onExited: (code, status) => { if (code === 0) root.recordDynamicRead("audio", readStarted) }
        command: ["/home/apx/.local/bin/apx-microphone-activity-v1"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var state = JSON.parse(text)
                    root.microphoneActive = state.microphone_active === true
                    root.cameraActive = state.camera_active === true
                    if (typeof state.camera_enabled === "boolean") {
                        var enabled = state.camera_enabled
                        if (root.cameraStateKnown && enabled !== root.cameraEnabled)
                            root.showHotkeyOsd(
                                Qt.resolvedUrl(enabled ? "icons/lucide/camera.svg" : "icons/lucide/camera-off.svg"),
                                "Câmara", enabled ? "Ativada" : "Desativada", -1)
                        root.cameraEnabled = enabled
                        root.cameraStateKnown = true
                    }
                } catch (error) {
                    root.microphoneActive = false
                    root.microphoneText = "--"
                }
            }
        }
    }
    Process {
        id: powerPrepareProcess
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.powerMessage = text.trim() }
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var result = JSON.parse(text)
                    root.powerBusy = false
                    if (result.prepared) {
                        root.powerToken = result.token
                        root.powerMessage = (result.action === "reboot" ? "Reiniciar" :
                                            result.action === "suspend" ? "Suspender" : "Encerrar")
                                            + (result.action === "suspend"
                                               ? " a máquina física? O Environment continuará aberto."
                                               : " a máquina física? O Environment atual será fechado.")
                        if (result.reboot_required) root.powerMessage += " A atualização pede reinício."
                        if (root.powerAction !== "suspend" || root.idleSuspendRequested) root.confirmPower()
                        root.idleSuspendRequested = false
                    } else {
                        root.powerTransitionActive = false
                        root.powerToken = ""
                        root.idleSuspendRequested = false
                        root.powerMessage = "AÇÃO BLOQUEADA :: " + (result.blockers || []).join(" | ")
                    }
                } catch (error) {
                    root.powerBusy = false
                    root.powerTransitionActive = false
                    root.powerToken = ""
                    root.idleSuspendRequested = false
                    root.powerMessage = "Não foi possível consultar o Host."
                }
            }
        }
        onExited: (code, status) => {
            if (code !== 0) {
                root.powerBusy = false
                root.powerTransitionActive = false
                root.idleSuspendRequested = false
                if (root.powerMessage === "A verificar o Host...") root.powerMessage = "O Host recusou a ação."
            }
        }
    }
    Process {
        id: powerConfirmProcess
        command: ["/home/apx/.local/libexec/apx-system-power-client-v1.py", "confirm", "--token-stdin"]
        stdinEnabled: true
        onStarted: powerConfirmProcess.write(root.powerToken + "\n")
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var result = JSON.parse(text)
                    root.powerMessage = result.accepted ? "PEDIDO ACEITE PELO HOST" : "PEDIDO RECUSADO"
                    if (result.accepted) root.powerToken = ""
                    if (!result.accepted) root.powerTransitionActive = false
                } catch (error) { root.powerTransitionActive = false; root.powerMessage = "O Host recusou a ação." }
            }
        }
        onExited: (code, status) => {
            root.powerBusy = false
            if (code !== 0) {
                root.powerTransitionActive = false
                root.powerMessage = "O Host recusou a ação."
            }
        }
    }
    Timer {
        interval: 95000
        running: root.powerTransitionActive
        repeat: false
        onTriggered: {
            root.powerTransitionActive = false
            root.powerMessage = "O Host não concluiu a ação. Verifica o estado antes de tentar novamente."
        }
    }
    Process {
        id: powerCancelProcess
        command: ["/home/apx/.local/libexec/apx-system-power-client-v1.py", "cancel", "--token-stdin"]
        stdinEnabled: true
        onStarted: powerCancelProcess.write(root.powerToken + "\n")
        onExited: {
            root.powerBusy = false
            root.powerToken = ""
            root.powerMessage = ""
            root.powerConfirmOpen = false
            root.powerTransitionActive = false
        }
    }

    // Warm the catalogue after session role discovery, before the first click.
    Timer {
        id: environmentMenuPrefetchTimer
        interval: 250
        running: root.isHub
        repeat: false
        onTriggered: root.refreshEnvironmentMenu()
    }
    // Opening paints the existing rows first; refresh after the 160ms reveal.
    Timer {
        id: environmentMenuRefreshTimer
        interval: 200
        onTriggered: if (popup.open && root.popupKind === "environments") root.refreshEnvironmentMenu()
    }

    Component.onCompleted: {
        calendarLoadProcess.running = true
        calendarSharedLoadProcess.running = true
        shortcutApplyProcess.command = ["/home/apx/.local/bin/apx-shortcuts-v1", "apply"]
        shortcutApplyProcess.running = true
    }

    Timer {
        id: displayBrightnessDebounce
        interval: 20
        repeat: false
        onTriggered: root.dispatchDisplayBrightness()
    }

    Timer {
        id: hotkeyOsdHideTimer
        interval: 1500
        repeat: false
        onTriggered: {
            root.hotkeyOsdOpacity = 0
            hotkeyOsdGoneTimer.restart()
        }
    }

    Timer {
        id: hotkeyOsdGoneTimer
        interval: 180
        repeat: false
        onTriggered: root.hotkeyOsdVisible = false
    }

    Timer {
        interval: popup.open ? 500 : 3000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: if (!radioStatusProcess.running) radioStatusProcess.running = true
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: root.updateClock()
    }

    Timer {
        interval: popup.open ? 500 : 3000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            if (!hostStatusProcess.running) hostStatusProcess.running = true
            if (!volumeProcess.running) volumeProcess.running = true
            if (!microphoneProcess.running) microphoneProcess.running = true
        }
    }

    // Device settings have no visible consumers while Controls is closed.
    Timer {
        id: inputSettingsRefreshTimer
        interval: 500; repeat: true; triggeredOnStart: true
        running: popup.open && root.popupKind === "controls"
        onTriggered: {
            if (!mouseSensitivityStatusProcess.running && !mouseSensitivityProcess.running) mouseSensitivityStatusProcess.running = true
            if (!trackpadSensitivityStatusProcess.running && !trackpadSensitivityProcess.running) trackpadSensitivityStatusProcess.running = true
        }
    }
    // Keep open menus fresh without launching slow sensor helpers twice a second at idle.
    Timer {
        id: backgroundSensorsRefreshTimer
        interval: popup.open ? 500 : 5000
        running: true; repeat: true; triggeredOnStart: true
        onTriggered: {
            if (!batteryProcess.running) batteryProcess.running = true
            if (!hardwareProfileProcess.running) hardwareProfileProcess.running = true
        }
    }

    Timer {
        interval: root.identityReady ? 5000 : 250; running: true; repeat: true; triggeredOnStart: true
        onTriggered: if (!environmentIdentityProcess.running) environmentIdentityProcess.running = true
    }

    Timer {
        interval: 350
        running: root.environmentManagementBusy
        repeat: true
        onTriggered: if (!environmentManagementStatusProcess.running) environmentManagementStatusProcess.running = true
    }

    Connections {
        target: bar ? bar.contentItem.Window.window : null
        function onFrameSwapped() { root.startupBarRendered = true }
    }

    Timer {
        interval: popup.open ? 500 : 3000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: if (!audioStateProcess.running) audioStateProcess.running = true
    }

    Timer {
        interval: 500
        repeat: true
        running: root.bluetoothPairSessionId.length > 0
                 && root.bluetoothPairPhase !== "needs-response"
                 && root.bluetoothPairPhase !== "completed"
                 && root.bluetoothPairPhase !== "failed"
        onTriggered: {
            if (!bluetoothPairStatusProcess.running && !bluetoothPairBeginProcess.running && !bluetoothPairRespondProcess.running) {
                bluetoothPairStatusProcess.command = ["/run/apx/host-services-client-v3.py", "bluetooth-pair-status", root.bluetoothPairSessionId]
                bluetoothPairStatusProcess.running = true
            }
        }
    }

    Timer {
        interval: 400
        repeat: true
        running: root.wifiTogglePhase.length > 0
                 || root.bluetoothPowerPhase.length > 0
                 || root.bluetoothDevicePendingAddress.length > 0
        onTriggered: if (!hostStatusProcess.running) hostStatusProcess.running = true
    }

    Timer {
        id: barAnimationReset
        interval: 150
        repeat: false
        onTriggered: {
            root.animatedBarOpenKind = ""
            root.animatedBarCloseKind = ""
        }
    }

    component MenuHeader: Item {
        id: menuHeader
        opacity: popupBackground.scrollingHeader === menuHeader
            ? 1 - stickyMenuHeader.revealProgress : 1
        property string title: ""
        width: parent.width
        height: 30
        Text { renderType: Text.QtRendering;
            anchors.left: parent.left
            anchors.leftMargin: Appearance.menuTitleInset
            anchors.right: parent.right
            height: 24
            verticalAlignment: Text.AlignVCenter
            text: parent.title
            color: root.textMain
            font.family: Appearance.fontFamily
            font.pixelSize: root.menuTitleSize
            font.weight: Font.DemiBold
        }
        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 1
            color: root.controlButtonOutline
        }
    }

    component SelectionIndicator: Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 4
        width: 18
        height: 2
        radius: 1
        color: root.textMain
        z: 2
    }

    component BluetoothDeviceRow: Rectangle {
        id: deviceRow
        required property var device
        property bool connected: false
        property bool paired: false
        property bool pending: root.bluetoothDevicePendingAddress === device.address
        signal activated()
        signal forgetRequested()
        width: parent ? parent.width : 300; height: connected ? 56 : 44; radius: Appearance.menuActionRadius
        color: root.controlButtonSurface
        LucideIcon {
            name: "bluetooth"; width: Appearance.menuGlyphSize; height: width
            anchors.left: parent.left; anchors.leftMargin: Appearance.menuIconInset + (Appearance.menuIconCircleSize - Appearance.menuGlyphSize) / 2; anchors.verticalCenter: parent.verticalCenter
            opacity: deviceRow.connected ? 1 : .65
        }
        Text { renderType: Text.QtRendering;
            anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset
            anchors.right: deviceActions.left; anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter; elide: Text.ElideRight
            text: deviceRow.device.name || deviceRow.device.address
            color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
        }
        BounceMouseArea {
            id: deviceMouse
            anchors.fill: parent; anchors.rightMargin: deviceActions.width + 16
            enabled: !deviceRow.connected && !root.bluetoothDevicePendingAddress.length && !bluetoothPairBeginProcess.running && !bluetoothPairRespondProcess.running
            hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
            onClicked: deviceRow.activated()
        }
        Row {
            id: deviceActions
            anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter; spacing: 6
            MenuButton {
                width: deviceRow.connected || !deviceRow.paired ? 104 : 68; height: 32; radius: 8
                brightActionHover: deviceRow.connected
                actionSurface: deviceRow.color
                label: deviceRow.pending ? (deviceRow.connected ? "A desligar…" : "A ligar…") : (deviceRow.connected ? "Desconectar" : (deviceRow.paired ? "Ligar" : "Emparelhar"))
                enabled: !root.bluetoothDevicePendingAddress.length && !bluetoothPairBeginProcess.running && !bluetoothPairRespondProcess.running
                onActivated: deviceRow.activated()
            }
            MenuButton {
                visible: deviceRow.paired && !deviceRow.connected
                width: visible ? 30 : 0; height: Appearance.menuActionHeight; label: "…"
                enabled: !root.bluetoothDevicePendingAddress.length
                Accessible.name: "Esquecer " + (deviceRow.device.name || deviceRow.device.address)
                onActivated: deviceRow.forgetRequested()
            }
        }
    }

    component MenuButton: Rectangle {
        id: menuButton
        property string label: ""
        property string iconName: ""
        property bool accent: false
        property bool lighterSurface: false
        property bool alignedIcon: iconName.length > 0
        property bool brightActionHover: false
        property color actionSurface: root.controlButtonSurface
        property bool selected: false
        property bool outlined: false
        property bool keyboardFocused: false
        onKeyboardFocusedChanged: if (keyboardFocused) root.revealKeyboardMenuItem(this)
        signal activated()
        width: parent ? parent.width : 250
        height: Appearance.menuActionHeight
        opacity: enabled ? 1 : 0.42
        radius: Appearance.menuActionRadius
        antialiasing: true
        HoverHandler { id: actionPointer; blocking: false }
        color: brightActionHover ? Qt.lighter(actionSurface, 1.6) : (keyboardFocused || menuMouse.activeFocus || menuMouse.keyboardActivationPending) ? root.controlButtonActive : (lighterSurface ? Qt.lighter(root.controlButtonActive, 1.5) : ((accent ? root.controlButtonActive : root.controlButtonSurface)))
        readonly property bool outlineManaged: true
        border.width: 0
        ButtonOutline {
            outlineTarget: menuButton
            selected: menuButton.keyboardFocused || menuMouse.activeFocus || menuMouse.keyboardActivationPending || menuButton.selected
            hovered: actionPointer.hovered && menuButton.enabled
            idleWidth: menuButton.outlined ? 1 : 0
        }
        Rectangle {
            visible: menuButton.alignedIcon
            objectName: "menuIconCircle"
            x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter; width: Appearance.menuIconCircleSize; height: width; radius: width / 2
            color: Qt.lighter(menuButton.color, 1.6)
        }
        LucideIcon {
            visible: menuButton.iconName.length > 0
            name: menuButton.iconName; tint: root.textMain
            width: menuButton.alignedIcon ? Appearance.menuGlyphSize : 17; height: width
            anchors.left: parent.left; anchors.leftMargin: menuButton.alignedIcon ? Appearance.menuIconInset + (Appearance.menuIconCircleSize - Appearance.menuGlyphSize) / 2 : 11
            anchors.verticalCenter: parent.verticalCenter
        }
        Text { renderType: Text.QtRendering;
            anchors.left: parent.left
            anchors.leftMargin: menuButton.alignedIcon ? Appearance.menuLabelInset : (menuButton.iconName.length ? 36 : 11)
            anchors.right: parent.right
            anchors.rightMargin: 11
            elide: Text.ElideRight
            anchors.verticalCenter: parent.verticalCenter
            text: menuButton.label
            color: root.textMain
            font.family: Appearance.fontFamily
            font.pixelSize: root.menuBodySize
        }
        SelectionIndicator { visible: menuButton.selected }
        BounceMouseArea {
            id: menuMouse
            anchors.fill: parent
            enabled: menuButton.enabled
            hoverEnabled: true
            cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
            onClicked: menuButton.activated()
        }
    }

    component EventField: Rectangle {
        id: field
        property alias text: input.text
        property string placeholder: ""
        function focusInput() { input.forceActiveFocus() }
        width: parent ? parent.width : 300
        height: 34
        radius: 6
        color: root.controlButtonSurface
        border.width: input.activeFocus ? 1 : 0
        border.color: root.cyan
        TextInput {
            id: input
            activeFocusOnTab: true
            anchors.fill: parent
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            verticalAlignment: TextInput.AlignVCenter
            color: root.textMain
            selectionColor: root.controlButtonOutline
            font.family: Appearance.fontFamily
            font.pixelSize: root.menuBodySize
            clip: true
            Text { renderType: Text.QtRendering;
                anchors.verticalCenter: parent.verticalCenter
                text: field.placeholder
                visible: !input.text.length && !input.activeFocus
                color: root.textDim
                font: input.font
            }
        }
    }

    component EventToggle: Rectangle {
        id: toggle
        property string label: ""
        property bool checked: false
        property bool keyboardFocused: false
        onKeyboardFocusedChanged: if (keyboardFocused) root.revealKeyboardMenuItem(this)
        signal activated()
        activeFocusOnTab: true
        height: 30
        radius: 6
        color: keyboardFocused ? root.controlButtonActive : (checked ? root.controlButtonActive : root.controlButtonSurface)
        border.width: 0
        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                toggle.activated()
                event.accepted = true
            }
        }
        Text { renderType: Text.QtRendering;
            anchors.left: parent.left
            anchors.leftMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            text: (toggle.checked ? "[✓] " : "[ ] ") + toggle.label
            color: toggle.checked ? root.textMain : root.textDim
            font.family: Appearance.fontFamily
            font.pixelSize: root.menuBodySize
            font.weight: Font.Normal
        }
        SelectionIndicator { visible: toggle.checked }
        BounceMouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: toggle.activated() }
    }

    component CreationChoice: Rectangle {
        id: choice
        property string title: ""
        property string description: ""
        property string iconName: "box"
        property bool selected: false
        property bool keyboardFocused: false
        onKeyboardFocusedChanged: if (keyboardFocused) root.revealKeyboardMenuItem(this)
        property bool interactive: true
        signal activated()
        radius: Appearance.menuActionRadius
        color: selected ? root.controlButtonActive : root.controlButtonSurface
        border.width: 0
        Accessible.role: interactive ? Accessible.RadioButton : Accessible.StaticText
        Accessible.name: description.length ? title + ". " + description : title
        Accessible.checked: selected
        Rectangle { x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter; width: Appearance.menuIconCircleSize; height: width; radius: width / 2; color: Qt.lighter(choice.color, 1.6)
            LucideIcon { anchors.centerIn: parent; width: Appearance.menuGlyphSize; height: width; name: choice.iconName }
        }
        Column {
            x: Appearance.menuLabelInset; width: parent.width - Appearance.menuLabelInset - 14 - (choice.interactive ? 14 : 0); anchors.verticalCenter: parent.verticalCenter; spacing: 4
            Text { renderType: Text.QtRendering; width: parent.width; text: choice.title; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; elide: Text.ElideRight }
            Text { renderType: Text.QtRendering; visible: choice.description.length > 0; width: parent.width; text: choice.description; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize; wrapMode: Text.WordWrap }
        }
        LucideIcon { visible: choice.selected; anchors.right: parent.right; anchors.rightMargin: 10; anchors.top: parent.top; anchors.topMargin: 10; width: 12; height: 12; name: "check" }
        BounceMouseArea { anchors.fill: parent; enabled: choice.interactive; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: choice.activated() }
    }

    component FeatureCard: Rectangle {
        id: featureCard
        property string label: ""
        property string detail: ""
        property string programs: ""
        property bool checked: false
        property bool keyboardFocused: false
        onKeyboardFocusedChanged: if (keyboardFocused) root.revealKeyboardMenuItem(this)
        property bool infoVisible: false
        signal activated()
        signal infoRequested()
        height: infoVisible ? 72 : 34
        radius: 7
        color: keyboardFocused ? root.controlButtonActive : ((checked ? root.controlButtonActive : root.controlButtonSurface))
        border.width: 0
        Rectangle {
            anchors.left: parent.left; anchors.leftMargin: 10; anchors.top: parent.top; anchors.topMargin: 8
            width: 18; height: 18; radius: 5
            color: featureCard.checked ? root.controlButtonActive : root.controlButtonSurface
            border.width: 1; border.color: "#52656d"
            Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: featureCard.checked ? "✓" : ""; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
        }
        Text { renderType: Text.QtRendering; anchors.left: parent.left; anchors.leftMargin: 36; anchors.right: parent.right; anchors.rightMargin: 10; anchors.top: parent.top; anchors.topMargin: 9; text: featureCard.label; color: featureCard.checked ? root.textMain : root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal; elide: Text.ElideRight }
        Text { renderType: Text.QtRendering; visible: featureCard.infoVisible; anchors.left: parent.left; anchors.leftMargin: 10; anchors.right: parent.right; anchors.rightMargin: 10; anchors.top: parent.top; anchors.topMargin: 31; text: featureCard.detail; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize; elide: Text.ElideRight }
        Text { renderType: Text.QtRendering; visible: featureCard.infoVisible; anchors.left: parent.left; anchors.leftMargin: 10; anchors.right: parent.right; anchors.rightMargin: 10; anchors.bottom: parent.bottom; anchors.bottomMargin: 8; text: featureCard.programs; color: featureCard.programs.indexOf("INSTALA") === 0 ? root.textMain : "#73929a"; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal; elide: Text.ElideRight }
        SelectionIndicator { visible: featureCard.checked }
        BounceMouseArea { id: featureMouse; anchors.fill: parent; acceptedButtons: Qt.LeftButton; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: featureCard.activated() }
        MouseArea { anchors.fill: parent; acceptedButtons: Qt.RightButton; cursorShape: Qt.WhatsThisCursor; onClicked: featureCard.infoRequested() }
    }

    // One background-layer surface per monitor. Rotation is Environment-local,
    // requires no extra daemon/package, and never reserves space or accepts
    // pointer/keyboard input.
    Timer {
        interval: 15 * 60 * 1000
        running: !Appearance.wallpaper.length
        repeat: true
        onTriggered: root.wallpaperIndex = (root.wallpaperIndex + 1) % root.wallpaperSources.length
    }

    Variants {
        model: Quickshell.screens

        PanelWindow {
            required property var modelData
            screen: modelData
            anchors { top: true; bottom: true; left: true; right: true }
            exclusionMode: ExclusionMode.Ignore
            exclusiveZone: 0
            focusable: false
            color: "#000000"
            mask: Region {}
            WlrLayershell.layer: WlrLayer.Background
            WlrLayershell.keyboardFocus: WlrKeyboardFocus.None

            Image {
                anchors.fill: parent
                source: root.currentWallpaper
                fillMode: Appearance.wallpaperFit === "fit" ? Image.PreserveAspectFit
                        : Appearance.wallpaperFit === "stretch" ? Image.Stretch : Image.PreserveAspectCrop
                scale: Appearance.wallpaperZoom / 100
                smooth: true
                mipmap: true
                asynchronous: false
                cache: true
            }
        }
    }

    Variants {
        id: barVariants
        model: Quickshell.screens
        PanelWindow {
        id: screenBar
        required property var modelData
        screen: modelData
        Component.onDestruction: {
            if (root.selectedBar === screenBar) {
                root.closePopup()
                root.selectedBar = null
            }
        }
        property alias calendarButton: calendarButton
        property alias environmentButton: environmentButton
        property alias batteryButton: batteryButton
        property alias mediaButton: mediaIsland
        readonly property real ghostWidth: ghostGreeting.width
        readonly property real workspaceWidth: workspaceStrip.width
        property alias appsButton: appsButton
        property alias filesButton: filesButton
        property alias controlCenterButton: controlCenterButton
        anchors { top: true; left: true; right: true }
        // Share outer edges with tiled application windows.
        margins { left: Appearance.desktopEdgeInset; right: Appearance.desktopEdgeInset }
        implicitHeight: 46
        exclusiveZone: 46
        color: "transparent"
        // Top panels are covered by fullscreen clients; Overlay is not.
        WlrLayershell.layer: popup.open || environmentAppsProcess.running ? WlrLayer.Overlay : WlrLayer.Top
        // APX shared launcher pointer focus: Hyprland hits only exclusive surfaces while Rofi owns focus.
        WlrLayershell.keyboardFocus: environmentAppsProcess.running ? WlrKeyboardFocus.Exclusive : WlrKeyboardFocus.None
        Shortcut {
            sequence: "Escape"
            enabled: environmentAppsProcess.running
            onActivated: environmentAppsProcess.running = false
        }

        Rectangle {
            anchors.fill: parent
            anchors.topMargin: 5
            anchors.bottomMargin: 5
            radius: 10
            color: "transparent"
            border.width: 0
            border.color: root.shellBorder

            MouseArea {
                anchors.fill: parent
                enabled: popup.open
                onClicked: root.closePopup()
            }

            Row {
                id: leftActions
                Rectangle {
                    parent: leftActions.parent
                    x: leftActions.x; y: leftActions.y; width: leftActions.width; height: leftActions.height
                    z: -1; radius: height / 2
                    color: Appearance.capsuleSurface
                    border.width: 1; border.color: "#304f566c"
                }
                anchors.left: parent.left
                anchors.leftMargin: 0
                anchors.verticalCenter: parent.verticalCenter
                spacing: 6
                BarButton {
                    id: calendarButton
                    outlineHost: screenBar.contentItem
                    grouped: true
                    hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === calendarButton : null
                    activeSurface: root.controlButtonHover
                    accentColor: root.textMain
                    textColor: root.textMain
                    label: root.clockText
                    iconName: "calendar-days"
                    alternateIconName: "calendar-search"
                    accessibleLabel: "Calendário, " + root.clockText
                    alternateLabel: calendarButton.label
                    alternateActive: root.bar === screenBar && popup.open && root.popupKind === "calendar"
                    animateActivation: root.animatedBarOpenKind === "calendar"
                    animateDeactivation: root.animatedBarCloseKind === "calendar"
                    onActivated: root.togglePopup("calendar", this, true)
                }
                WorkspaceStrip {
                    id: workspaceStrip
                    expanded: root.workspacesExpanded
                    onToggleRequested: root.workspacesExpanded = !root.workspacesExpanded
                    grouped: true
                    visible: !root.isHub
                    workspaces: root.openWorkspaces
                    barWindow: screenBar
                    wallpaper: root.currentWallpaper
                    surfaceColor: root.panel
                    activeColor: root.controlButtonActive
                    mainColor: root.textMain
                    dimColor: root.textDim
                    borderColor: root.shellBorder
                    menusOpen: popup.open || environmentAppsProcess.running
                    onActivated: root.closePopup()
                }
            }


            BarButton {
                id: environmentButton
                outlineHost: environmentButton.parent
                inactiveBorderWidth: 0
                    hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === environmentButton : null
                activeSurface: root.controlButtonHover
                accentColor: root.textMain
                textColor: root.textMain
                anchors.centerIn: parent
                // The button is a compact context label; actions live in the popup.
                label: root.environmentLabel
                iconName: root.activeEnvironmentIcon
                accessibleLabel: "Environment " + root.environmentLabel
                alternateLabel: environmentButton.label
                alternateActive: root.bar === screenBar && popup.open && root.popupKind === "environments"
                animateActivation: root.animatedBarOpenKind === "environments"
                animateDeactivation: root.animatedBarCloseKind === "environments"
                onActivated: {
                    root.environmentKeyboardFocus = false
                    root.togglePopup("environments", this, true)
                }
            }

            Row {
                id: rightActions
                readonly property real fixedWidth: [microphoneButton, appsButton, filesButton, batteryButton, controlCenterButton].filter(function(item) { return item.visible }).reduce(function(total, item) { return total + item.width + rightActions.spacing }, 0)
            MediaIsland {
                id: mediaIsland
                outlineHost: mediaIsland.parent
                hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === mediaIsland : null
                parent: rightActions.parent
                grouped: false
                // Reveal a separate capsule outward from the central Environment pill.
                x: environmentButton.x + environmentButton.width / 2 + (environmentButton.width / 2 + 8) * presence
                y: environmentButton.y
                z: -0.5
                // APX transient island v2: resize in one curve, then restore the media title.
                readonly property real availableWidth: Math.max(0, rightActions.x - (environmentButton.x + environmentButton.width) - 16)
                width: Math.min(showingTransient ? 88 : (selected ? 36 : 220), availableWidth) * presence
                Behavior on width { enabled: mediaIsland.presence === 1; NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }
                visible: (!root.isHub || showingTransient) && (showingTransient || width > 1) && (showingTransient || availableWidth >= (selected ? 36 : 90))
                cameraUsage: root.cameraActive && !root.focusedFullscreen && !root.hotkeyOsdVisible
                transientActive: (root.hotkeyOsdVisible || cameraUsage) && root.bar === screenBar && !root.fullscreenOsd
                transientIcon: root.hotkeyOsdIcon
                transientTitle: cameraUsage ? "Câmara" : root.hotkeyOsdTitle
                transientDetail: cameraUsage ? "Em utilização" : root.hotkeyOsdDetail
                transientProgress: cameraUsage ? -1 : root.hotkeyOsdProgress
                selected: root.bar === screenBar && popup.open && root.popupKind === "media" && !root.popupClosing
                onActivated: {
                    DesktopActivity.refresh()
                    root.togglePopup("media", mediaIsland, true)
                }
            }

                Rectangle {
                    parent: rightActions.parent
                    x: rightActions.x; y: rightActions.y
                    width: rightActions.width; height: rightActions.height
                    z: -1; radius: height / 2
                    color: Appearance.capsuleSurface
                    border.width: 1; border.color: "#304f566c"
                }
                anchors.right: parent.right
                anchors.rightMargin: 0
                anchors.verticalCenter: parent.verticalCenter
                spacing: 6
                BarButton {
                activeSurface: root.controlButtonHover
                    accentColor: root.textMain
                    textColor: root.textMain
                    id: microphoneButton
                    outlineHost: screenBar.contentItem
                    grouped: true
                    visible: root.microphoneActive
                    label: "Microfone"
                    iconName: "mic"
                }
                BarButton {
                    grouped: true
                    id: appsButton
                    outlineHost: screenBar.contentItem
                    visible: !root.isHub
                    hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === appsButton : null
                    activeSurface: root.controlButtonHover
                    accentColor: root.textMain
                    textColor: root.textMain
                    label: ""
                    iconName: root.appsIconName
                    alternateIconName: "layout-panel-left"
                    accessibleLabel: "Aplicações"
                    alternateLabel: appsButton.label
                    alternateActive: environmentAppsProcess.running
                    onActivated: root.toggleApplicationLauncher()
                }
                BarButton {
                    grouped: true
                    id: filesButton
                    outlineHost: screenBar.contentItem
                    visible: !root.isHub
                    hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === filesButton : null
                    activeSurface: root.controlButtonHover
                    accentColor: root.textMain
                    textColor: root.textMain
                    iconName: "folder"
                    alternateIconName: "folder-open"
                    accessibleLabel: "Abrir gestor de ficheiros"
                    alternateActive: root.filesOpen
                    alternateLabel: filesButton.label
                    onActivated: {
                        root.closePopup()
                        if (environmentAppsProcess.running) environmentAppsProcess.running = false
                        if (!fileShortcutProcess.running) fileShortcutProcess.running = true
                    }
                }
                BarButton {
                    grouped: true
                    id: batteryButton
                    outlineHost: screenBar.contentItem
                    scale: (animateActivation || animateDeactivation) ? 0.92 : 1
                    hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === batteryButton : null
                activeSurface: root.controlButtonHover
                    accentColor: root.textMain
                    textColor: root.textMain
                    label: root.batteryText
                    iconName: root.batteryIconName
                    accessibleLabel: "Bateria " + root.batteryText + ", " + root.batteryStatus
                    alternateLabel: batteryButton.label
                    alternateActive: root.bar === screenBar && popup.open && root.popupKind === "battery"
                    animateActivation: root.animatedBarOpenKind === "battery"
                    animateDeactivation: root.animatedBarCloseKind === "battery"
                    onActivated: root.togglePopup("battery", this, true)
                }
                Item {
                    // Keep the greeting and its trailing gap in one continuous layout slot.
                    width: ghostGreeting.width + controlCenterButton.width
                    height: 32
                Item {
                    id: ghostGreeting
                    readonly property real budget: Math.max(0, rightActions.parent.width - (environmentButton.x + environmentButton.width) - rightActions.fixedWidth - 34)
                    property real reveal: root.ghostGreetingVisible ? 1 : 0
                    width: Math.min(ghostBarText.implicitWidth + 22, budget) * reveal
                    height: 32
                    visible: reveal > 0
                    clip: true
                    opacity: reveal
                    Behavior on reveal { NumberAnimation { duration: 320; easing.type: Easing.InOutCubic } }
                    Accessible.role: Accessible.StaticText
                    Accessible.name: "Gosty: " + root.ghostMessage
                    Item {
                        id: ghostViewport
                        x: 8; width: ghostBarText.implicitWidth; height: parent.height; clip: false
                        Text { renderType: Text.QtRendering;
                            id: ghostBarText
                            text: root.ghostMessage; textFormat: Text.PlainText
                            color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: 12
                            anchors.verticalCenter: parent.verticalCenter
                            x: 0
                        }
                    }
                }
                BarButton {
                    grouped: true
                    id: controlCenterButton
                    outlineHost: screenBar.contentItem
                    scale: (animateActivation || animateDeactivation) ? 0.92 : 1
                    x: ghostGreeting.width
                    compactSymbol: false
                    hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === controlCenterButton : null
                    activeSurface: root.controlButtonHover
                    accentColor: root.textMain
                    textColor: root.textMain
                    label: ""
                    alternateLabel: ""
                    iconName: "hexagon"
                    alternateIconName: "ghost"
                    accessibleLabel: "Central de Controlo"
                    alternateActive: root.bar === screenBar && popup.open && root.popupKind === "controls"
                    animateActivation: root.animatedBarOpenKind === "controls"
                    animateDeactivation: root.animatedBarCloseKind === "controls"
                    onActivated: root.togglePopup("controls", this, true)
                }
                }
            }
        }
    }
    }

    PanelWindow {
        id: hotkeyOsdWindow
        screen: root.bar ? root.bar.screen : null
        visible: root.hotkeyOsdVisible && root.fullscreenOsd
        anchors { bottom: true }
        margins { bottom: 72 }
        implicitWidth: 286
        implicitHeight: 132
        exclusiveZone: 0
        aboveWindows: true
        focusable: false
        color: "transparent"
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None

        Rectangle {
            anchors.fill: parent
            opacity: root.hotkeyOsdOpacity
            radius: 22
            color: "#dc10181e"
            border.width: 1
            border.color: root.shellBorder

            Behavior on opacity { NumberAnimation { duration: 160; easing.type: Easing.OutCubic } }

            ControlIcon {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 15
                width: 38
                height: 38
                source: root.hotkeyOsdIcon
                tint: Appearance.iconColor
            }

            Text { renderType: Text.QtRendering;
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 57
                text: root.hotkeyOsdTitle
                color: root.textMain
                font.family: Appearance.fontFamily
                font.pixelSize: 14
                font.bold: true
            }

            Text { renderType: Text.QtRendering;
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 80
                text: root.hotkeyOsdDetail
                color: root.textDim
                font.family: Appearance.fontFamily
                font.pixelSize: Appearance.bodySize
            }

            Rectangle {
                visible: root.hotkeyOsdProgress >= 0
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.leftMargin: 24
                anchors.rightMargin: 24
                anchors.bottomMargin: 14
                height: 5
                radius: 3
                color: "#394b53"

                Rectangle {
                    width: parent.width * Math.max(0, Math.min(100, root.hotkeyOsdProgress)) / 100
                    height: parent.height
                    radius: 3
                    color: root.textMain
                    Behavior on width { NumberAnimation { duration: 90; easing.type: Easing.OutCubic } }
                }
            }
        }
    }

    Variants {
        id: transitionVariants
        model: Quickshell.screens
        PanelWindow {
        required property var modelData
        screen: modelData
        id: environmentTransitionOverlay
        Connections {
            target: environmentTransitionOverlay.contentItem.Window.window
            function onFrameSwapped() {
                if (root.environmentSwitchPending && !root.environmentSwitchDispatched) {
                    root.environmentSwitchDispatched = true
                    environmentSwitchProcess.running = true
                }
            }
        }
        visible: root.environmentSwitchPending || root.startupCover || root.powerTransitionActive
        exclusionMode: ExclusionMode.Ignore
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive
        anchors { top: true; bottom: true; left: true; right: true }
        WlrLayershell.layer: WlrLayer.Overlay
        exclusiveZone: 0
        color: "#000000"

        MouseArea { anchors.fill: parent; cursorShape: Qt.BlankCursor; acceptedButtons: Qt.AllButtons }
        Text { renderType: Text.QtRendering;
            visible: root.powerTransitionActive
            anchors.centerIn: parent
            text: root.powerAction === "reboot" ? "A reiniciar…" : "A encerrar…"
            color: "#ffffff"; font.family: Appearance.fontFamily; font.pixelSize: 24
        }
    }
    }

    Connections {
        target: popupBackground.Window.window
        // Wait for glyphs, icons and layout to render before starting the reveal.
        function onFrameSwapped() {
            if (root.menuFrameProbeEnabled && popup.open
                    && (root.popupAnimationPending || popupOpenAnimation.running || popupCloseAnimation.running || controlPageAnimation.running))
                root.menuFrameSamples.push({time: Date.now(), kind: root.popupKind, progress: root.islandProgress, contentWidth: menuFlick.width, targetHeight: popupBackground.targetHeight, reads: root.dynamicReadMetrics})
            if (!popup.open || !root.popupAnimationPending) return
            root.popupAnimationPending = false
            popupOpenAnimation.restart()
        }
    }

    // Keep this layer mapped for the lifetime of QuickShell. Hyprland can drop
    // pointer focus when a click maps a second layer surface, which consumes
    // the next stationary click. The zero-sized mask makes the already-mapped
    // layer input-transparent while the menu is closed.
    Variants {
        model: Quickshell.screens
        PanelWindow {
        id: popupDismissLayer
        required property var modelData
        screen: modelData
        visible: true
        anchors { left: true; right: true; bottom: true }
        implicitHeight: screen ? Math.max(0, screen.height - (root.bar && screen === root.bar.screen ? 46 : 0)) : 0
        exclusionMode: ExclusionMode.Ignore
        exclusiveZone: 0
        focusable: false
        color: "transparent"
        mask: Region { item: dismissInputRegion }
        WlrLayershell.layer: root.bar && screen === root.bar.screen ? WlrLayer.Top : WlrLayer.Overlay
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None

        Item {
            id: dismissInputRegion
            width: popup.open ? parent.width : 0
            height: popup.open ? parent.height : 0
        }

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.AllButtons
            onClicked: root.closePopup()
        }
    }

    }

    // Exclusive keyboard input closes menus reliably with Escape.
    // Outside clicks on this monitor use the full-screen popup input mask.
    HyprlandFocusGrab {
        id: popupFocusGrab
        windows: root.bar ? [popup, root.bar] : [popup]
        active: false // The full-screen input mask handles outside clicks.
        onCleared: root.closePopup()
    }

    PanelWindow {
        id: popup
        screen: root.bar ? root.bar.screen : null
        property bool open: false
        anchors { top: true; bottom: true; left: true; right: true }
        exclusionMode: ExclusionMode.Ignore
        exclusiveZone: 0
        // The window itself never unmaps. Only its visual and input mask open,
        // so the bar keeps the compositor's pointer focus after activation.
        visible: true
        // keyboardFocus owns interactivity. focusable would overwrite Exclusive
        // with OnDemand when the popup opens.
        mask: Region { item: popupInputRegion }
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.keyboardFocus: open
                                     ? WlrKeyboardFocus.Exclusive
                                     : WlrKeyboardFocus.None
        property real menuWidth: root.popupKind === "calendar" ? 440
                                                     : (root.popupKind === "environments" ? 460
                                                        : (root.popupKind === "controls" ? 340 * root.controlCenterScale : (root.popupKind === "battery" || root.popupKind === "media" ? 340 : 300)))
        property real menuHeight: root.popupKind === "calendar"
                        ? (root.calendarEditor ? 500
                           : (root.calendarView === "day"
                              ? 205 + Math.min(4, root.eventsForDate(root.calendarDate).length) * 50
                              : 410 + Math.min(4, root.eventsForDate(root.calendarDate).length) * 44))
                                                       : (root.popupKind === "controls"
                                                          ? (root.renderedControls.shortcutsOpen ? Math.min(620, popup.height - 74) * root.controlCenterScale
                                                             : root.renderedControls.controlsMoreOpen ? (root.renderedControls.controlsAppearanceOpen ? Math.min(popup.height - 74, menuContent.implicitHeight + (popupBackground.splitControls ? 0 : 20)) : 340) * root.controlCenterScale
                                                             : root.renderedControlsAllClosed() ? Math.min(popup.height - 74, menuContent.implicitHeight + (popupBackground.splitControls ? 0 : 20)) * root.controlCenterScale
                                                             : ((root.renderedControls.controlsBrightnessOpen || root.renderedControls.controlsAudioOpen || root.renderedControls.controlsMicrophoneOpen) ? Math.max(232, menuContent.implicitHeight + (popupBackground.splitControls ? 0 : 20))
                                                                : (root.renderedControls.controlsBluetoothOpen ? 320 : 480)) * root.controlCenterScale)
                                                          : (root.popupKind === "media" ? Math.min(popup.height - 74, menuContent.implicitHeight + (popupBackground.splitControls ? 0 : 20)) : (root.popupKind === "environments" ? root.environmentPopupHeight : (root.popupKind === "battery" ? 650 : 440))))
        color: "transparent"
        // A layer-shell surface can accept both pointer and keyboard input
        // even when opened by an IPC shortcut, which avoids the xdg_popup
        // input-serial limitation of PopupWindow.

        Shortcut {
            sequence: "Escape"
            enabled: popup.open
            onActivated: {
                if (root.editingMenuSlider) root.editingMenuSlider = null
                else if (root.wifiPasswordVisible)
                    root.cancelWifiPassword()
                else if (root.popupKind === "calendar" && root.calendarEditor)
                    root.cancelCalendarEditor()
                else
                    root.closePopup()
            }
        }

        Item {
            id: popupInputRegion
            width: popup.open ? parent.width : 0
            height: popup.open ? parent.height : 0
        }

        // The exclusive popup receives clicks over the bar too. Dispatch the
        // existing button action on a completed click without closing first.
        MouseArea {
            id: popupBarPointer
            anchors.fill: parent
            enabled: popup.open
            acceptedButtons: Qt.AllButtons
            hoverEnabled: true
            property var pressedBarTarget: null
            readonly property var hoveredBarTarget: popup.open && containsMouse
                                                    ? root.popupBarTargetAt(mouseX, mouseY) : null
            cursorShape: hoveredBarTarget ? Qt.PointingHandCursor : Qt.ArrowCursor
            onPressed: (mouse) => { pressedBarTarget = root.popupBarTargetAt(mouse.x, mouse.y) }
            onCanceled: pressedBarTarget = null
            onPositionChanged: {
                if (containsMouse && root.popupClosing && root.popupKind === "media" && root.mediaButton
                        && root.popupBarTargetAt(mouseX, mouseY) !== root.mediaButton)
                    root.mediaButton.endHoverHandoff()
            }
            onClicked: (mouse) => {
                var target = root.popupBarTargetAt(mouse.x, mouse.y)
                if (mouse.button === Qt.LeftButton && target && target === pressedBarTarget)
                    target.activated()
                else
                    root.closePopup()
                pressedBarTarget = null
            }
        }

        MouseArea {
            id: controlTransitionShield
            z: 3
            x: Math.min(popupBackground.x, root.outgoingPageRect.x)
            y: Math.min(popupBackground.y, root.outgoingPageRect.y)
            width: Math.max(popupBackground.width, root.outgoingPageRect.width) + 56
            height: Math.max(popupBackground.height, root.outgoingPageRect.height)
            visible: enabled
            enabled: popup.open && root.popupKind === "controls" && root.controlPageCapturing
            acceptedButtons: Qt.AllButtons
            hoverEnabled: true
            onWheel: (wheel) => { wheel.accepted = true }
        }

        Image {
            id: outgoingControlPage
            z: 2
            visible: root.controlPageCapture !== null && root.controlPageBlend < 1
            source: root.controlPageCapture ? root.controlPageCapture.url : ""
            x: root.outgoingPageRect.x - root.controlPageDirection * 18 * root.controlPageMotion
            y: root.outgoingPageRect.y
            width: root.outgoingPageRect.width; height: root.outgoingPageRect.height
            opacity: 1 - root.controlPageBlend
            smooth: true
        }

        Rectangle {
            id: popupClipMask
            width: popupBackground.width
            height: popupBackground.height
            radius: popupBackground.radius
            color: "white"
            visible: false
            layer.enabled: popup.open
            layer.textureSize: popupBackground.stableTextureSize
        }

        Rectangle {
            id: popupBackground
            readonly property real renderScale: Window.window && Window.window.devicePixelRatio > 0
                ? Window.window.devicePixelRatio : (Screen.devicePixelRatio > 0 ? Screen.devicePixelRatio : 1)
            // Round buffers upward for fractional scales; geometry still uses the actual DPR.
            readonly property real textureScale: Math.ceil(renderScale)
            // Allocate once at the final size; growing GPU targets every frame stalls the reveal.
            readonly property size stableTextureSize: Qt.size(
                Math.ceil(Math.max(root.islandOrigin.width, targetWidth) * textureScale),
                Math.ceil(Math.max(root.islandOrigin.height, viewportHeight, targetHeight) * textureScale))
            visible: popup.open
            property real targetWidth: Math.min(popup.menuWidth, popup.width - 16)
            Behavior on targetWidth { enabled: root.popupKind !== "controls" && popup.open && root.islandProgress > .99 && !root.popupClosing; NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }
            readonly property real contentInset: splitControls ? 0 : (root.popupKind === "controls" ? 8 : 10)
            readonly property real contentBottomInset: splitControls ? 0 : (root.popupKind === "controls" ? 8 : 12)
            readonly property Item scrollingHeader: root.popupKind === "calendar"
                ? (root.calendarEditor ? calendarEditorHeader : calendarMenuHeader) : scrollingMenuHeader
            readonly property bool headerScrolledOut: scrollingHeader && scrollingHeader.visible
                && menuFlick.contentY >= scrollingHeader.mapToItem(menuFlick.contentItem, 0, 0).y + scrollingHeader.height
            readonly property real viewportTargetHeight: Math.min(
                Math.max(0, popup.height - Appearance.menuTop - 10),
                Appearance.menuMaxHeight,
                menuContent.implicitHeight + contentInset + contentBottomInset)
            // Scrolling uses a stable viewport; only its visible frame fits to whole cards.
            // Feeding the fitted frame back into Flickable would repeatedly shrink it.
            property real viewportHeight: viewportTargetHeight
            Behavior on viewportHeight { enabled: root.popupKind !== "controls" && root.islandProgress > .99 && !root.popupClosing && !(root.popupKind === "media" && mediaMenu.mediaTransitionRunning); NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
            readonly property real targetHeight: root.menuHeightForCompleteActions(viewportHeight)
            readonly property real settledHeight: targetHeight
            property real settledX: Math.max(Appearance.desktopEdgeInset, Math.min(root.popupLeftMargin, popup.width - targetWidth - Appearance.desktopEdgeInset))
            Behavior on settledX { enabled: root.popupKind !== "controls" && popup.open && root.islandProgress > .99 && !root.popupClosing; NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }
            readonly property bool alignPhysicalPixels: root.islandProgress === 1 && !root.popupClosing
                && !root.controlPageCapturing && !controlPageAnimation.running
            readonly property real animatedX: root.islandOrigin.x + (settledX - root.islandOrigin.x) * root.islandProgress
            x: alignPhysicalPixels ? Math.round(animatedX * renderScale) / renderScale : animatedX
            property real settledY: Appearance.menuTop
            Behavior on settledY { enabled: root.popupKind !== "controls" && popup.open && root.islandProgress > .99 && !root.popupClosing; NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }
            readonly property real animatedY: root.islandOrigin.y + (settledY - root.islandOrigin.y) * root.islandProgress
            y: alignPhysicalPixels ? Math.round(animatedY * renderScale) / renderScale : animatedY
            width: root.islandOrigin.width + (targetWidth - root.islandOrigin.width) * root.islandProgress
            height: root.islandOrigin.height + (settledHeight - root.islandOrigin.height) * root.islandProgress
            Keys.onPressed: function(event) { root.navigateGenericMenu(event) }
            // All menus emerge from their trigger using the Calendar geometry animation.
            scale: 1
            opacity: Math.min(1, root.islandProgress * 5)
            transformOrigin: Item.TopLeft
            clip: true
            // Rectangle.clip is rectangular: mask every scrolling child to one contour.
            layer.enabled: popup.open
            layer.textureSize: popupBackground.stableTextureSize
            layer.effect: MultiEffect {
                autoPaddingEnabled: false
                maskEnabled: true
                maskSource: popupClipMask
            }
            radius: Math.min(height / 2, Appearance.desktopCornerRadius)
            readonly property bool splitControls: root.popupKind === "controls" && root.renderedControlsAllClosed() && !root.renderedControls.controlsMoreOpen && !root.renderedControls.shortcutsOpen && !root.renderedControls.powerConfirmOpen
            color: splitControls ? "transparent" : root.popupPanel
            Behavior on color { enabled: root.popupKind !== "controls"; ColorAnimation { id: panelMaterialFade; duration: 180; easing.type: Easing.OutCubic } }
            border.width: 0
            border.color: root.shellBorder

            NumberAnimation {
                id: popupOpenAnimation
                target: root; property: "islandProgress"; to: 1
                duration: 300; easing.type: Easing.OutCubic
                onFinished: root.flushEnvironmentCatalog()
            }
            NumberAnimation {
                id: popupCloseAnimation
                target: root; property: "islandProgress"; to: 0
                duration: root.pendingPopupRequest ? 140 : (root.popupKind === "controls" ? 300 : 240)
                easing.type: root.popupKind === "controls" && !root.pendingPopupRequest ? Easing.InOutCubic : Easing.OutCubic
                onFinished: if (root.popupClosing) root.finishClosePopup()
            }
            NumberAnimation {
                id: islandContentAnimation
                target: root; property: "islandContentOpacity"; to: 1
                duration: 200; easing.type: Easing.OutCubic
            }

            // Blank space inside the card must not fall through to dismissal.
            MouseArea { anchors.fill: parent; acceptedButtons: Qt.AllButtons }

            HoverHandler {
                id: popupHover
            }

            Rectangle {
                id: stickyMenuHeader
                x: 1
                y: 1
                width: Math.max(0, popupBackground.width - 2)
                height: popupBackground.contentInset + 34
                clip: false
                z: 2
                property real revealProgress: popup.open && popupBackground.headerScrolledOut ? 1 : 0
                Behavior on revealProgress {
                    id: titleRevealBehavior
                    enabled: popup.open
                    NumberAnimation {
                        duration: titleRevealBehavior.targetValue > 0 ? 420 : 240
                        easing.type: titleRevealBehavior.targetValue > 0 ? Easing.InOutSine : Easing.InOutQuad
                    }
                }
                visible: popup.open && (popupBackground.headerScrolledOut || revealProgress > 0)
                // Keep the backdrop steady on entrance; animate only the text.
                readonly property color backdropColor: root.popupPanel
                readonly property real backdropStrength: popupBackground.headerScrolledOut ? 1 : revealProgress
                function smoke(alpha) {
                    return Qt.rgba(backdropColor.r, backdropColor.g, backdropColor.b, alpha * backdropStrength)
                }
                color: "transparent"
                opacity: menuFlick.opacity
                Rectangle {
                    id: stickyTitleBackdrop
                    width: parent.width
                    height: parent.height + 18
                    radius: Math.max(0, popupBackground.radius - 1)
                    gradient: Gradient {
                        orientation: Gradient.Vertical
                        GradientStop { position: 0; color: stickyMenuHeader.smoke(1) }
                        GradientStop { position: Math.min(0.25, 8 / stickyTitleBackdrop.height); color: stickyMenuHeader.smoke(1) }
                        GradientStop { position: 0.75; color: stickyMenuHeader.smoke(0.75) }
                        GradientStop { position: 1; color: stickyMenuHeader.smoke(0) }
                    }
                }
                // The title owns clicks; wheel events continue to the scrolling content.
                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.AllButtons
                    onWheel: event => event.accepted = false
                }
                Text { renderType: Text.QtRendering;
                    id: stickyTitleText
                    opacity: stickyMenuHeader.revealProgress
                    anchors.fill: parent
                    anchors.topMargin: Math.max(0, popupBackground.contentInset - 1)
                    anchors.leftMargin: popupBackground.contentInset + Appearance.menuTitleInset
                    anchors.rightMargin: popupBackground.contentInset
                    anchors.bottomMargin: 5
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    text: popupBackground.scrollingHeader ? popupBackground.scrollingHeader.title : ""
                    color: root.textMain
                    font.family: Appearance.fontFamily
                    font.pixelSize: root.menuTitleSize
                    font.weight: Font.DemiBold
                    elide: Text.ElideRight
                }
            }

            // Content stays behind the translucent title; only the outer viewport clips it.
            Item {
                id: menuScrollClip
                x: popupBackground.contentInset
                y: popupBackground.contentInset
                width: menuFlick.width
                height: menuFlick.height
                clip: true

            Flickable {
                id: menuFlick
                readonly property real headerInset: stickyMenuHeader.visible ? stickyMenuHeader.y + stickyMenuHeader.height - popupBackground.contentInset : 0
                x: 0
                y: 0
                // Lay out text and lists once at their destination width. The
                // animated outer card clips the reveal without reflowing every frame.
                width: Math.max(0, popupBackground.targetWidth - popupBackground.contentInset * 2)
                height: Math.max(0, root.islandOrigin.height + (popupBackground.viewportHeight - root.islandOrigin.height) * root.islandProgress - popupBackground.contentInset - popupBackground.contentBottomInset)
                opacity: Math.max(0, (root.islandProgress - .3) / .7) * (root.popupKind === "media" ? 1 : root.islandContentOpacity) * (root.popupKind === "controls" ? root.controlPageProgress : 1)
                enabled: !root.popupClosing && root.islandProgress > .8
                contentWidth: width
                contentHeight: menuContent.implicitHeight
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                flickableDirection: Flickable.VerticalFlick
                pixelAligned: true
                // Retarget one continuous animation instead of stopping/restarting
                // Flickable on every event and injecting a delayed second impulse.
                property real wheelPosition: 0
                property real wheelDestination: 0
                property bool wheelAnimating: false
                onWheelPositionChanged: if (wheelAnimating) contentY = wheelPosition
                function stopWheel() {
                    wheelAnimating = false
                    menuWheelAnimation.stop()
                    cancelFlick()
                }
                function scrollWheel(delta) {
                    if (!delta) return
                    cancelFlick()
                    if (!menuWheelAnimation.running) {
                        wheelAnimating = false
                        wheelPosition = contentY
                        wheelDestination = contentY
                    }
                    wheelDestination = Math.max(0, Math.min(Math.max(0, contentHeight - height), wheelDestination - delta * 2.5))
                    wheelAnimating = true
                    wheelPosition = wheelDestination
                }
                onEnabledChanged: if (!enabled) stopWheel()
                onContentHeightChanged: { stopWheel(); menuViewportGuardInstall.restart() }
                onDraggingChanged: if (dragging) stopWheel()
                Behavior on wheelPosition {
                    enabled: menuFlick.wheelAnimating
                    SmoothedAnimation {
                        id: menuWheelAnimation
                        velocity: -1; duration: 160; maximumEasingTime: 80
                        reversingMode: SmoothedAnimation.Immediate
                    }
                }
                WheelHandler {
                    target: null
                    acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                    onWheel: event => {
                        var delta = event.pixelDelta.y || event.angleDelta.y / 120 * 48
                        menuFlick.scrollWheel(delta)
                        event.accepted = true
                    }
                }
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOff }

                Column {
                    id: menuContent
                    width: parent.width
                    spacing: root.popupKind === "controls" ? 8 : 5
                    transform: Translate { x: root.popupKind === "controls" ? root.controlPageOffset : 0 }

                    Column {
                        id: calendarMenu
                        width: parent.width
                        spacing: 8
                        visible: root.popupKind === "calendar" && !root.calendarEditor
                        focus: visible
                        Keys.onPressed: function(event) { root.handleCalendarKey(event) }

                        MenuHeader { id: calendarMenuHeader; title: "Calendário" }

                        Row {
                            width: parent.width
                            spacing: 4
                            Rectangle {
                                    width: Appearance.calendarActionHeight; height: Appearance.calendarActionHeight; radius: 8
                                    color: root.calendarActionIsFocused("previous", "previous") ? root.controlButtonActive : (root.controlButtonSurface)
                                    readonly property bool menuScrollFocused: root.calendarActionIsFocused("previous", "previous")
                                    onMenuScrollFocusedChanged: if (menuScrollFocused) root.revealKeyboardMenuItem(this)
                                    border.width: root.calendarActionIsFocused("previous", "previous") ? 1 : 0; border.color: "#ffffff"
                                Text { renderType: Text.QtRendering; font.family: Appearance.fontFamily; anchors.centerIn: parent; text: "‹"; color: root.textMain; font.pixelSize: 22 }
                                BounceMouseArea { id: previousMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.moveCalendar(-1) }
                            }
                            Text { renderType: Text.QtRendering;
                                width: parent.width - Appearance.calendarActionHeight * 2 - 8; height: Appearance.calendarActionHeight; text: root.calendarTitle(); color: root.textMain
                                horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                                font.family: Appearance.fontFamily; font.pixelSize: root.menuTitleSize; font.weight: Font.DemiBold
                            }
                            Rectangle {
                                    width: Appearance.calendarActionHeight; height: Appearance.calendarActionHeight; radius: 8
                                    color: root.calendarActionIsFocused("next", "next") ? root.controlButtonActive : (root.controlButtonSurface)
                                    readonly property bool menuScrollFocused: root.calendarActionIsFocused("next", "next")
                                    onMenuScrollFocusedChanged: if (menuScrollFocused) root.revealKeyboardMenuItem(this)
                                    border.width: root.calendarActionIsFocused("next", "next") ? 1 : 0; border.color: "#ffffff"
                                Text { renderType: Text.QtRendering; font.family: Appearance.fontFamily; anchors.centerIn: parent; text: "›"; color: root.textMain; font.pixelSize: 22 }
                                BounceMouseArea { id: nextMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.moveCalendar(1) }
                            }
                        }

                        Row {
                            width: parent.width
                            spacing: 5
                            Repeater {
                                model: [{ key: "day", label: "Dia" }, { key: "month", label: "Mês" }, { key: "year", label: "Ano" }]
                                Rectangle {
                                    required property var modelData
                                    width: (menuContent.width - 10) / 3; height: Appearance.calendarActionHeight; radius: 8
                                    color: root.calendarActionIsFocused("view", modelData.key) ? root.controlButtonActive : (root.calendarView === modelData.key ? root.controlButtonActive : root.controlButtonSurface)
                                    readonly property bool menuScrollFocused: root.calendarActionIsFocused("view", modelData.key)
                                    onMenuScrollFocusedChanged: if (menuScrollFocused) root.revealKeyboardMenuItem(this)
                                    border.width: root.calendarActionIsFocused("view", modelData.key) ? 1 : 0
                                    border.color: "#ffffff"
                                    Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: modelData.label; color: root.calendarView === modelData.key ? root.textMain : root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                    BounceMouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.changeCalendarView(modelData.key) }
                                }
                            }
                        }

                        Column {
                            width: parent.width; spacing: 8
                            opacity: root.calendarPageOpacity
                            transform: Translate { x: root.calendarPageOffset }
                        Rectangle {
                            id: calendarMonthDaysSurface
                            width: parent.width
                            height: visible ? calendarMonthGrid.implicitHeight + 12 : 0
                            visible: root.calendarView === "month"
                            radius: 14
                            color: root.controlButtonSurface
                            border.width: 0
                            border.color: root.controlButtonOutline

                            Grid {
                                id: calendarMonthGrid
                                anchors.fill: parent
                                anchors.margins: 6
                                columns: 7; rowSpacing: 1; columnSpacing: 3
                                Repeater {
                                    model: root.weekNames
                                    Text { renderType: Text.QtRendering;
                                        required property string modelData
                                        width: (calendarMonthGrid.width - 18) / 7; height: 18; text: modelData
                                        color: root.textDim; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                                        font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                                    }
                                }
                                Repeater {
                                    model: root.monthDays()
                                    Rectangle {
                                        required property var modelData
                                        property bool today: modelData !== null && root.sameDay(modelData, root.currentDate)
                                        property bool selected: modelData !== null && root.dateKey(modelData) === root.calendarSelectedDateKey
                                        width: (calendarMonthGrid.width - 18) / 7; height: Appearance.calendarDayHeight; radius: 8
                                        color: modelData !== null && root.calendarActionIsFocused("date", root.dateKey(modelData)) ? root.controlButtonActive : (selected ? root.controlButtonActive : ("transparent"))
                                        readonly property bool menuScrollFocused: modelData !== null && root.calendarActionIsFocused("date", root.dateKey(modelData))
                                        onMenuScrollFocusedChanged: if (menuScrollFocused) root.revealKeyboardMenuItem(this)
                                        SelectionIndicator { visible: parent.selected; color: "#ffffff" }
                                        border.width: selected || (modelData !== null && root.calendarActionIsFocused("date", root.dateKey(modelData))) ? 1 : 0
                                        border.color: "#ffffff"
                                        Rectangle {
                                            visible: parent.today && !parent.selected && !root.calendarActionIsFocused("date", root.dateKey(modelData))
                                            anchors.fill: parent; anchors.margins: parent.selected ? 4 : 2
                                            radius: 4; color: "transparent"
                                            border.width: 1; border.color: "#ffb15a"
                                        }
                                        Text { renderType: Text.QtRendering;
                                            anchors.centerIn: parent
                                            text: modelData === null ? "" : modelData.getDate()
                                            color: parent.selected ? root.textMain : (parent.today ? "#ffc36b" : root.textMain)
                                            font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                            font.weight: Font.Normal
                                        }
                                        Rectangle {
                                            visible: modelData !== null && root.eventsForDate(modelData).length > 0
                                            anchors.bottom: parent.bottom; anchors.bottomMargin: 3; anchors.horizontalCenter: parent.horizontalCenter
                                            width: 4; height: 4; radius: 2; color: root.textMain
                                        }
                                        BounceMouseArea {
                                            id: dayMouse; anchors.fill: parent; enabled: modelData !== null; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                            onClicked: root.selectCalendarDate(modelData)
                                        }
                                    }
                                }
                            }
                        }

                        Grid {
                            width: parent.width; columns: 3; rowSpacing: 4; columnSpacing: 4
                            visible: root.calendarView === "year"
                            Repeater {
                                model: root.monthNames
                                Rectangle {
                                    required property string modelData
                                    required property int index
                                    property bool currentMonth: index === root.currentDate.getMonth() && root.calendarDate.getFullYear() === root.currentDate.getFullYear()
                                    width: (menuContent.width - 8) / 3; height: Appearance.calendarActionHeight; radius: 8
                                    color: root.calendarActionIsFocused("month", index) ? root.controlButtonActive : (currentMonth ? root.controlButtonActive : (root.controlButtonSurface))
                                    readonly property bool menuScrollFocused: root.calendarActionIsFocused("month", index)
                                    onMenuScrollFocusedChanged: if (menuScrollFocused) root.revealKeyboardMenuItem(this)
                                    border.width: root.calendarActionIsFocused("month", index) ? 1 : 0
                                    border.color: "#ffffff"
                                    Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: modelData.slice(0, 3); color: parent.currentMonth ? root.textMain : root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                    BounceMouseArea {
                                        id: monthMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                        onClicked: root.changeCalendarView("month", new Date(root.calendarDate.getFullYear(), index, 1))
                                    }
                                }
                            }
                        }

                        Column {
                            width: parent.width
                            spacing: 6
                            visible: root.calendarView === "day"

                            Text { renderType: Text.QtRendering;
                                visible: root.eventsForDate(root.calendarDate).length === 0
                                text: "Sem eventos"
                                color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                            }
                            ListView {
                                id: dayTimeline
                                width: parent.width
                                height: Math.min(4, count) * 50
                                spacing: 3
                                clip: true
                                interactive: count > 4
                                model: root.sortedEventsForDate(root.calendarDate)
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOff }
                                delegate: Item {
                                    required property var modelData
                                    width: dayTimeline.width
                                    height: 47

                                    Text { renderType: Text.QtRendering;
                                        width: 52; anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                                        text: modelData.time
                                        color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                                        horizontalAlignment: Text.AlignRight
                                    }
                                    Rectangle {
                                        anchors.left: parent.left; anchors.leftMargin: 65
                                        anchors.top: parent.top; anchors.bottom: parent.bottom
                                        width: 1; color: root.controlButtonOutline
                                    }
                                    Rectangle {
                                        anchors.left: parent.left; anchors.leftMargin: 61
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 9; height: 9; radius: 5; color: root.textMain
                                    }
                                    Rectangle {
                                        anchors.left: parent.left; anchors.leftMargin: 80
                                        anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                                        height: 44; radius: 12; color: root.controlButtonSurface
                                        Text { renderType: Text.QtRendering;
                                            anchors.left: parent.left; anchors.leftMargin: 11; anchors.top: parent.top; anchors.topMargin: 7
                                            width: parent.width - 112
                                            text: modelData.title
                                            elide: Text.ElideRight; color: root.textMain
                                            font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                                        }
                                        Text { renderType: Text.QtRendering;
                                            anchors.left: parent.left; anchors.leftMargin: 11; anchors.bottom: parent.bottom; anchors.bottomMargin: 6
                                            width: parent.width - 112
                                            text: modelData.category + (modelData.notes ? " · " + modelData.notes : "")
                                            elide: Text.ElideRight; color: root.textDim
                                            font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                        }
                                        Rectangle {
                                            id: timelineEdit
                                            anchors.right: timelineRemove.left; anchors.rightMargin: 5; anchors.verticalCenter: parent.verticalCenter
                                            width: 54; height: Appearance.calendarActionHeight; radius: 5
                                            color: root.calendarActionIsFocused("edit", modelData.id) ? root.controlButtonActive : (root.controlButtonSurface)
                                            readonly property bool menuScrollFocused: root.calendarActionIsFocused("edit", modelData.id)
                                            onMenuScrollFocusedChanged: if (menuScrollFocused) root.revealKeyboardMenuItem(this)
                                            border.width: root.calendarActionIsFocused("edit", modelData.id) ? 1 : 0; border.color: "#ffffff"
                                            Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: "Editar"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                            BounceMouseArea { id: timelineEditMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.beginEditEvent(modelData) }
                                        }
                                        Rectangle {
                                            id: timelineRemove
                                            anchors.right: parent.right; anchors.rightMargin: 7; anchors.verticalCenter: parent.verticalCenter
                                            width: 28; height: Appearance.calendarActionHeight; radius: 5
                                            color: root.calendarActionIsFocused("delete", modelData.id) ? "#743541" : (root.controlButtonSurface)
                                            readonly property bool menuScrollFocused: root.calendarActionIsFocused("delete", modelData.id)
                                            onMenuScrollFocusedChanged: if (menuScrollFocused) root.revealKeyboardMenuItem(this)
                                            border.width: root.calendarActionIsFocused("delete", modelData.id) ? 1 : 0; border.color: "#ffffff"
                                            Text { renderType: Text.QtRendering; font.family: Appearance.fontFamily; anchors.centerIn: parent; text: "×"; color: "#ff91a4"; font.pixelSize: 16 }
                                            BounceMouseArea { id: timelineRemoveMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.deleteEvent(modelData.id) }
                                        }
                                    }
                                }
                            }
                        }

                        }

                        Row {
                            width: parent.width
                            spacing: 6
                            Rectangle {
                                width: (parent.width - 6) / 2; height: Appearance.calendarActionHeight; radius: 8
                                color: root.calendarActionIsFocused("today", "today") ? root.controlButtonActive : (root.controlButtonSurface)
                                readonly property bool menuScrollFocused: root.calendarActionIsFocused("today", "today")
                                onMenuScrollFocusedChanged: if (menuScrollFocused) root.revealKeyboardMenuItem(this)
                                border.width: root.calendarActionIsFocused("today", "today") ? 1 : 0; border.color: "#ffffff"
                                Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: "Hoje"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                BounceMouseArea { id: todayMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.selectCalendarDate(root.currentDate) }
                            }
                            Rectangle {
                                width: (parent.width - 6) / 2; height: Appearance.calendarActionHeight; radius: 8
                                color: root.calendarActionIsFocused("new", "new") ? root.controlButtonActive : (root.controlButtonSurface)
                                readonly property bool menuScrollFocused: root.calendarActionIsFocused("new", "new")
                                onMenuScrollFocusedChanged: if (menuScrollFocused) root.revealKeyboardMenuItem(this)
                                border.width: root.calendarActionIsFocused("new", "new") ? 1 : 0; border.color: "#ffffff"
                                Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: "Novo evento"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                BounceMouseArea { id: addMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.beginEvent() }
                            }
                        }

                        Text { renderType: Text.QtRendering;
                            visible: root.calendarView !== "day"
                            text: root.calendarDate.getDate() + " de " + root.monthNames[root.calendarDate.getMonth()].toLowerCase()
                            color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                        }
                        Text { renderType: Text.QtRendering;
                            visible: root.calendarView !== "day" && root.eventsForDate(root.calendarDate).length === 0
                            text: "Sem eventos"
                            color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                        }
                        ListView {
                            id: dayEventList
                            width: parent.width
                            height: root.calendarView === "day" ? 0 : Math.min(4, count) * 46
                            visible: root.calendarView !== "day"
                            spacing: 4
                            clip: true
                            interactive: count > 4
                            model: root.eventsForDate(root.calendarDate)
                            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOff }
                            delegate: Rectangle {
                                required property var modelData
                                width: menuContent.width; height: Appearance.calendarActionHeight; radius: 8
                                color: root.controlButtonSurface; opacity: modelData.active ? 1 : 0.55
                                Rectangle { width: 4; height: parent.height; radius: 2; color: root.textMain }
                                Text { renderType: Text.QtRendering;
                                    anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter
                                    width: parent.width - 108
                                    text: modelData.time + "  " + modelData.title
                                    elide: Text.ElideRight; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                }
                                Rectangle {
                                    id: editEvent
                                    anchors.right: removeEvent.left; anchors.rightMargin: 5; anchors.verticalCenter: parent.verticalCenter
                                    width: 54; height: Appearance.calendarActionHeight; radius: 5
                                    color: root.calendarActionIsFocused("edit", modelData.id) ? root.controlButtonActive : (root.controlButtonSurface)
                                    readonly property bool menuScrollFocused: root.calendarActionIsFocused("edit", modelData.id)
                                    onMenuScrollFocusedChanged: if (menuScrollFocused) root.revealKeyboardMenuItem(this)
                                    border.width: root.calendarActionIsFocused("edit", modelData.id) ? 1 : 0; border.color: "#ffffff"
                                    Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: "Editar"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                    BounceMouseArea { id: editMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.beginEditEvent(modelData) }
                                }
                                Rectangle {
                                    id: removeEvent
                                    anchors.right: parent.right; anchors.rightMargin: 6; anchors.verticalCenter: parent.verticalCenter
                                    width: 28; height: Appearance.calendarActionHeight; radius: 5
                                    color: root.calendarActionIsFocused("delete", modelData.id) ? "#743541" : (root.controlButtonSurface)
                                    readonly property bool menuScrollFocused: root.calendarActionIsFocused("delete", modelData.id)
                                    onMenuScrollFocusedChanged: if (menuScrollFocused) root.revealKeyboardMenuItem(this)
                                    border.width: root.calendarActionIsFocused("delete", modelData.id) ? 1 : 0; border.color: "#ffffff"
                                    Text { renderType: Text.QtRendering; font.family: Appearance.fontFamily; anchors.centerIn: parent; text: "×"; color: "#ff91a4"; font.pixelSize: 16 }
                                    BounceMouseArea { id: removeMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.deleteEvent(modelData.id) }
                                }
                            }
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 6
                        visible: root.popupKind === "calendar" && root.calendarEditor

                        MenuButton { alignedIcon: false; height: Appearance.calendarActionHeight; width: parent.width; outlined: true; iconName: "chevron-left"; label: "Voltar ao calendário"; onActivated: root.cancelCalendarEditor() }
                        MenuHeader { id: calendarEditorHeader; title: root.editingEventId ? "Editar evento" : "Novo evento" }
                        Text { renderType: Text.QtRendering; text: "Título"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        EventField { id: calendarTitleField; text: root.draftTitle; placeholder: "Nome do evento"; onTextChanged: root.draftTitle = text }

                        Row {
                            width: parent.width; spacing: 6
                            Column {
                                width: (parent.parent.width - 6) * 0.62; spacing: 4
                                Text { renderType: Text.QtRendering; text: "Data (AAAA-MM-DD)"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                                EventField { id: calendarDateField; width: parent.width; text: root.draftDate; placeholder: "2026-08-02"; onTextChanged: root.draftDate = text }
                            }
                            Column {
                                width: (parent.parent.width - 6) * 0.38; spacing: 4
                                Text { renderType: Text.QtRendering; text: "Hora"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                                EventField { id: calendarTimeField; width: parent.width; text: root.draftTime; placeholder: "09:00"; onTextChanged: root.draftTime = text }
                            }
                        }

                        Text { renderType: Text.QtRendering; text: "Categoria"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        Rectangle {
                            id: categoryButton
                            width: parent.width; height: Appearance.calendarActionHeight; radius: 8
                            activeFocusOnTab: true
                            color: activeFocus ? root.controlButtonActive : (root.controlButtonSurface)
                            border.width: root.categoryPickerOpen || activeFocus ? 1 : 0; border.color: activeFocus ? root.cyan : root.controlButtonOutline
                            Keys.onPressed: function(event) {
                                if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                    root.categoryPickerOpen = !root.categoryPickerOpen
                                    event.accepted = true
                                }
                            }
                            Text { renderType: Text.QtRendering;
                                anchors.left: parent.left; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter
                                text: root.draftCategory || "Escolher categoria"
                                color: root.draftCategory ? root.textMain : root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                            }
                            Text { renderType: Text.QtRendering; font.family: Appearance.fontFamily; anchors.right: parent.right; anchors.rightMargin: 10; anchors.verticalCenter: parent.verticalCenter; text: root.categoryPickerOpen ? "▴" : "▾"; color: root.textMain }
                            BounceMouseArea { id: categoryButtonMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.categoryPickerOpen = !root.categoryPickerOpen }
                        }
                        Column {
                            width: parent.width; spacing: 4; visible: root.categoryPickerOpen
                            Text { renderType: Text.QtRendering;
                                visible: root.calendarCategories.length === 0
                                text: "Sem categorias"
                                color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                            }
                            ListView {
                                width: parent.width
                                height: Math.min(4, count) * 30
                                spacing: 3; clip: true; interactive: count > 4
                                model: root.calendarCategories
                                delegate: Rectangle {
                                    required property string modelData
                                    width: ListView.view.width; height: 27; radius: 5
                                    activeFocusOnTab: true
                                    color: activeFocus ? root.controlButtonActive : (root.draftCategory === modelData ? root.controlButtonOutline : root.controlButtonSurface)
                                    SelectionIndicator { visible: root.draftCategory === modelData }
                                    border.width: activeFocus ? 1 : 0; border.color: root.cyan
                                    Keys.onPressed: function(event) {
                                        if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                            root.draftCategory = modelData
                                            root.categoryPickerOpen = false
                                            event.accepted = true
                                        }
                                    }
                                    Text { renderType: Text.QtRendering; anchors.left: parent.left; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter; text: modelData; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                                    BounceMouseArea {
                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                        onClicked: { root.draftCategory = modelData; root.categoryPickerOpen = false }
                                    }
                                }
                            }
                            Rectangle {
                                width: parent.width; height: Appearance.calendarActionHeight; radius: 5; activeFocusOnTab: true
                                color: activeFocus ? root.controlButtonActive : (root.controlButtonSurface)
                                border.width: activeFocus ? 1 : 0; border.color: root.cyan
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                        root.newCategoryOpen = true
                                        event.accepted = true
                                    }
                                }
                                Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: "Criar categoria"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                BounceMouseArea { id: newCategoryMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.newCategoryOpen = true }
                            }
                        }
                        Row {
                            width: parent.width; spacing: 6; visible: root.newCategoryOpen
                            EventField { id: newCategoryField; width: parent.width - 86; text: root.newCategoryName; placeholder: "Nome da categoria"; onTextChanged: root.newCategoryName = text }
                            Rectangle {
                                width: 80; height: Appearance.calendarActionHeight; radius: 8; activeFocusOnTab: true
                                color: activeFocus ? root.controlButtonHover : (root.controlButtonOutline)
                                border.width: activeFocus ? 1 : 0; border.color: root.cyan
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                        root.createCategory()
                                        event.accepted = true
                                    }
                                }
                                Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: "Criar"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                BounceMouseArea { id: createCategoryMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.createCategory() }
                            }
                        }

                        MenuButton { alignedIcon: false;
                            width: parent.width; height: Appearance.calendarActionHeight; iconName: "chevron-right"
                            label: "Notas e partilha"; onActivated: root.calendarDetailsOpen = !root.calendarDetailsOpen
                        }
                        Column {
                            width: parent.width; spacing: 6
                            height: root.calendarDetailsOpen ? implicitHeight : 0
                            visible: height > 0; clip: true
                            opacity: root.calendarDetailsOpen ? 1 : 0
                            Behavior on height { NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                            Behavior on opacity { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                        Text { renderType: Text.QtRendering; text: "Notas (opcional)"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        EventField { id: calendarNotesField; text: root.draftNotes; placeholder: "Local, descrição, ligação…"; onTextChanged: root.draftNotes = text }

                        Text { renderType: Text.QtRendering; text: "Partilha"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        EventToggle {
                            width: parent.width
                            label: "Partilhar entre Environments"
                            checked: root.draftShared
                            onActivated: root.draftShared = !root.draftShared
                        }

                        }
                        MenuButton { alignedIcon: false;
                            width: parent.width; height: Appearance.calendarActionHeight; iconName: "bell"
                            label: root.draftReminders.length ? "Lembretes · " + root.draftReminders.length : "Adicionar lembrete"
                            onActivated: root.calendarRemindersOpen = !root.calendarRemindersOpen
                        }
                        Column {
                            width: parent.width; spacing: 6
                            height: root.calendarRemindersOpen ? implicitHeight : 0
                            visible: height > 0; clip: true
                            opacity: root.calendarRemindersOpen ? 1 : 0
                            Behavior on height { NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                            Behavior on opacity { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                        Text { renderType: Text.QtRendering; text: "Avisar antes"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        Row {
                            width: parent.width; spacing: 5
                            EventField {
                                width: 58
                                text: root.draftReminderAmount
                                placeholder: "1"
                                onTextChanged: root.draftReminderAmount = text.replace(/[^0-9]/g, "")
                            }
                            Repeater {
                                model: ["Minutos", "Horas", "Dias", "Semanas"]
                                Rectangle {
                                    required property string modelData
                                    width: (menuContent.width - 73) / 4; height: Appearance.calendarActionHeight; radius: 5
                                    activeFocusOnTab: true
                                    color: activeFocus ? root.controlButtonActive : (root.draftReminderUnit === modelData ? root.controlButtonOutline : root.controlButtonSurface)
                                    SelectionIndicator { visible: root.draftReminderUnit === modelData }
                                    border.width: activeFocus ? 1 : 0; border.color: activeFocus ? root.cyan : root.controlButtonOutline
                                    Keys.onPressed: function(event) {
                                        if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                            root.draftReminderUnit = modelData
                                            event.accepted = true
                                        }
                                    }
                                    Text { renderType: Text.QtRendering;
                                        anchors.centerIn: parent; text: modelData
                                        color: root.draftReminderUnit === modelData ? root.textMain : root.textDim
                                        font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                                    }
                                    BounceMouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.draftReminderUnit = modelData }
                                }
                            }
                        }
                        Rectangle {
                            width: parent.width; height: Appearance.calendarActionHeight; radius: 8; activeFocusOnTab: true
                            color: activeFocus ? root.controlButtonHover : (root.controlButtonOutline)
                            border.width: 1; border.color: activeFocus ? root.cyan : root.controlButtonOutline
                            Keys.onPressed: function(event) {
                                if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                    root.addDraftReminder()
                                    event.accepted = true
                                }
                            }
                            Text { renderType: Text.QtRendering;
                                anchors.centerIn: parent
                                text: "Adicionar lembrete"
                                color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                            }
                            BounceMouseArea {
                                id: addReminderMouse
                                anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                onClicked: root.addDraftReminder()
                            }
                        }
                        Text { renderType: Text.QtRendering;
                            visible: root.draftReminders.length === 0
                            text: "Sem lembretes"
                            color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                        }
                        Flow {
                            width: parent.width
                            spacing: 5
                            Repeater {
                                model: root.draftReminders
                                Rectangle {
                                    required property int modelData
                                    height: Appearance.calendarActionHeight
                                    width: reminderText.implicitWidth + 42
                                    radius: 8; color: activeFocus ? "#49242c" : root.controlButtonSurface
                                    activeFocusOnTab: true
                                    border.width: 1; border.color: activeFocus ? "#ffd3da" : root.controlButtonOutline
                                    Keys.onPressed: function(event) {
                                        if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space || event.key === Qt.Key_Delete) {
                                            root.removeDraftReminder(modelData)
                                            event.accepted = true
                                        }
                                    }
                                    Text { renderType: Text.QtRendering;
                                        id: reminderText
                                        anchors.left: parent.left; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter
                                        text: root.reminderLabel(modelData)
                                        color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                    }
                                    Text { renderType: Text.QtRendering; font.family: Appearance.fontFamily;
                                        anchors.right: parent.right; anchors.rightMargin: 9; anchors.verticalCenter: parent.verticalCenter
                                        text: "×"; color: "#ff91a4"; font.pixelSize: root.menuTitleSize
                                    }
                                    BounceMouseArea {
                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                        onClicked: root.removeDraftReminder(modelData)
                                    }
                                }
                            }
                        }

                        }

                        Text { renderType: Text.QtRendering;
                            visible: root.eventError.length > 0
                            text: root.eventError; color: "#ff91a4"; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                        }
                        Row {
                            width: parent.width; spacing: 6
                            Rectangle {
                                width: (parent.width - 6) / 2; height: Appearance.calendarActionHeight; radius: 8; activeFocusOnTab: true
                                color: activeFocus ? root.controlButtonActive : (root.controlButtonSurface)
                                border.width: activeFocus ? 1 : 0; border.color: root.cyan
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                        root.cancelCalendarEditor()
                                        event.accepted = true
                                    }
                                }
                                Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: "Cancelar"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                                BounceMouseArea { id: cancelMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.cancelCalendarEditor() }
                            }
                            Rectangle {
                                width: (parent.width - 6) / 2; height: Appearance.calendarActionHeight; radius: 8; activeFocusOnTab: true
                                color: activeFocus ? root.controlButtonHover : (root.controlButtonOutline)
                                border.width: 1; border.color: activeFocus ? root.cyan : root.controlButtonOutline
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                        root.saveDraftEvent()
                                        event.accepted = true
                                    }
                                }
                                Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: root.editingEventId ? "Guardar alterações" : "Guardar evento"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                BounceMouseArea { id: saveMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.saveDraftEvent() }
                            }
                        }
                    }

                MenuHeader {
                    id: scrollingMenuHeader
                    visible: root.popupKind !== "calendar" && !popupBackground.splitControls
                    title: root.popupKind === "media" ? "Reprodução" : root.popupKind === "battery" ? "Bateria e Energia" : (root.popupKind === "controls" ? (root.renderedControls.controlsActivityKind === "notifications" ? "Notificações" : root.renderedControls.shortcutsOpen ? "Lista de Atalhos" : (root.renderedControls.controlsMoreOpen ? (root.renderedControls.controlsAppearanceOpen ? "Personalização" : (root.renderedControls.controlsActivityKind === "trackpad" ? "Trackpad" : "Mais opções")) : "Central de Controlo")) : (root.popupKind === "environments" ? (root.environmentCreateOpen ? "Criar environment" : "Environments") : "[ " + root.popupKind.toUpperCase() + " Control ]"))
                }

                Column {
                    id: mediaMenu
                    readonly property bool mediaTransitionRunning: mediaPanel.transitioning
                    width: parent.width; spacing: 10
                    visible: root.popupKind === "media"
                    ActivityPanel { id: mediaPanel; width: parent.width; kind: "media"; showBack: false }
                    Row {
                        width: parent.width; spacing: 8; height: 36
                        LucideIcon { width: 20; height: 20; anchors.verticalCenter: parent.verticalCenter; name: root.volumeMuted ? "volume-x" : "volume-2" }
                        ControlSlider {
                            id: mediaVolume
                            width: parent.width - 28; height: 36
                            from: 0; to: 100; stepSize: 1; activeFocusOnTab: true
                            Accessible.name: "Volume de reprodução"
                            onMoved: { root.previewVolume(value); if (!pressed) root.commitVolume(value) }
                            onPressedChanged: if (!pressed) root.commitVolume(value)
                            Binding { target: mediaVolume; property: "value"; value: root.volumeMuted ? 0 : root.volumeValue; when: !mediaVolume.pressed }
                        }
                    }
                }


                Column {
                    id: environmentMenu
                    width: parent.width; spacing: 8
                    visible: root.popupKind === "environments"
                    focus: visible && root.isHub
                    Keys.onPressed: function(event) {
                        if (!root.isHub) { root.navigateGenericMenu(event); return }
                        if (!root.environmentKeyboardFocus && event.key === Qt.Key_Up) { event.accepted = true; return }
                        if ([Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down].indexOf(event.key) >= 0)
                            root.menuKeyboardNavigation = true
                        if (!root.environmentKeyboardFocus && [Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down, Qt.Key_Return, Qt.Key_Enter].indexOf(event.key) >= 0) {
                            root.environmentKeyboardFocus = true
                            root.menuKeyboardNavigation = true
                            if (!root.environmentEditOpen && !root.environmentCreateOpen && !root.environmentDeleteConfirm) {
                                root.environmentFocusIndex = -1
                                root.moveEnvironmentFocus(event.key === Qt.Key_Up || event.key === Qt.Key_Backtab ? -1 : 1)
                            }
                            event.accepted = true
                            return
                        }
                        if (root.environmentEditOpen) {
                            root.handleEnvironmentEditKey(event)
                            return
                        }
                        if (root.environmentCreateOpen) {
                            root.handleEnvironmentCreateKey(event)
                            return
                        }
                        if (!root.isHub) return
                        if (root.environmentDeleteConfirm) {
                            if (event.key === Qt.Key_Left) {
                                root.environmentDeleteFocusIndex = 0
                            } else if (event.key === Qt.Key_Right) {
                                root.environmentDeleteFocusIndex = 1
                            } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                                if (root.environmentDeleteFocusIndex === 0) root.cancelEnvironmentDelete()
                                else root.destroySelectedEnvironment()
                            } else if (event.key === Qt.Key_Escape) {
                                root.cancelEnvironmentDelete()
                            } else {
                                return
                            }
                            event.accepted = true
                            return
                        }
                        if (event.key === Qt.Key_Up) {
                            root.moveEnvironmentFocus(-1)
                            event.accepted = true
                        } else if (event.key === Qt.Key_Down) {
                            root.moveEnvironmentFocus(1)
                            event.accepted = true
                        } else if (event.key === Qt.Key_Left) {
                            root.moveEnvironmentActionFocus(-1)
                            event.accepted = true
                        } else if (event.key === Qt.Key_Right) {
                            root.moveEnvironmentActionFocus(1)
                            event.accepted = true
                        } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                            root.activateEnvironmentFocus()
                            event.accepted = true
                        } else if (event.key === Qt.Key_Delete) {
                            root.deleteFocusedEnvironment()
                            event.accepted = true
                        } else if (event.key === Qt.Key_F2) {
                            root.beginEnvironmentEdit()
                            event.accepted = true
                        } else if (event.key === Qt.Key_Escape) {
                            root.closePopup()
                            event.accepted = true
                        }
                    }
                    Rectangle {
                        id: hubEnvironmentCard
                        visible: root.isHub && !root.environmentCreateOpen
                        property bool keyboardFocused: false
                        onKeyboardFocusedChanged: if (keyboardFocused) root.revealKeyboardMenuItem(this)
                        width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius
                        color: keyboardFocused ? root.controlButtonActive : root.controlButtonSurface
                        border.width: keyboardFocused ? 1 : 0
                        border.color: root.cyan
                        LucideIcon { anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter; width: 18; height: 18; name: root.activeEnvironmentIcon }
                        Column {
                            anchors.left: parent.left; anchors.leftMargin: 42; anchors.right: activeEnvironmentBadge.left; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; spacing: 3
                            Text { renderType: Text.QtRendering; width: parent.width; text: root.environmentLabel; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal; elide: Text.ElideRight }
                        }
                        Rectangle {
                            id: activeEnvironmentBadge
                            anchors.right: parent.right; anchors.rightMargin: 10; anchors.verticalCenter: parent.verticalCenter
                            width: 58; height: 24; radius: 12; color: root.controlButtonActive
                            Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: "Ativo"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                        }
                    }

                    Rectangle {
                        visible: !root.isHub
                        width: parent.width; height: 80; radius: 14; color: root.controlButtonSurface
                        Rectangle {
                            x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
                            width: Appearance.menuIconCircleSize; height: width; radius: width / 2; color: Qt.lighter(root.controlButtonSurface, 1.6)
                            LucideIcon { anchors.centerIn: parent; width: Appearance.menuGlyphSize; height: width; name: root.activeEnvironmentIcon }
                        }
                        Column {
                            anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset
                            anchors.right: parent.right; anchors.rightMargin: 14
                            anchors.verticalCenter: parent.verticalCenter; spacing: 5
                            Text { renderType: Text.QtRendering; width: parent.width; text: root.environmentLabel; elide: Text.ElideRight; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                            Row {
                                spacing: 6
                                LucideIcon { width: 14; height: 14; name: "check"; tint: root.textDim }
                                Text { renderType: Text.QtRendering; text: "Environment ativo"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            }
                        }
                    }

                    Column {
                        width: parent.width; spacing: 7
                        visible: root.isHub && !root.environmentCreateOpen && !root.environmentEditOpen
                        Row {
                            width: parent.width; height: 24
                            Text { renderType: Text.QtRendering; width: parent.width * 0.42; anchors.verticalCenter: parent.verticalCenter; text: "Os teus Environments"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                            Text { renderType: Text.QtRendering; width: parent.width * 0.58; anchors.verticalCenter: parent.verticalCenter; horizontalAlignment: Text.AlignRight; text: ""; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize; elide: Text.ElideLeft }
                        }
                        Repeater {
                            model: root.environmentCatalog.length ? root.environmentCatalog : [{ name: "", display_name: "Ainda não tens Environments", state: "empty", generation: "", category: "general" }]
                            Rectangle {
                                required property var modelData
                                required property int index
                                width: parent ? parent.width : 400; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius
                                property bool selected: modelData.name.length > 0 && root.selectedEnvironmentName === modelData.name
                                property bool keyboardFocused: root.environmentIsOpenable(modelData) && root.environmentKeyboardFocus && root.environmentFocusIndex === index
                                onKeyboardFocusedChanged: if (keyboardFocused) root.revealKeyboardMenuItem(this)
                                color: keyboardFocused ? root.controlButtonActive : (selected ? root.controlButtonActive : (root.controlButtonSurface))
                                SelectionIndicator { visible: parent.selected; color: "#ffffff" }
                                border.width: keyboardFocused ? 1 : 0; border.color: root.cyan
                                LucideIcon { anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter; width: 18; height: 18; name: root.environmentIcon(modelData) }
                                Column {
                                    anchors.left: parent.left; anchors.leftMargin: 42; anchors.right: environmentRowStatus.left; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; spacing: 3
                                    Text { renderType: Text.QtRendering; width: parent.width; text: String(modelData.display_name || modelData.name); color: modelData.state === "empty" ? root.textDim : root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal; elide: Text.ElideRight }

                                }
                                Text { renderType: Text.QtRendering; id: environmentRowStatus; anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; text: root.environmentIsOpenable(modelData) ? "" : (modelData.state === "preparing" ? "A preparar" : (modelData.state === "empty" ? "" : "Indisponível")); color: parent.selected ? root.textMain : root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                                BounceMouseArea {
                                    id: environmentChoiceMouse
                                    anchors.fill: parent
                                    enabled: root.environmentIsOpenable(modelData) && !root.environmentManagementBusy && !root.environmentMetadataBusy
                                    hoverEnabled: true
                                    cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                                    onClicked: {
                                        root.environmentKeyboardFocus = true
                                        root.environmentFocusIndex = index
                                        root.selectEnvironment(modelData)
                                        Qt.callLater(function() { environmentMenu.forceActiveFocus() })
                                    }
                                    onDoubleClicked: { root.environmentFocusIndex = index; root.selectEnvironment(modelData); root.openSelectedEnvironment() }
                                }
                            }
                        }

                        Row {
                            width: parent.width; height: Appearance.menuActionHeight; spacing: 6
                            MenuButton { width: (parent.width - 12) * 0.44; height: Appearance.menuActionHeight; label: "Criar"; keyboardFocused: root.environmentKeyboardFocus && root.environmentFocusIndex === root.environmentCatalog.length; enabled: !root.environmentManagementBusy && !root.environmentMetadataBusy; onActivated: { root.environmentFocusIndex = root.environmentCatalog.length; root.beginEnvironmentCreate() } }
                            MenuButton { width: (parent.width - 12) * 0.31; height: Appearance.menuActionHeight; label: "Editar"; keyboardFocused: root.environmentKeyboardFocus && root.environmentFocusIndex === root.environmentCatalog.length + 1; enabled: root.selectedEnvironmentName.length > 0 && !root.environmentManagementBusy && !root.environmentMetadataBusy; onActivated: { root.environmentFocusIndex = root.environmentCatalog.length + 1; root.beginEnvironmentEdit() } }
                            MenuButton { width: (parent.width - 12) * 0.25; height: Appearance.menuActionHeight; label: "Apagar"; keyboardFocused: root.environmentKeyboardFocus && root.environmentFocusIndex === root.environmentCatalog.length + 2; enabled: root.selectedEnvironmentName.length > 0 && !root.environmentManagementBusy && !root.environmentMetadataBusy; onActivated: { root.environmentFocusIndex = root.environmentCatalog.length + 2; root.requestEnvironmentDelete() } }
                        }

                        Rectangle {
                            visible: root.environmentDeleteConfirm
                            width: parent.width; height: visible ? 80 : 0; radius: 8; color: "#29181d"; border.width: 1; border.color: "#7d3947"
                            Column { anchors.left: parent.left; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter; width: parent.width - 162; spacing: 2
                                Text { renderType: Text.QtRendering; width: parent.width; text: "Apagar " + root.selectedEnvironmentName + "?"; color: "#ffb2bf"; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal; elide: Text.ElideRight }
                                Text { renderType: Text.QtRendering; width: parent.width; text: root.environmentSelection() && root.environmentSelection().native_version === 3 ? "Apaga só este Windows e o seu EFI. Os 80 GiB ficam reservados para outro Windows; não é apagamento seguro." : (root.environmentIsNative(root.environmentSelection()) ? "Apaga a partição e devolve todo o espaço ao APX após reiniciar." : "Purga total: dados, VM, cópias e metadados."); color: "#b98992"; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize; wrapMode: Text.WordWrap }
                            }
                            Row { anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter; spacing: 5
                                Rectangle { width: 62; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; color: root.environmentDeleteFocusIndex === 0 ? root.controlButtonActive : "#21161a"; border.width: root.environmentDeleteFocusIndex === 0 ? 1 : 0; border.color: root.cyan
                                    Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: "Cancelar"; color: root.environmentDeleteFocusIndex === 0 ? root.textMain : root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                                    BounceMouseArea { id: cancelDeleteMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: { root.environmentDeleteFocusIndex = 0; root.cancelEnvironmentDelete() } }
                                }
                                Rectangle { width: 70; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; color: root.environmentDeleteFocusIndex === 1 ? "#8a4050" : "#21161a"; border.width: root.environmentDeleteFocusIndex === 1 ? 1 : 0; border.color: "#ffd3da"
                                    Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: "Apagar"; color: root.environmentDeleteFocusIndex === 1 ? "#ffd3da" : root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                                    BounceMouseArea { id: confirmDeleteMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: { root.environmentDeleteFocusIndex = 1; root.destroySelectedEnvironment() } }
                                }
                            }
                        }
                    }

                    Column {
                        width: parent.width; spacing: 9
                        visible: root.isHub && root.environmentEditOpen
                        Row {
                            width: parent.width; height: Appearance.menuActionHeight; spacing: 8
                            Rectangle {
                                width: 92; height: parent.height; radius: 6
                                color: root.environmentEditFocusIndex === 0 ? root.controlButtonActive : (root.controlButtonSurface)
                                border.width: root.environmentEditFocusIndex === 0 ? 1 : 0
                                border.color: root.cyan
                                Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: "‹  Voltar"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                                BounceMouseArea { id: environmentEditBackMouse; anchors.fill: parent; enabled: !root.environmentMetadataBusy; hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor; onClicked: { root.environmentEditFocusIndex = 0; root.cancelEnvironmentEdit() } }
                            }
                            Text { renderType: Text.QtRendering; width: parent.width - 100; anchors.verticalCenter: parent.verticalCenter; text: "Editar apresentação"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                        }
                        Rectangle {
                            width: parent.width; height: 42; radius: 7; color: root.controlButtonSurface; border.width: 1; border.color: environmentEditTitleInput.activeFocus || root.environmentEditFocusIndex === 1 ? root.cyan : root.controlButtonOutline
                            TextInput {
                                id: environmentEditTitleInput; anchors.fill: parent; anchors.leftMargin: 11; anchors.rightMargin: 11; verticalAlignment: TextInput.AlignVCenter
                                text: root.environmentEditTitle; onTextChanged: root.environmentEditTitle = text; maximumLength: 64; enabled: !root.environmentMetadataBusy
                                color: root.textMain; selectionColor: root.controlButtonOutline; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                onActiveFocusChanged: if (activeFocus) { root.environmentEditFocusIndex = 1; root.revealKeyboardMenuItem(parent) }
                                onAccepted: { root.environmentEditFocusIndex = 2; environmentEditDescriptionInput.forceActiveFocus() }
                                Keys.priority: Keys.BeforeItem
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Tab) { root.environmentEditFocusIndex = 2; environmentEditDescriptionInput.forceActiveFocus(); event.accepted = true }
                                    else if (event.key === Qt.Key_Backtab) { root.environmentEditFocusIndex = 0; environmentMenu.forceActiveFocus(); event.accepted = true }
                                    else if (event.key === Qt.Key_Escape) { root.cancelEnvironmentEdit(); event.accepted = true }
                                }
                            }
                            Text { renderType: Text.QtRendering; anchors.left: parent.left; anchors.leftMargin: 11; anchors.verticalCenter: parent.verticalCenter; visible: !environmentEditTitleInput.text.length; text: "Título do Environment"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        }
                        Rectangle {
                            width: parent.width; height: 42; radius: 7; color: root.controlButtonSurface; border.width: 1; border.color: environmentEditDescriptionInput.activeFocus || root.environmentEditFocusIndex === 2 ? root.cyan : root.controlButtonOutline
                            TextInput {
                                id: environmentEditDescriptionInput; anchors.fill: parent; anchors.leftMargin: 11; anchors.rightMargin: 11; verticalAlignment: TextInput.AlignVCenter
                                text: root.environmentEditDescription; onTextChanged: root.environmentEditDescription = text; maximumLength: 120; enabled: !root.environmentMetadataBusy
                                color: root.textMain; selectionColor: root.controlButtonOutline; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                onActiveFocusChanged: if (activeFocus) { root.environmentEditFocusIndex = 2; root.revealKeyboardMenuItem(parent) }
                                onAccepted: { root.environmentEditFocusIndex = 3; environmentMenu.forceActiveFocus() }
                                Keys.priority: Keys.BeforeItem
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Tab) { root.environmentEditFocusIndex = 3; environmentMenu.forceActiveFocus(); event.accepted = true }
                                    else if (event.key === Qt.Key_Backtab) { root.environmentEditFocusIndex = 1; environmentEditTitleInput.forceActiveFocus(); event.accepted = true }
                                    else if (event.key === Qt.Key_Escape) { root.cancelEnvironmentEdit(); event.accepted = true }
                                }
                            }
                            Text { renderType: Text.QtRendering; anchors.left: parent.left; anchors.leftMargin: 11; anchors.verticalCenter: parent.verticalCenter; visible: !environmentEditDescriptionInput.text.length; text: "Legenda (opcional)"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        }
                        Text { renderType: Text.QtRendering; text: "Ícone"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                        Grid {
                            width: parent.width; columns: 8; spacing: 5
                            Repeater {
                                model: root.environmentIconChoices
                                delegate: MenuButton {
                                    required property string modelData
                                    width: (parent.width - 35) / 8; height: Appearance.menuActionHeight
                                    iconName: modelData
                                    label: ""
                                    Accessible.name: "Ícone " + modelData
                                    selected: root.environmentEditIcon === modelData
                                    keyboardFocused: root.environmentEditFocusIndex === 3 && selected
                                    enabled: !root.environmentMetadataBusy
                                    onActivated: {
                                        root.environmentEditIcon = modelData
                                        root.environmentEditFocusIndex = 3
                                        environmentMenu.forceActiveFocus()
                                    }
                                }
                            }
                        }
                        MenuButton {
                            width: parent.width; height: Appearance.menuActionHeight
                            label: root.environmentMetadataBusy ? "A guardar…" : "Guardar alterações"
                            accent: true
                            keyboardFocused: root.environmentEditFocusIndex === 4
                            enabled: !root.environmentMetadataBusy && root.environmentEditTitle.trim().length > 0
                            onActivated: { root.environmentEditFocusIndex = 3; root.saveEnvironmentMetadata() }
                        }
                    }

                    Column {
                        id: environmentCreationForm
                        width: parent.width; spacing: 10
                        visible: root.isHub && root.environmentCreateOpen
                        MenuButton {
                            width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius
                            alignedIcon: true; iconName: "chevron-left"; label: "Voltar aos environments"
                            keyboardFocused: root.environmentCreateFocusIndex === 0
                            enabled: !root.environmentManagementBusy
                            onActivated: { root.environmentCreateFocusIndex = 0; root.cancelEnvironmentCreate() }
                        }
                        Rectangle {
                            width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; color: root.controlButtonSurface
                            border.width: environmentNameInput.activeFocus ? 1 : 0; border.color: root.cyan
                            Rectangle { x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter; width: Appearance.menuIconCircleSize; height: width; radius: width / 2; color: Qt.lighter(root.controlButtonSurface, 1.6)
                                LucideIcon { anchors.centerIn: parent; width: Appearance.menuGlyphSize; height: width; name: "book-a" }
                            }
                            Text { renderType: Text.QtRendering; x: Appearance.menuLabelInset; anchors.verticalCenter: parent.verticalCenter; text: "Nome"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                            TextInput {
                                id: environmentNameInput
                                x: Appearance.menuLabelInset + 90; anchors.verticalCenter: parent.verticalCenter; width: parent.width - Appearance.menuLabelInset - 104; height: 22; verticalAlignment: TextInput.AlignVCenter
                                text: root.environmentDraftName; onTextChanged: root.environmentDraftName = text; maximumLength: 27
                                color: root.textMain; selectionColor: root.controlButtonOutline; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; clip: true
                                Accessible.name: "Nome do environment"
                                onActiveFocusChanged: if (activeFocus) { root.environmentCreateFocusIndex = 1; root.revealKeyboardMenuItem(parent) }
                                onAccepted: { root.environmentCreateFocusIndex = 2; environmentDescriptionInput.forceActiveFocus() }
                                Keys.priority: Keys.BeforeItem
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Tab) { root.environmentCreateFocusIndex = 2; environmentDescriptionInput.forceActiveFocus(); event.accepted = true }
                                    else if (event.key === Qt.Key_Backtab) { root.environmentCreateFocusIndex = 0; environmentMenu.forceActiveFocus(); event.accepted = true }
                                }
                            }
                        }
                        Rectangle {
                            width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; color: root.controlButtonSurface
                            border.width: environmentDescriptionInput.activeFocus ? 1 : 0; border.color: root.cyan
                            Rectangle { x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter; width: Appearance.menuIconCircleSize; height: width; radius: width / 2; color: Qt.lighter(root.controlButtonSurface, 1.6)
                                LucideIcon { anchors.centerIn: parent; width: Appearance.menuGlyphSize; height: width; name: "book-open" }
                            }
                            Text { renderType: Text.QtRendering; x: Appearance.menuLabelInset; anchors.verticalCenter: parent.verticalCenter; text: "Descrição"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                            TextInput {
                                id: environmentDescriptionInput
                                x: Appearance.menuLabelInset + 90; anchors.verticalCenter: parent.verticalCenter; width: parent.width - Appearance.menuLabelInset - 104; height: 22; verticalAlignment: TextInput.AlignVCenter
                                text: root.environmentDraftDescription; onTextChanged: root.environmentDraftDescription = text; maximumLength: 120
                                color: root.textMain; selectionColor: root.controlButtonOutline; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; clip: true
                                Accessible.name: "Descrição do environment"
                                onActiveFocusChanged: if (activeFocus) { root.environmentCreateFocusIndex = 2; root.revealKeyboardMenuItem(parent) }
                                onAccepted: { root.environmentCreateFocusIndex = 3; environmentMenu.forceActiveFocus() }
                                Keys.priority: Keys.BeforeItem
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Backtab) { root.environmentCreateFocusIndex = 1; environmentNameInput.forceActiveFocus(); event.accepted = true }
                                    else if (event.key === Qt.Key_Tab) { root.environmentCreateFocusIndex = 3; environmentMenu.forceActiveFocus(); event.accepted = true }
                                }
                            }
                        }
                        Text { renderType: Text.QtRendering; text: "Sistema"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                        Row {
                            width: parent.width; height: Appearance.menuActionHeight; spacing: 8
                            CreationChoice {
                                width: (parent.width - 8) / 2; height: parent.height
                                objectName: "createApxChoice"
                                title: "APX"; iconName: "package"
                                selected: root.environmentSystemKind === "arch"; keyboardFocused: root.environmentCreateFocusIndex === 3
                                onActivated: { root.environmentCreateFocusIndex = 3; root.environmentSystemKind = "arch" }
                            }
                            CreationChoice {
                                width: (parent.width - 8) / 2; height: parent.height
                                objectName: "createWindowsChoice"
                                title: "Windows"; iconName: "monitor"
                                selected: root.environmentSystemKind === "windows-native"; keyboardFocused: root.environmentCreateFocusIndex === 4
                                onActivated: { root.environmentCreateFocusIndex = 4; root.environmentSystemKind = "windows-native"; if (!root.environmentDraftName.length || root.environmentDraftName === "windows") root.environmentDraftName = "windows-2" }
                            }
                        }
                        Text { renderType: Text.QtRendering; visible: root.environmentSystemKind === "windows-native"; text: "Espaço para o Windows"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                        Row {
                            visible: root.environmentSystemKind === "windows-native"; height: visible ? 44 : 0
                            width: parent.width; spacing: 8
                            Repeater {
                                model: [120, 180, 250]
                                MenuButton {
                                    required property int modelData
                                    required property int index
                                    width: (parent.width - 16) / 3; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius
                                    label: modelData + " GiB"; selected: root.environmentNativeWindowsSizeGib === modelData
                                    keyboardFocused: root.environmentCreateFocusIndex === 6 + index
                                    onActivated: { root.environmentCreateFocusIndex = 6 + index; root.environmentNativeWindowsSizeGib = modelData }
                                }
                            }
                        }
                        MenuButton {
                            visible: root.environmentSystemKind === "arch"
                            width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius
                            objectName: "createCustomize"
                            alignedIcon: true; iconName: "settings"; label: "Personalizar funcionalidades"
                            selected: root.environmentCreateCustomizeOpen
                            keyboardFocused: root.environmentCreateFocusIndex === 5
                            onActivated: { root.environmentCreateFocusIndex = 5; root.environmentCreateCustomizeOpen = !root.environmentCreateCustomizeOpen; environmentMenu.forceActiveFocus() }
                            LucideIcon { anchors.right: parent.right; anchors.rightMargin: 16; anchors.verticalCenter: parent.verticalCenter; width: Appearance.menuGlyphSize; height: width; name: "chevron-right"; rotation: root.environmentCreateCustomizeOpen ? 90 : 0; tint: root.textDim }
                        }
                        Column {
                            visible: root.environmentSystemKind === "arch" && root.environmentCreateCustomizeOpen
                            width: parent.width; spacing: 5
                            Repeater {
                                model: root.environmentModuleGroups
                                Column {
                                    id: featureGroup
                                    required property var modelData
                                    required property int index
                                    width: parent ? parent.width : 660; spacing: 4
                                    Rectangle {
                                        width: parent.width; height: 40; radius: 12
                                        property bool keyboardFocused: root.environmentCreateFocusIndex === 9 + index
                                        onKeyboardFocusedChanged: if (keyboardFocused) root.revealKeyboardMenuItem(this)
                                        color: keyboardFocused ? root.controlButtonActive : (root.controlButtonSurface)
                                        border.width: keyboardFocused || root.environmentFeatureDrawer === modelData.key ? 1 : 0
                                        border.color: keyboardFocused ? root.cyan : root.controlButtonOutline
                                        Text { renderType: Text.QtRendering; anchors.left: parent.left; anchors.leftMargin: 11; anchors.right: parent.right; anchors.rightMargin: 34; anchors.verticalCenter: parent.verticalCenter; text: ["Sistema e desktop", "Internet e dispositivos", "Aplicações do dia a dia", "Trabalho e programação", "Integrações"][featureGroup.index] || modelData.label; color: root.environmentFeatureDrawer === modelData.key ? root.textMain : root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal; elide: Text.ElideRight }
                                        Text { renderType: Text.QtRendering; font.family: Appearance.fontFamily; anchors.right: parent.right; anchors.rightMargin: 11; anchors.verticalCenter: parent.verticalCenter; text: root.environmentFeatureDrawer === modelData.key ? "▴" : "▾"; color: root.textDim; font.pixelSize: root.menuTitleSize }
                                        BounceMouseArea { id: featureDrawerMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: { root.environmentCreateFocusIndex = 9 + featureGroup.index; root.environmentFeatureDrawer = root.environmentFeatureDrawer === modelData.key ? "" : modelData.key; root.environmentFeatureInfo = "" } }
                                    }
                                    Grid {
                                        visible: root.environmentFeatureDrawer === modelData.key
                                        width: parent.width
                                        columns: 2; columnSpacing: 6; rowSpacing: 4
                                        Repeater {
                                            model: modelData.modules
                                            FeatureCard {
                                                required property string modelData
                                                property var moduleInfo: root.environmentModuleInfo(modelData)
                                                width: (environmentMenu.width - 6) / 2
                                                label: moduleInfo.label
                                                detail: moduleInfo.detail
                                                programs: moduleInfo.programs
                                                checked: root.environmentSelectedModules[moduleInfo.key] === true
                                                infoVisible: root.environmentFeatureInfo === moduleInfo.key
                                                keyboardFocused: root.environmentCreateFocusIndex === root.environmentCreateModuleFocusBase + root.environmentModuleIndex(moduleInfo.key)
                                                onActivated: { root.environmentCreateFocusIndex = root.environmentCreateModuleFocusBase + root.environmentModuleIndex(moduleInfo.key); root.setEnvironmentModule(moduleInfo.key, !checked) }
                                                onInfoRequested: { root.environmentCreateFocusIndex = root.environmentCreateModuleFocusBase + root.environmentModuleIndex(moduleInfo.key); root.environmentFeatureInfo = infoVisible ? "" : moduleInfo.key }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        Text { renderType: Text.QtRendering;
                            width: parent.width; wrapMode: Text.WordWrap; color: root.textDim
                            font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize
                            visible: root.environmentSystemKind === "windows-native"
                            text: "O Windows atual é preservado. Verifica o espaço antes de continuar."
                        }
                        Text { renderType: Text.QtRendering;
                            visible: root.environmentSystemKind === "windows-native" && !!root.nativeCreationPreview.target
                            width: parent.width
                            text: root.nativeCreationPreview.target ? ("Windows atual: " + root.nativeCreationPreview.existing_windows_gib + " GiB · Novo: " + root.nativeCreationPreview.size_gib + " GiB · APX: " + root.nativeCreationPreview.apx_gib + " GiB\n" + root.nativeCreationPreview.message) : ""
                            color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize; wrapMode: Text.WordWrap
                        }
                        MenuButton { objectName: "createSubmit"; width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; alignedIcon: true; iconName: "check"; label: root.environmentSystemKind === "windows-native" ? (nativeCreationPreviewProcess.running ? "A verificar…" : (root.nativeCreationPreview.can_create === true ? "Preparar Windows" : "Verificar espaço")) : (root.environmentManagementBusy ? "A criar…" : "Criar environment"); accent: true; keyboardFocused: root.environmentCreateFocusIndex === root.environmentCreateSubmitFocusIndex; enabled: !root.environmentManagementBusy && !nativeCreationPreviewProcess.running && root.environmentDraftName.trim().length > 0; onActivated: { root.environmentCreateFocusIndex = root.environmentCreateSubmitFocusIndex; root.createEnvironment(environmentNameInput.text, environmentDescriptionInput.text) } }
                    }

                    Rectangle {
                        visible: root.environmentManagementBusy
                        width: parent.width; height: visible ? 34 : 0; radius: 7; color: root.controlButtonSurface
                        Text { renderType: Text.QtRendering; anchors.left: parent.left; anchors.leftMargin: 9; anchors.top: parent.top; anchors.topMargin: 5; text: root.environmentManagementState.message || "A preparar…"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                        Rectangle { anchors.left: parent.left; anchors.leftMargin: 9; anchors.right: parent.right; anchors.rightMargin: 9; anchors.bottom: parent.bottom; anchors.bottomMargin: 6; height: 4; radius: 2; color: root.controlButtonOutline; Rectangle { width: parent.width * Math.max(2, Math.min(100, root.environmentManagementState.progress || 2)) / 100; height: parent.height; radius: 2; color: root.textMain } }
                    }

                    Column {
                        visible: root.isHub && root.environmentManagementState.native_v3 === true
                        width: parent.width; spacing: 6
                        Text { renderType: Text.QtRendering; width: parent.width; wrapMode: Text.WordWrap; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                            text: root.environmentManagementState.pending_stage === "deleting" ? "A eliminar apenas o Windows novo. Se a operação parou, podes continuá-la sem tocar no Windows atual." : (root.environmentManagementState.native_v3_activate ? (root.environmentManagementState.pending_mode === "slot-reuse" ? "O espaço reservado de " + root.environmentManagementState.new_size_gib + " GiB está pronto para receber outro Windows. A instalação reinicia o computador automaticamente e regressa ao Hub." : "A cópia está verificada. O Windows atual ficará com " + root.environmentManagementState.existing_size_gib + " GiB e o novo terá " + root.environmentManagementState.new_size_gib + " GiB. A instalação reinicia o computador automaticamente e regressa ao Hub.") : (root.environmentManagementState.native_v3_rollback ? "Podes repor o Windows anterior a partir da cópia guardada. A instalação nova incompleta será removida." : (root.environmentManagementState.native_v3_retry ? "A instalação nova falhou. Podes recomeçá-la; isso apaga apenas o Windows novo incompleto. O Windows atual e o APX ficam preservados." : (root.environmentManagementState.native_v3_manual_recovery ? "A instalação parou. Os dados e as partições foram preservados; é necessária uma recuperação assistida antes de tentar novamente." : "A preparar Windows. Acompanha o progresso acima."))))
                        }
                        MenuButton { visible: root.environmentManagementState.native_v3_activate === true; width: parent.width; height: visible ? Appearance.menuActionHeight : 0
                            label: root.nativeV3Confirmation === "activate:" + root.environmentManagementState.pending_generation ? "Confirmar instalação e reinício" : "Instalar e reiniciar"
                            enabled: !environmentActionProcess.running; accent: true; onActivated: root.nativeV3Action("activate") }
                        MenuButton { visible: root.environmentManagementState.native_v3_rollback === true; width: parent.width; height: visible ? Appearance.menuActionHeight : 0
                            label: root.nativeV3Confirmation === "rollback:" + root.environmentManagementState.pending_generation ? "Confirmar reposição" : "Repor Windows anterior"
                            enabled: !environmentActionProcess.running; onActivated: root.nativeV3Action("rollback") }
                        MenuButton { visible: root.environmentManagementState.native_v3_retry === true; width: parent.width; height: visible ? Appearance.menuActionHeight : 0
                            label: root.nativeV3Confirmation === "retry:" + root.environmentManagementState.pending_generation ? "Confirmar nova tentativa" : "Recomeçar instalação nova"
                            enabled: !environmentActionProcess.running; onActivated: root.nativeV3Action("retry") }
                        MenuButton { visible: root.environmentManagementState.native_v3_delete_retry === true; width: parent.width; height: visible ? Appearance.menuActionHeight : 0
                            label: root.nativeV3Confirmation === "delete:" + root.environmentManagementState.pending_generation ? "Confirmar continuar eliminação" : "Continuar eliminação"
                            enabled: !environmentActionProcess.running; onActivated: root.nativeV3Action("delete") }
                    }

                    Rectangle {
                        visible: root.isHub && root.nativeWindowsRecoveryAvailable()
                        width: parent.width; height: visible ? 112 : 0; radius: 8
                        color: "#291f18"; border.width: 1; border.color: "#765334"
                        Column {
                            anchors.fill: parent; anchors.margins: 8; spacing: 6
                            Text { renderType: Text.QtRendering; width: parent.width; text: "A criação Windows parou em segurança. Podes recomeçar apenas essa instalação ou devolver o espaço ao APX."; wrapMode: Text.WordWrap; color: "#e5c29c"; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            Row {
                                width: parent.width; height: Appearance.menuActionHeight; spacing: 6
                                MenuButton { visible: root.environmentManagementState.native_retry === true; width: visible ? (root.environmentManagementState.native_discard === true ? (parent.width - 6) * 0.5 : parent.width) : 0; height: Appearance.menuActionHeight; label: root.environmentManagementState.pending_stage === "boot-prepared" ? "Prosseguir Windows" : "Retomar Windows"; accent: true; enabled: !environmentActionProcess.running; onActivated: root.recoverNativeWindows("retry") }
                                MenuButton { visible: root.environmentManagementState.native_discard === true; width: visible ? (root.environmentManagementState.native_retry === true ? (parent.width - 6) * 0.5 : parent.width) : 0; height: Appearance.menuActionHeight; label: root.nativeRecoveryDiscardConfirm ? "Confirmar apagar" : (root.environmentManagementState.native_retry === true ? "Apagar incompleto" : "Tentar apagar"); enabled: !environmentActionProcess.running; onActivated: { if (root.nativeRecoveryDiscardConfirm) root.recoverNativeWindows("discard"); else root.nativeRecoveryDiscardConfirm = true } }
                            }
                        }
                    }

                    MenuButton {
                        visible: !root.isHub
                        width: parent.width; height: visible ? Appearance.menuActionHeight : 0; radius: Appearance.menuActionRadius; alignedIcon: true; iconName: "log-out"; label: root.environmentSwitchPending ? "A regressar…" : "Voltar ao Hub"; accent: true
                        enabled: root.sessionKindReady && !root.environmentSwitchPending
                        onActivated: root.returnToHub()
                    }
                    Text { renderType: Text.QtRendering; visible: root.environmentSwitchError.length > 0; width: parent.width; wrapMode: Text.WordWrap; text: root.environmentSwitchError; color: "#ff91a4"; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                }

                    Column {
                    width: parent.width
                    spacing: 5
                    visible: root.popupKind === "controls" && !root.renderedControls.shortcutsOpen && !root.renderedControls.controlsMoreOpen



                    ControlDashboard {
                        id: compactDashboard
                        displayScale: popupBackground.renderScale
                        topCornerRadius: popupBackground.radius
                        width: parent.width
                        visible: root.renderedControlsAllClosed() && !root.renderedControls.powerConfirmOpen
                        controller: root
                    }
                    Column {
                        width: parent.width; spacing: 8
                        visible: root.renderedControls.controlsConnectivityOpen
                        MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar aos controlos"; onActivated: root.openControlSection("connectivity") }
                        Text { renderType: Text.QtRendering; leftPadding: Appearance.menuTitleInset; text: "Ligações"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }
                        ControlTile { width: parent.width; height: Appearance.menuActionHeight; showCaption: true; iconName: root.wifiDisplayPowered() ? "wifi" : "wifi-off"; caption: "Wi-Fi"; quiet: true; selected: root.wifiDisplayPowered(); iconActionEnabled: true; iconActionAvailable: !wifiPowerProcess.running; iconActionLabel: root.wifiDisplayPowered() ? "Desativar Wi-Fi" : "Ativar Wi-Fi"; onIconActivated: root.toggleWifiPower(); onActivated: root.openControlSection("wifi") }
                        ControlTile { width: parent.width; height: Appearance.menuActionHeight; showCaption: true; iconName: root.bluetoothDisplayPowered() ? "bluetooth" : "bluetooth-off"; caption: "Bluetooth"; quiet: true; selected: root.bluetoothDisplayPowered(); iconActionEnabled: true; iconActionAvailable: !bluetoothPowerProcess.running && !root.bluetoothPowerPhase.length; iconActionLabel: root.bluetoothDisplayPowered() ? "Desativar Bluetooth" : "Ativar Bluetooth"; onIconActivated: root.toggleBluetoothPower(); onActivated: root.openControlSection("bluetooth") }
                        ControlTile { width: parent.width; height: Appearance.menuActionHeight; showCaption: true; iconName: "plane"; caption: "Modo de avião"; quiet: true; selected: root.airplaneMode; iconActionEnabled: true; iconActionAvailable: !DesktopActivity.busy; iconActionLabel: root.airplaneMode ? "Desativar modo de avião" : "Ativar modo de avião"; onIconActivated: DesktopActivity.action(["airplane", root.airplaneMode ? "off" : "on"]); onActivated: root.openActivitySection("airplane") }
                    }
                    Column {
                        width: parent.width; spacing: 8
                        visible: root.renderedControls.controlsActivityKind === "airplane"
                        MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar às ligações"; onActivated: root.openControlSection("connectivity") }
                        Rectangle {
                            width: parent.width; height: 72; radius: Appearance.menuActionRadius
                            color: root.controlButtonSurface
                            RadioIconButton {
                                x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
                                iconName: "plane"; powered: root.airplaneMode
                                busy: DesktopActivity.busy
                                actionLabel: root.airplaneMode ? "Desativar modo de avião" : "Ativar modo de avião"
                                onActivated: DesktopActivity.action(["airplane", root.airplaneMode ? "off" : "on"])
                            }
                            Column {
                                anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset
                                anchors.right: parent.right; anchors.rightMargin: 12
                                anchors.verticalCenter: parent.verticalCenter; spacing: 4
                                Text { renderType: Text.QtRendering; text: "Modo de avião"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                                Text { renderType: Text.QtRendering; text: DesktopActivity.busy ? "A alterar…" : root.airplaneMode ? "Ativado" : "Desativado"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            }
                        }
                        Text { renderType: Text.QtRendering; text: "Comunicações afetadas"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                        Repeater {
                            model: [
                                {name: "Wi-Fi", icon: (root.airplaneWifiKnown ? root.airplaneWifiPowered : root.wifiDisplayPowered()) ? "wifi" : "wifi-off", powered: (root.airplaneWifiKnown ? root.airplaneWifiPowered : root.wifiDisplayPowered()), detail: "Internet e pesquisa de redes"},
                                {name: "Bluetooth", icon: (root.airplaneBluetoothKnown ? root.airplaneBluetoothPowered : root.bluetoothDisplayPowered()) ? "bluetooth" : "bluetooth-off", powered: (root.airplaneBluetoothKnown ? root.airplaneBluetoothPowered : root.bluetoothDisplayPowered()), detail: "Ligações e pesquisa de dispositivos"}
                            ]
                            Rectangle {
                                required property var modelData
                                width: parent.width; height: 72; radius: Appearance.menuActionRadius
                                color: root.controlButtonSurface
                                Rectangle {
                                    x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
                                    width: Appearance.menuIconCircleSize; height: width; radius: width / 2
                                    color: Qt.lighter(root.controlButtonSurface, 1.6)
                                    LucideIcon { anchors.centerIn: parent; width: Appearance.menuGlyphSize; height: width; name: modelData.icon; opacity: modelData.powered ? 1 : .55 }
                                }
                                Text { renderType: Text.QtRendering;
                                    id: airplaneServiceState
                                    anchors.right: parent.right; anchors.rightMargin: 12; y: 14
                                    text: modelData.powered ? "Ligado" : "Desligado"
                                    color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                }
                                Text { renderType: Text.QtRendering;
                                    anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset
                                    anchors.right: airplaneServiceState.left; anchors.rightMargin: 8; y: 12
                                    text: modelData.name; elide: Text.ElideRight
                                    color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                }
                                Text { renderType: Text.QtRendering;
                                    anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset
                                    anchors.right: parent.right; anchors.rightMargin: 12; y: 38
                                    text: modelData.detail; wrapMode: Text.WordWrap
                                    color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize
                                }
                            }
                        }
                        Text { renderType: Text.QtRendering;
                            width: parent.width; wrapMode: Text.WordWrap
                            text: root.airplaneMode ? "Wi-Fi e Bluetooth bloqueados pelo modo de avião." : "Ao ativar, o Wi-Fi e o Bluetooth serão desativados."
                            color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                        }
                    }
                    Column {
                        width: parent.width; spacing: 8
                        visible: root.renderedControls.controlsActivityKind === "keyboard"
                        MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar ao som e brilho"; onActivated: root.openControlSection("brightness") }
                        Rectangle {
                            width: parent.width; height: 72; radius: Appearance.menuActionRadius
                            color: root.controlButtonSurface
                            RadioIconButton {
                                x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
                                iconName: "keyboard"; powered: root.keyboardBrightness > 0
                                busy: keyboardBrightnessProcess.running
                                actionLabel: "Alterar iluminação do teclado"
                                onActivated: root.cycleKeyboardBrightness()
                            }
                            Column {
                                anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset
                                anchors.right: parent.right; anchors.rightMargin: 12
                                anchors.verticalCenter: parent.verticalCenter; spacing: 4
                                Text { renderType: Text.QtRendering; text: "Iluminação do teclado"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                                Text { renderType: Text.QtRendering; text: keyboardBrightnessProcess.running ? "A alterar…" : root.keyboardBrightness > 0 ? "Ligada" : "Desligada"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            }
                        }
                        Text { renderType: Text.QtRendering; text: "Intensidade atual"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                        Rectangle {
                            width: parent.width; height: 92; radius: Appearance.menuActionRadius
                            color: root.controlButtonSurface
                            Text { renderType: Text.QtRendering;
                                x: 14; y: 14
                                text: "Nível " + root.keyboardBrightness + " de " + root.keyboardBrightnessMax
                                color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                            }
                            Text { renderType: Text.QtRendering;
                                anchors.right: parent.right; anchors.rightMargin: 14; y: 10
                                text: (root.keyboardBrightnessMax > 0 ? Math.round(root.keyboardBrightness * 100 / root.keyboardBrightnessMax) : 0) + "%"
                                color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold
                            }
                            Row {
                                x: 14; anchors.bottom: parent.bottom; anchors.bottomMargin: 18
                                width: parent.width - 28; spacing: 6
                                Repeater {
                                    model: Math.max(0, root.keyboardBrightnessMax)
                                    Rectangle {
                                        required property int index
                                        width: (parent.width - Math.max(0, root.keyboardBrightnessMax - 1) * 6) / Math.max(1, root.keyboardBrightnessMax)
                                        height: 8; radius: 4
                                        color: index < root.keyboardBrightness ? root.textMain : root.controlButtonOutline
                                    }
                                }
                            }
                        }
                        Text { renderType: Text.QtRendering; visible: root.hardwareControlError.length > 0; width: parent.width; text: root.hardwareControlError; wrapMode: Text.WordWrap; color: "#ff91a4"; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                    }
                    ActivityPanel {
                        width: parent.width
                        visible: root.renderedControls.controlsActivityKind.length > 0 && ["airplane", "keyboard", "trackpad"].indexOf(root.renderedControls.controlsActivityKind) < 0
                        kind: root.renderedControls.controlsActivityKind
                        onBack: { root.controlsActivityKind = ""; menuFlick.contentY = 0 }
                    }

                    Column {
                        width: parent.width; spacing: 8
                        visible: root.renderedControls.controlsWifiOpen
                        MenuButton { outlined: true; iconName: "chevron-left"; label: root.wifiPasswordVisible ? "Escolher outra rede" : "Voltar às ligações"; enabled: !wifiCredentialProcess.running && !hostActionProcess.running; onActivated: { if (root.wifiPasswordVisible) root.cancelWifiPassword(); else root.openControlSection("wifi") } }
                        Text { renderType: Text.QtRendering; leftPadding: Appearance.menuTitleInset; text: "Wi-Fi"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }
                        Rectangle {
                            visible: !root.wifiPasswordVisible
                            width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius
                            color: root.controlButtonSurface
                            RadioIconButton {
                                x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
                                iconName: root.wifiDisplayPowered() ? "wifi" : "wifi-off"
                                cardOutlineEnabled: false
                                powered: root.wifiDisplayPowered()
                                busy: wifiPowerProcess.running
                                actionLabel: root.wifiDisplayPowered() ? "Desativar Wi-Fi" : "Ativar Wi-Fi"
                                onActivated: root.toggleWifiPower()
                            }
                            Column {
                                anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset; anchors.right: disconnectButton.left; anchors.rightMargin: 10
                                anchors.verticalCenter: parent.verticalCenter; spacing: 3
                                Item {
                                    width: parent.width; height: currentWifiName.implicitHeight
                                    property int signalStrength: root.wifiCurrentSignal()
                                    Text { renderType: Text.QtRendering;
                                        id: currentWifiName
                                        anchors.left: parent.left; anchors.right: currentWifiSignal.left
                                        anchors.rightMargin: currentWifiSignal.visible ? 6 : 0
                                        elide: Text.ElideRight
                                        text: !root.wifiDisplayPowered() ? "Wi-Fi desativado" : (root.wifiDisplayActive() ? root.hostState.network_name : (root.wifiTogglePhase === "connecting" ? "A ligar…" : "Sem ligação"))
                                        color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                    }
                                    Text { renderType: Text.QtRendering;
                                        id: currentWifiSignal
                                        anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                                        visible: parent.signalStrength >= 0
                                        width: visible ? implicitWidth : 0
                                        text: parent.signalStrength + "%"
                                        color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                        Accessible.name: "Força do sinal: " + text
                                    }
                                }
                                Text { renderType: Text.QtRendering;
                                    visible: root.wifiDisplayActive()
                                    text: "Ligado"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize
                                }
                            }
                            MenuButton {
                                id: disconnectButton
                                visible: root.wifiDisplayActive() && root.wifiTogglePhase !== "connecting"
                                anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter
                                width: visible ? 104 : 0; height: 32; radius: Appearance.menuActionRadius
                                label: "Desconectar"
                                brightActionHover: true
                                actionSurface: parent.color
                                onActivated: { root.cancelWifiPassword(); root.toggleWifiConnection() }
                            }
                        }
                        Row {
                            visible: !root.wifiPasswordVisible && root.wifiDisplayPowered() && !!root.hostState.network_name && ["portal", "limited", "none"].indexOf(root.hostState.network_connectivity) >= 0
                            width: parent.width; height: visible ? 32 : 0; spacing: 8
                            Text { renderType: Text.QtRendering;
                                anchors.verticalCenter: parent.verticalCenter
                                text: root.hostState.network_connectivity === "portal" ? "Iniciar sessão na rede" : "Sem acesso à Internet"
                                color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                            }
                            MenuButton { visible: root.hostState.network_connectivity === "portal"; height: Appearance.menuActionHeight; width: 112; label: "Abrir acesso"; onActivated: if (!wifiPortalProcess.running) wifiPortalProcess.running = true }
                        }
                        Text { renderType: Text.QtRendering;
                            visible: root.wifiDisplayPowered() && !root.wifiPasswordVisible
                            text: "Outras redes"; color: root.textDim
                            font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                        }
                        Rectangle {
                            id: wifiPasswordCard
                            visible: root.wifiPasswordVisible
                            width: parent.width
                            height: visible ? wifiCredentialFields.implicitHeight + 16 : 0
                            radius: Appearance.menuActionRadius
                            color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                            Column {
                                id: wifiCredentialFields
                                x: 8; y: 8; width: parent.width - 16; spacing: 8
                                Row {
                                    width: parent.width; spacing: 8; height: 40
                                    Rectangle {
                                        width: Appearance.menuIconCircleSize; height: width; radius: width / 2; color: root.controlButtonActive
                                        anchors.verticalCenter: parent.verticalCenter
                                        LucideIcon { anchors.centerIn: parent; name: "wifi"; width: Appearance.menuGlyphSize; height: width }
                                    }
                                    Column {
                                        width: parent.width - 46; anchors.verticalCenter: parent.verticalCenter; spacing: 3
                                        Text { renderType: Text.QtRendering; text: root.wifiSelectedSsid; width: parent.width; elide: Text.ElideRight; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                                        Text { renderType: Text.QtRendering; text: root.wifiIsKnown(root.wifiSelectedSsid) ? "Rede guardada" : (root.wifiIsOpen(root.wifiSelectedSsid) ? "Rede aberta" : (root.wifiIsEnterprise(root.wifiSelectedSsid) ? "Rede da organização" : "Rede protegida")); color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                    }
                                }
                                Text { renderType: Text.QtRendering;
                                    visible: root.wifiIsKnown(root.wifiSelectedSsid) || root.wifiIsOpen(root.wifiSelectedSsid)
                                    width: parent.width; wrapMode: Text.Wrap
                                    text: root.wifiIsKnown(root.wifiSelectedSsid) ? "As credenciais guardadas serão usadas para ligar." : "Esta rede não pede palavra-passe."
                                    color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                }
                                Row {
                                    visible: root.wifiIsEnterprise(root.wifiSelectedSsid) && !root.wifiIsKnown(root.wifiSelectedSsid)
                                    width: parent.width; spacing: 6
                                    MenuButton { width: (parent.width - 12) / 3; height: Appearance.menuActionHeight; label: "PEAP"; accent: root.wifiEnterpriseMethod === "PEAP"; onActivated: root.wifiEnterpriseMethod = "PEAP" }
                                    MenuButton { width: (parent.width - 12) / 3; height: Appearance.menuActionHeight; label: "TTLS/PAP"; accent: root.wifiEnterpriseMethod === "TTLS-PAP"; onActivated: root.wifiEnterpriseMethod = "TTLS-PAP" }
                                    MenuButton { width: (parent.width - 12) / 3; height: Appearance.menuActionHeight; label: "TTLS/MS"; accent: root.wifiEnterpriseMethod === "TTLS-MSCHAPV2"; onActivated: root.wifiEnterpriseMethod = "TTLS-MSCHAPV2" }
                                }
                                Text { renderType: Text.QtRendering; visible: wifiUsernameField.visible; text: "Utilizador"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                Rectangle {
                                    id: wifiUsernameField
                                    visible: root.wifiIsEnterprise(root.wifiSelectedSsid) && !root.wifiIsKnown(root.wifiSelectedSsid)
                                    width: parent.width; height: visible ? 40 : 0; radius: 9; color: root.controlButtonActive
                                    enabled: !wifiCredentialProcess.running && !hostActionProcess.running
                                    border.width: wifiUsernameInput.activeFocus ? 1 : 0; border.color: root.textMain
                                    TextInput {
                                        id: wifiUsernameInput
                                        Accessible.name: "Utilizador"
                                        activeFocusOnTab: true
                                        Keys.onPressed: function(event) {
                                            if (event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab)
                                                root.navigateGenericMenu(event)
                                        }
                                        onActiveFocusChanged: {
                                            if (activeFocus) {
                                                root.clearPendingMenuFocus()
                                                root.focusedMenuItem = wifiUsernameInput
                                            }
                                        }
                                        anchors.fill: parent; anchors.leftMargin: 9; verticalAlignment: TextInput.AlignVCenter; text: root.wifiUsername; onTextChanged: root.wifiUsername = text; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                    }
                                    Text { renderType: Text.QtRendering; visible: !wifiUsernameInput.text.length; anchors.left: parent.left; anchors.leftMargin: 9; anchors.verticalCenter: parent.verticalCenter; text: "nome@instituição.pt"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                }
                                Text { renderType: Text.QtRendering; visible: wifiPasswordField.visible; text: "Palavra-passe"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                Rectangle {
                                    id: wifiPasswordField
                                    visible: !root.wifiIsKnown(root.wifiSelectedSsid) && !root.wifiIsOpen(root.wifiSelectedSsid)
                                    width: parent.width; height: visible ? 40 : 0; radius: 9; color: root.controlButtonActive; enabled: !wifiCredentialProcess.running && !hostActionProcess.running; border.width: wifiPasswordInput.activeFocus ? 1 : 0; border.color: root.textMain
                                    TextInput {
                                        id: wifiPasswordInput; Accessible.name: "Palavra-passe"; anchors.fill: parent; anchors.leftMargin: 9; anchors.rightMargin: 94; verticalAlignment: TextInput.AlignVCenter
                                        activeFocusOnTab: true
                                        Keys.onPressed: function(event) {
                                            if (event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab)
                                                root.navigateGenericMenu(event)
                                        }
                                        onActiveFocusChanged: {
                                            if (activeFocus) {
                                                root.clearPendingMenuFocus()
                                                root.focusedMenuItem = wifiPasswordInput
                                            }
                                        }
                                        text: root.wifiPassword; onTextChanged: root.wifiPassword = text; echoMode: root.wifiShowPassword ? TextInput.Normal : TextInput.Password; passwordCharacter: "•"
                                        color: root.textMain; selectionColor: root.controlButtonOutline; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                        onAccepted: root.submitWifiPassword()
                                    }
                                    MenuButton {
                                        anchors.right: parent.right; anchors.rightMargin: 5; anchors.verticalCenter: parent.verticalCenter
                                        id: wifiPasswordToggle
                                        lighterSurface: true
                                        width: 84; height: parent.height - 10; radius: 6; label: root.wifiShowPassword ? "Ocultar" : "Mostrar"
                                        onActivated: { root.wifiShowPassword = !root.wifiShowPassword; if (!root.menuKeyboardNavigation) wifiPasswordInput.forceActiveFocus() }
                                    }
                                    Text { renderType: Text.QtRendering; anchors.left: parent.left; anchors.leftMargin: 9; anchors.verticalCenter: parent.verticalCenter; visible: !wifiPasswordInput.text.length; anchors.right: wifiPasswordToggle.left; anchors.rightMargin: 8; elide: Text.ElideRight; text: "Introduz a palavra-passe"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                }
                                Text { renderType: Text.QtRendering; visible: wifiDomainField.visible; text: "Domínio do servidor"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                Rectangle {
                                    id: wifiDomainField
                                    visible: root.wifiIsEnterprise(root.wifiSelectedSsid) && !root.wifiIsKnown(root.wifiSelectedSsid)
                                    width: parent.width; height: visible ? 40 : 0; radius: 9; color: root.controlButtonActive
                                    enabled: !wifiCredentialProcess.running && !hostActionProcess.running
                                    border.width: wifiDomainInput.activeFocus ? 1 : 0; border.color: root.textMain
                                    TextInput {
                                        id: wifiDomainInput
                                        Accessible.name: "Domínio do servidor"
                                        activeFocusOnTab: true
                                        Keys.onPressed: function(event) {
                                            if (event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab)
                                                root.navigateGenericMenu(event)
                                        }
                                        onActiveFocusChanged: {
                                            if (activeFocus) {
                                                root.clearPendingMenuFocus()
                                                root.focusedMenuItem = wifiDomainInput
                                            }
                                        }
                                        anchors.fill: parent; anchors.leftMargin: 9; verticalAlignment: TextInput.AlignVCenter; text: root.wifiDomain; onTextChanged: root.wifiDomain = text; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                    }
                                    Text { renderType: Text.QtRendering; visible: !wifiDomainInput.text.length; anchors.left: parent.left; anchors.leftMargin: 9; anchors.verticalCenter: parent.verticalCenter; text: "wifi.escola.pt"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                }
                                Text { renderType: Text.QtRendering; visible: wifiCaField.visible; text: "Certificado CA"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                Rectangle {
                                    id: wifiCaField
                                    visible: root.wifiIsEnterprise(root.wifiSelectedSsid) && !root.wifiIsKnown(root.wifiSelectedSsid)
                                    width: parent.width; height: visible ? 40 : 0; radius: 9; color: root.controlButtonActive
                                    enabled: !wifiCredentialProcess.running && !hostActionProcess.running
                                    border.width: wifiCaInput.activeFocus ? 1 : 0; border.color: root.textMain
                                    TextInput {
                                        id: wifiCaInput
                                        Accessible.name: "Certificado CA"
                                        activeFocusOnTab: true
                                        Keys.onPressed: function(event) {
                                            if (event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab)
                                                root.navigateGenericMenu(event)
                                        }
                                        onActiveFocusChanged: {
                                            if (activeFocus) {
                                                root.clearPendingMenuFocus()
                                                root.focusedMenuItem = wifiCaInput
                                            }
                                        }
                                        anchors.fill: parent; anchors.leftMargin: 9; verticalAlignment: TextInput.AlignVCenter; text: root.wifiCaCert; onTextChanged: root.wifiCaCert = text; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                    }
                                }
                                Text { renderType: Text.QtRendering; visible: root.wifiIsEnterprise(root.wifiSelectedSsid) && !root.wifiIsKnown(root.wifiSelectedSsid); width: parent.width; wrapMode: Text.Wrap; text: "Verifica o domínio e o certificado da organização."; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                                Text { renderType: Text.QtRendering;
                                    visible: root.wifiMessage.length > 0; width: parent.width; wrapMode: Text.Wrap
                                    text: root.wifiMessage; color: root.wifiMessage.indexOf("A ligar") === 0 ? root.textDim : "#ffb0bd"
                                    font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                }
                                Row {
                                    width: parent.width; spacing: 8
                                    MenuButton {
                                        width: (parent.width - 8) / 2; height: Appearance.menuActionHeight; label: "Cancelar"
                                        enabled: !wifiCredentialProcess.running && !hostActionProcess.running
                                        onActivated: root.cancelWifiPassword()
                                    }
                                    MenuButton {
                                        width: (parent.width - 8) / 2; height: Appearance.menuActionHeight; accent: true
                                        label: (wifiCredentialProcess.running || hostActionProcess.running) ? "A ligar…" : "Ligar"
                                        enabled: !wifiCredentialProcess.running && !hostActionProcess.running && root.wifiSelectedSsid !== root.hostState.network_name
                                        onActivated: root.submitWifiPassword()
                                    }
                                }
                            }
                        }
                        Text { renderType: Text.QtRendering; visible: !root.wifiPasswordVisible && root.wifiMessage.length > 0; width: parent.width; wrapMode: Text.Wrap; text: root.wifiMessage; color: root.wifiMessage.indexOf("Não") === 0 ? "#ff91a4" : root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                        Repeater {
                            model: root.wifiDisplayPowered() && !root.wifiPasswordVisible ? root.wifiAvailableNetworks() : []
                            Rectangle {
                                required property string modelData
                                visible: modelData !== root.hostState.network_name
                                      && (!root.wifiPasswordVisible || modelData !== root.wifiSelectedSsid)
                                width: parent ? parent.width : 300; height: visible ? 40 : 0; radius: 10
                                color: root.controlButtonSurface
                                border.width: 0; border.color: root.controlButtonOutline
                                LucideIcon {
                                    name: root.wifiDetails(modelData).signal >= 50 ? "wifi" : (root.wifiDetails(modelData).signal >= 25 ? "wifi-high" : "wifi-low")
                                    width: Appearance.menuGlyphSize; height: width
                                    anchors.left: parent.left; anchors.leftMargin: Appearance.menuIconInset + (Appearance.menuIconCircleSize - Appearance.menuGlyphSize) / 2; anchors.verticalCenter: parent.verticalCenter
                                    opacity: .7
                                }
                                Text { renderType: Text.QtRendering;
                                    anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset; anchors.verticalCenter: parent.verticalCenter
                                    width: parent.width - 94; elide: Text.ElideRight
                                    text: modelData; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                }
                                LucideIcon {
                                    visible: !root.wifiIsOpen(modelData)
                                    name: "lock-keyhole"; width: 14; height: 14; opacity: .4
                                    anchors.right: parent.right; anchors.rightMargin: 14; anchors.verticalCenter: parent.verticalCenter
                                }
                                BounceMouseArea {
                                    id: nearbyWifiMouse
                                    anchors.fill: parent
                                    enabled: true
                                    hoverEnabled: true
                                    cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                                    onClicked: {
                                        root.cancelWifiPassword()
                                        root.wifiSelectionTap = true
                                        root.beginWifiConnect(modelData)
                                    }
                                }
                            }
                        }
                        Text { renderType: Text.QtRendering;
                            visible: root.wifiDisplayPowered() && !root.wifiPasswordVisible && !root.wifiAvailableNetworks().length
                            text: root.wifiDisplayActive() ? "Não há outras redes disponíveis" : "Nenhuma rede encontrada"
                            color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                        }
                    }

                    Column {
                        visible: root.renderedControls.controlsBluetoothOpen
                        width: parent.width; spacing: 8
                        MenuButton { outlined: true; iconName: "chevron-left"; label: root.bluetoothRemoveAddress.length ? "Voltar aos dispositivos" : "Voltar às ligações"; enabled: !bluetoothRemoveProcess.running; onActivated: { if (root.bluetoothRemoveAddress.length) { root.bluetoothRemoveAddress = ""; root.bluetoothRemoveName = "" } else root.openControlSection("bluetooth") } }
                        Text { renderType: Text.QtRendering; leftPadding: Appearance.menuTitleInset; text: "Bluetooth"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }
                        Column {
                            id: bluetoothContent
                            property bool formVisible: root.bluetoothPairPhase.length > 0 || root.bluetoothRemoveAddress.length > 0
                            width: parent.width; spacing: 8
                            Rectangle {
                                visible: !bluetoothContent.formVisible
                                width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; color: root.controlButtonSurface
                                RadioIconButton {
                                    x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
                                    iconName: root.bluetoothDisplayPowered() ? "bluetooth" : "bluetooth-off"
                                    powered: root.bluetoothDisplayPowered()
                                    busy: bluetoothPowerProcess.running || root.bluetoothPowerPhase.length > 0
                                    actionLabel: root.bluetoothDisplayPowered() ? "Desativar Bluetooth" : "Ativar Bluetooth"
                                    onActivated: root.toggleBluetoothPower()
                                }
                                Column {
                                    anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset
                                    anchors.right: bluetoothSearchButton.left; anchors.rightMargin: 10
                                    anchors.verticalCenter: parent.verticalCenter; spacing: 3
                                    Text { renderType: Text.QtRendering; width: parent.width; elide: Text.ElideRight; text: "Bluetooth"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                                    Text { renderType: Text.QtRendering; text: root.bluetoothDisplayPowered() ? "Ativo" : "Desativado"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                                }
                                MenuButton {
                                    id: bluetoothSearchButton
                                    visible: root.bluetoothDisplayPowered()
                                    anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter
                                    width: visible ? 104 : 0; height: 32; radius: Appearance.menuActionRadius
                                    label: bluetoothScanProcess.running ? "A procurar…" : "Procurar"
                                    brightActionHover: true
                                    actionSurface: parent.color
                                    enabled: !bluetoothScanProcess.running && !root.bluetoothPowerPhase.length
                                    onActivated: bluetoothScanProcess.running = true
                                }
                            }
                            Rectangle {
                                id: bluetoothPairCard
                                visible: root.bluetoothPairPhase.length > 0
                                width: parent.width; height: visible ? bluetoothPairFields.implicitHeight + 16 : 0
                                radius: Appearance.menuActionRadius; color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                                Column {
                                    id: bluetoothPairFields
                                    x: 8; y: 8; width: parent.width - 16; spacing: 8
                                    Row {
                                        width: parent.width; height: 40; spacing: 8
                                        Rectangle { width: Appearance.menuIconCircleSize; height: width; radius: width / 2; anchors.verticalCenter: parent.verticalCenter; color: Qt.lighter(root.controlButtonSurface, 1.6); LucideIcon { anchors.centerIn: parent; name: "bluetooth"; width: Appearance.menuGlyphSize; height: width } }
                                        Column {
                                            width: parent.width - 46; anchors.verticalCenter: parent.verticalCenter; spacing: 3
                                            Text { renderType: Text.QtRendering; width: parent.width; elide: Text.ElideRight; text: root.bluetoothPairName; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                                            Text { renderType: Text.QtRendering; text: "Emparelhar dispositivo"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                        }
                                    }
                                    Text { renderType: Text.QtRendering;
                                        width: parent.width; wrapMode: Text.Wrap
                                        text: root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "confirm" ? "Confirma que este código coincide no dispositivo." : (root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "pin" ? "Introduz o PIN apresentado pelo dispositivo." : (root.bluetoothPairPhase === "waiting-device" ? "Escreve este código no dispositivo Bluetooth." : (root.bluetoothMessage || "A aguardar o dispositivo…")))
                                        color: root.bluetoothPairPhase === "failed" ? "#ffb0bd" : root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                    }
                                    Rectangle {
                                        visible: root.bluetoothPairPasskey.length > 0
                                        width: parent.width; height: visible ? 52 : 0; radius: 9; color: root.controlButtonActive
                                        Text { renderType: Text.QtRendering; anchors.centerIn: parent; text: root.bluetoothPairPasskey; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: 24; font.letterSpacing: 4 }
                                    }
                                    Text { renderType: Text.QtRendering; visible: bluetoothPinField.visible; text: "PIN"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                    Rectangle {
                                        id: bluetoothPinField
                                        visible: root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "pin"
                                        width: parent.width; height: visible ? 40 : 0; radius: 9; color: root.controlButtonActive
                                        border.width: bluetoothPinInput.activeFocus ? 1 : 0; border.color: root.textMain
                                        enabled: !bluetoothPairRespondProcess.running
                                        TextInput {
                                            id: bluetoothPinInput
                                            anchors.fill: parent; anchors.leftMargin: 9; anchors.rightMargin: 94
                                            verticalAlignment: TextInput.AlignVCenter; activeFocusOnTab: true
                                            Accessible.name: "PIN do dispositivo Bluetooth"
                                            text: root.bluetoothPairPin; onTextChanged: root.bluetoothPairPin = text
                                            echoMode: root.bluetoothShowPin ? TextInput.Normal : TextInput.Password; maximumLength: 16
                                            color: root.textMain; selectionColor: root.controlButtonOutline; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                            Keys.onPressed: event => { if (event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab) root.navigateGenericMenu(event) }
                                            onActiveFocusChanged: if (activeFocus) { root.clearPendingMenuFocus(); root.focusedMenuItem = bluetoothPinInput }
                                            onAccepted: if (text.length) root.respondBluetoothPair(true, text)
                                        }
                                        MenuButton {
                                            anchors.right: parent.right; anchors.rightMargin: 5; anchors.verticalCenter: parent.verticalCenter
                                            width: 84; height: Appearance.menuActionHeight; lighterSurface: true; label: root.bluetoothShowPin ? "Ocultar" : "Mostrar"
                                            onActivated: { root.bluetoothShowPin = !root.bluetoothShowPin; if (!root.menuKeyboardNavigation) bluetoothPinInput.forceActiveFocus() }
                                        }
                                    }
                                    Row {
                                        width: parent.width; spacing: 8
                                        MenuButton {
                                            width: root.bluetoothPairPhase === "needs-response" ? (parent.width - 8) / 2 : parent.width; height: Appearance.menuActionHeight
                                            label: root.bluetoothPairPhase === "completed" || root.bluetoothPairPhase === "failed" ? "Fechar" : (root.bluetoothPairPhase === "needs-response" ? "Cancelar" : "A aguardar…")
                                            enabled: !bluetoothPairBeginProcess.running && !bluetoothPairRespondProcess.running && ["needs-response", "completed", "failed"].indexOf(root.bluetoothPairPhase) >= 0
                                            onActivated: root.bluetoothPairPhase === "needs-response" ? root.cancelBluetoothPairing() : root.dismissBluetoothPairing()
                                        }
                                        MenuButton {
                                            visible: root.bluetoothPairPhase === "needs-response"
                                            width: (parent.width - 8) / 2; height: Appearance.menuActionHeight; accent: true
                                            label: root.bluetoothPairChallenge === "pin" ? "Emparelhar" : "Confirmar"
                                            enabled: !bluetoothPairRespondProcess.running && (root.bluetoothPairChallenge !== "pin" || root.bluetoothPairPin.length > 0)
                                            onActivated: root.respondBluetoothPair(true, root.bluetoothPairChallenge === "pin" ? root.bluetoothPairPin : "")
                                        }
                                    }
                                }
                            }
                            Rectangle {
                                id: bluetoothForgetCard
                                visible: root.bluetoothRemoveAddress.length > 0
                                width: parent.width; height: visible ? bluetoothForgetFields.implicitHeight + 16 : 0
                                radius: Appearance.menuActionRadius; color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                                Column {
                                    id: bluetoothForgetFields
                                    x: 8; y: 8; width: parent.width - 16; spacing: 8
                                    Text { renderType: Text.QtRendering; width: parent.width; elide: Text.ElideRight; text: root.bluetoothRemoveName; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                                    Text { renderType: Text.QtRendering; width: parent.width; wrapMode: Text.Wrap; text: "Esquecer este dispositivo? Para voltar a usá-lo, será necessário emparelhar novamente."; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                    Row {
                                        width: parent.width; spacing: 8
                                        MenuButton { width: (parent.width - 8) / 2; height: Appearance.menuActionHeight; label: "Cancelar"; enabled: !bluetoothRemoveProcess.running; onActivated: { root.bluetoothRemoveAddress = ""; root.bluetoothRemoveName = "" } }
                                        MenuButton { width: (parent.width - 8) / 2; height: Appearance.menuActionHeight; label: bluetoothRemoveProcess.running ? "A esquecer…" : "Esquecer"; enabled: !bluetoothRemoveProcess.running; onActivated: root.confirmBluetoothRemove() }
                                    }
                                }
                            }
                            Text { renderType: Text.QtRendering; visible: !bluetoothContent.formVisible && root.bluetoothMessage.length > 0; width: parent.width; wrapMode: Text.Wrap; text: root.bluetoothMessage; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            Text { renderType: Text.QtRendering; visible: !bluetoothContent.formVisible && root.bluetoothConnectedDevices().length > 0; text: "Ligados"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            Repeater {
                                model: bluetoothContent.formVisible ? [] : root.bluetoothConnectedDevices()
                                BluetoothDeviceRow {
                                    required property var modelData
                                    device: modelData; connected: true; paired: modelData.paired === true
                                    onActivated: root.bluetoothDeviceAction("bluetooth-disconnect", modelData)
                                }
                            }
                            Text { renderType: Text.QtRendering; visible: !bluetoothContent.formVisible && root.bluetoothKnownDevices().length > 0; text: "Guardados"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            Repeater {
                                model: bluetoothContent.formVisible ? [] : root.bluetoothKnownDevices()
                                BluetoothDeviceRow {
                                    required property var modelData
                                    device: modelData; paired: true
                                    onActivated: root.bluetoothDeviceAction("bluetooth-connect", modelData)
                                    onForgetRequested: root.beginBluetoothRemove(modelData)
                                }
                            }
                            Text { renderType: Text.QtRendering; visible: !bluetoothContent.formVisible && root.bluetoothAvailableDevices().length > 0; text: "Disponíveis"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            Repeater {
                                model: bluetoothContent.formVisible ? [] : root.bluetoothAvailableDevices()
                                BluetoothDeviceRow {
                                    required property var modelData
                                    device: modelData
                                    onActivated: root.beginBluetoothPair(modelData)
                                }
                            }
                            Text { renderType: Text.QtRendering; visible: !bluetoothContent.formVisible && root.bluetoothDisplayPowered() && !bluetoothScanProcess.running && !root.bluetoothKnownDevices().length && !root.bluetoothConnectedDevices().length && !root.bluetoothAvailableDevices().length && !root.bluetoothMessage.length; width: parent.width; wrapMode: Text.Wrap; text: "Nenhum dispositivo encontrado"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                        }
                    }

                    Text { renderType: Text.QtRendering;
                        visible: root.renderedControlsAllClosed() && root.hardwareControlError.length > 0
                        width: parent.width; text: root.hardwareControlError; color: "#ff91a4"
                        wrapMode: Text.WordWrap; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize
                    }
                    Column {
                        width: parent.width; spacing: 8
                        visible: root.renderedControls.controlsBrightnessOpen
                        MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar aos controlos"; onActivated: root.openControlSection("brightness") }
                        Rectangle {
                            id: combinedVolumeCard
                            width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius
                            color: root.controlButtonSurface
                            BounceMouseArea {
                                id: combinedVolumeCardMouse
                                anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                Accessible.name: "Som"
                                onClicked: root.openControlSection("audio")
                            }
                                RadioIconButton {
                                    x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter; iconName: root.volumeMuted ? "volume-x" : "volume-2"
                                    powered: !root.volumeMuted; busy: localActionProcess.running
                                    actionLabel: root.volumeMuted ? "Reativar som" : "Silenciar som"
                                    onActivated: root.toggleVolumeMute()
                                }

                            Text { renderType: Text.QtRendering;
                                id: combinedVolumePercent
                                anchors.right: parent.right; anchors.rightMargin: 14
                                anchors.verticalCenter: parent.verticalCenter
                                width: 40; horizontalAlignment: Text.AlignRight
                                text: (root.volumeMuted ? 0 : root.volumeValue) + "%"; color: root.textDim
                                font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                            }
                            MenuSlider {
                                id: combinedVolumeSlider
                                anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset
                                anchors.right: combinedVolumePercent.left; anchors.rightMargin: 8
                                anchors.verticalCenter: parent.verticalCenter
                                height: 16; topPadding: 0; bottomPadding: 0; from: 0; to: 100; stepSize: 1; activeFocusOnTab: true
                                Accessible.name: "Som"
                                onKeyboardValueChanged: nextValue => root.commitVolume(nextValue)
                                onMoved: root.previewVolume(value)
                                onPressedChanged: { if (pressed) forceActiveFocus(); else root.commitVolume(value) }
                                Binding { target: combinedVolumeSlider; property: "value"; value: root.volumeMuted ? 0 : root.volumeValue; when: !combinedVolumeSlider.pressed }
                                background: Rectangle {
                                    x: combinedVolumeSlider.leftPadding; y: combinedVolumeSlider.topPadding + combinedVolumeSlider.availableHeight / 2 - height / 2
                                    width: combinedVolumeSlider.availableWidth; height: 5; radius: 3; color: root.controlButtonOutline
                                    Rectangle { width: combinedVolumeSlider.visualPosition * parent.width; height: parent.height; radius: 3; color: root.textMain }
                                }
                                handle: Item { width: 0; height: 0 }
                            }
                        }
                        Rectangle {
                            id: combinedBrightnessCard
                            width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius
                            color: root.controlButtonSurface
                            BounceMouseArea {
                                id: combinedBrightnessCardMouse
                                anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                Accessible.name: "Brilho do ecrã"
                                onClicked: root.toggleDisplayDim()
                            }
                                RadioIconButton {
                                    x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter; iconName: "sun"
                                    powered: root.displayBrightness > 5; busy: displayBrightnessProcess.running
                                    actionLabel: root.displayBrightness > 5 ? "Reduzir brilho" : "Restaurar brilho"
                                    onActivated: root.toggleDisplayDim()
                                }

                            Text { renderType: Text.QtRendering;
                                id: combinedBrightnessPercent
                                anchors.right: parent.right; anchors.rightMargin: 14
                                anchors.verticalCenter: parent.verticalCenter
                                width: 40; horizontalAlignment: Text.AlignRight
                                text: root.displayBrightness + "%"; color: root.textDim
                                font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                            }
                            MenuSlider {
                                id: displayBrightnessSlider
                                anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset
                                anchors.right: combinedBrightnessPercent.left; anchors.rightMargin: 8
                                anchors.verticalCenter: parent.verticalCenter
                                height: 16; topPadding: 0; bottomPadding: 0; from: 5; to: 100; stepSize: 1; activeFocusOnTab: true
                                Accessible.name: "Brilho do ecrã"
                                onKeyboardValueChanged: nextValue => root.commitDisplayBrightness(nextValue)
                                onMoved: root.previewDisplayBrightness(value)
                                onPressedChanged: { if (pressed) forceActiveFocus(); else root.commitDisplayBrightness(value) }
                                Binding { target: displayBrightnessSlider; property: "value"; value: root.displayBrightness; when: !displayBrightnessSlider.pressed }
                                background: Rectangle {
                                    x: displayBrightnessSlider.leftPadding; y: displayBrightnessSlider.topPadding + displayBrightnessSlider.availableHeight / 2 - height / 2
                                    width: displayBrightnessSlider.availableWidth; height: 5; radius: 3; color: root.controlButtonOutline
                                    Rectangle { width: displayBrightnessSlider.visualPosition * parent.width; height: parent.height; radius: 3; color: root.textMain }
                                }
                                handle: Item { width: 0; height: 0 }
                            }
                        }
                        ControlTile { width: parent.width; height: Appearance.menuActionHeight; quiet: true; showCaption: true; iconName: root.microphoneMuted ? "mic-off" : "mic"; caption: "Microfone"; selected: !root.microphoneMuted; iconActionEnabled: true; iconActionAvailable: !localActionProcess.running; iconActionLabel: root.microphoneMuted ? "Reativar microfone" : "Silenciar microfone"; onIconActivated: root.toggleMicrophoneMute(); onActivated: root.openControlSection("microphone") }
                        ControlTile { width: parent.width; height: Appearance.menuActionHeight; quiet: true; showCaption: true; iconName: "keyboard"; caption: "Iluminação do teclado"; selected: root.keyboardBrightness > 0; iconActionEnabled: true; iconActionAvailable: !keyboardBrightnessProcess.running; iconActionLabel: "Alterar iluminação do teclado"; onIconActivated: root.cycleKeyboardBrightness(); onActivated: root.openActivitySection("keyboard") }
                    }
                    Column {
                        visible: root.renderedControls.controlsAudioOpen
                        width: parent.width; spacing: 8
                        MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar a som e brilho"; onActivated: root.openControlSection("audio") }
                        Text { renderType: Text.QtRendering; leftPadding: Appearance.menuTitleInset; text: "Som"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }
                    }
                    Column {
                        width: parent.width; spacing: 8; visible: root.renderedControls.controlsAudioOpen

                        Rectangle {
                            width: parent.width; height: 80; radius: Appearance.menuActionRadius
                            color: root.controlButtonSurface; border.width: 0; border.color: root.controlButtonOutline
                            RadioIconButton {
                                x: 6; y: 3
                                iconName: root.volumeMuted ? "volume-x" : "volume-2"
                                powered: !root.volumeMuted; busy: localActionProcess.running
                                actionLabel: root.volumeMuted ? "Reativar som" : "Silenciar som"
                                onActivated: root.toggleVolumeMute()
                            }
                            Text { renderType: Text.QtRendering;
                                anchors.left: parent.left; anchors.leftMargin: 50; anchors.top: parent.top; anchors.topMargin: 12
                                text: root.volumeMuted ? "Volume silenciado" : "Volume de saída"
                                color: root.volumeMuted ? root.textDim : root.textMain
                                font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                            }
                            Text { renderType: Text.QtRendering;
                                anchors.right: parent.right; anchors.rightMargin: 12; anchors.top: parent.top; anchors.topMargin: 12
                                text: Math.round(volumeSlider.value) + "%"
                                color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                            }
                            MenuSlider {
                                id: volumeSlider
                                onKeyboardValueChanged: (nextValue) => root.commitVolume(nextValue)
                                anchors.left: parent.left; anchors.leftMargin: 16
                                anchors.right: parent.right; anchors.rightMargin: 14
                                anchors.bottom: parent.bottom; anchors.bottomMargin: 7
                                height: 28; from: 0; to: 100; stepSize: 1
                                activeFocusOnTab: true
                                enabled: !localActionProcess.running
                                onMoved: root.previewVolume(value)
                                onPressedChanged: {
                                    if (pressed)
                                        forceActiveFocus()
                                    else
                                        root.commitVolume(value)
                                }
                                Binding { target: volumeSlider; property: "value"; value: root.volumeMuted ? 0 : root.volumeValue; when: !volumeSlider.pressed }
                                background: Rectangle {
                                    x: volumeSlider.leftPadding
                                    y: volumeSlider.topPadding + volumeSlider.availableHeight / 2 - height / 2
                                    width: volumeSlider.availableWidth; height: 5; radius: 3; color: volumeSlider.keyboardEditing ? Qt.darker(root.cyan, 2.5) : root.controlButtonOutline
                                    Rectangle {
                                        width: volumeSlider.visualPosition * parent.width; height: parent.height; radius: 3
                                        color: volumeSlider.keyboardEditing ? root.cyan : (root.volumeMuted ? root.textDim : root.textMain)
                                    }
                                }
                                handle: Item { width: 0; height: 0 }
                            }
                        }


                    }

                    Column {
                        visible: root.renderedControls.controlsMicrophoneOpen
                        width: parent.width; spacing: 8
                        MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar a som e brilho"; onActivated: root.openControlSection("microphone") }
                        Text { renderType: Text.QtRendering; leftPadding: Appearance.menuTitleInset; text: "Microfone"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }
                    }
                    Column {
                        width: parent.width; spacing: 8; visible: root.renderedControls.controlsMicrophoneOpen
                        Rectangle {
                            width: parent.width; height: 80; radius: Appearance.menuActionRadius
                            color: root.controlButtonSurface; border.width: 0; border.color: root.controlButtonOutline
                            RadioIconButton {
                                x: 6; y: 3
                                iconName: root.microphoneMuted ? "mic-off" : "mic"
                                powered: !root.microphoneMuted; busy: localActionProcess.running
                                actionLabel: root.microphoneMuted ? "Reativar microfone" : "Silenciar microfone"
                                onActivated: root.toggleMicrophoneMute()
                            }
                            Text { renderType: Text.QtRendering; anchors.left: parent.left; anchors.leftMargin: 50; anchors.top: parent.top; anchors.topMargin: 12; text: root.microphoneMuted ? "Microfone silenciado" : "Volume de entrada"; color: root.microphoneMuted ? root.textDim : root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            Text { renderType: Text.QtRendering; anchors.right: parent.right; anchors.rightMargin: 12; anchors.top: parent.top; anchors.topMargin: 12; text: Math.round(microphoneSlider.value) + "%"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            MenuSlider {
                                id: microphoneSlider
                                onKeyboardValueChanged: (nextValue) => root.commitMicrophoneVolume(nextValue)
                                anchors.left: parent.left; anchors.leftMargin: 16; anchors.right: parent.right; anchors.rightMargin: 14
                                anchors.bottom: parent.bottom; anchors.bottomMargin: 7
                                height: 28; from: 0; to: 100; stepSize: 1; activeFocusOnTab: true
                                enabled: !localActionProcess.running
                                onPressedChanged: { if (pressed) forceActiveFocus(); else root.commitMicrophoneVolume(value) }
                                Binding { target: microphoneSlider; property: "value"; value: root.microphoneVolume; when: !microphoneSlider.pressed }
                                background: Rectangle {
                                    x: microphoneSlider.leftPadding; y: microphoneSlider.topPadding + microphoneSlider.availableHeight / 2 - height / 2
                                    width: microphoneSlider.availableWidth; height: 5; radius: 3; color: microphoneSlider.keyboardEditing ? Qt.darker(root.cyan, 2.5) : root.controlButtonOutline
                                    Rectangle { width: microphoneSlider.visualPosition * parent.width; height: parent.height; radius: 3; color: microphoneSlider.keyboardEditing ? root.cyan : (root.microphoneMuted ? root.textDim : root.textMain) }
                                }
                                handle: Item { width: 0; height: 0 }
                            }
                        }

                    }






                    Rectangle {
                        visible: root.renderedControlsAllClosed() && root.renderedControls.powerConfirmOpen
                        width: parent.width
                        height: visible ? 104 : 0
                        radius: 7
                        color: root.controlButtonSurface
                        border.width: 1
                        border.color: root.powerToken.length ? "#ffb15a" : root.controlButtonOutline
                        Column {
                            anchors.fill: parent
                            anchors.margins: 9
                            spacing: 8
                            Text { renderType: Text.QtRendering;
                                width: parent.width
                                text: root.powerMessage
                                color: root.powerToken.length ? "#ffd09a" : root.textDim
                                font.family: Appearance.fontFamily
                                font.pixelSize: root.menuBodySize
                                font.weight: Font.Normal
                                wrapMode: Text.Wrap
                            }
                            Row {
                                width: parent.width
                                spacing: 6
                                MenuButton {
                                    width: (parent.width - 6) / 2
                                    label: "Cancelar"
                                    onActivated: root.cancelPower()
                                }
                                MenuButton {
                                    visible: root.powerToken.length > 0
                                    width: (parent.width - 6) / 2
                                    label: root.powerBusy ? "A processar..." : "Confirmar"
                                    accent: true
                                    onActivated: root.confirmPower()
                                }
                            }
                        }
                    }

                }

                Column {
                    width: parent.width; spacing: 8
                    visible: root.popupKind === "controls" && root.renderedControls.controlsMoreOpen && !root.renderedControls.shortcutsOpen && !root.renderedControls.controlsAppearanceOpen && root.renderedControls.controlsActivityKind !== "trackpad"
                    MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar aos controlos"; onActivated: { root.controlsMoreOpen = false; menuFlick.contentY = 0 } }
                    MenuButton { height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; alignedIcon: true; iconName: "paintbrush"; label: "Personalização"; onActivated: { Appearance.refresh(); personalizationPanel.section = ""; root.controlsAppearanceOpen = true; menuFlick.contentY = 0 } }
                    Column {
                        visible: root.hasExternalDisplay; width: parent.width; spacing: 6
                        Text { renderType: Text.QtRendering; text: "Posição do monitor externo"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        Row {
                            width: parent.width; spacing: 6
                            MenuButton { width: (parent.width - 6) / 2; outlined: true; label: "À esquerda"; enabled: !displayLayoutProcess.running; onActivated: root.setDisplayLayout("left"); SelectionIndicator { visible: root.displayLayoutSide === "left" } }
                            MenuButton { width: (parent.width - 6) / 2; outlined: true; label: "À direita"; enabled: !displayLayoutProcess.running; onActivated: root.setDisplayLayout("right"); SelectionIndicator { visible: root.displayLayoutSide === "right" } }
                        }
                        Text { renderType: Text.QtRendering; text: "Super+Ctrl+Home traz o ponteiro para o portátil."; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                        Text { renderType: Text.QtRendering; visible: root.displayLayoutError.length > 0; width: parent.width; text: root.displayLayoutError; color: "#ff91a4"; wrapMode: Text.WordWrap; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                    }
                    Rectangle {
                        id: mouseSensitivityCard
                        width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; color: root.controlButtonSurface
                        border.width: 0; border.color: root.controlButtonOutline
                        RadioIconButton {
                            x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
                            cardHoverEnabled: false
                            iconName: root.pointerDevices.mouse.available && root.pointerDevices.mouse.enabled ? "mouse" : "mouse-off"; powered: root.pointerDevices.mouse.available && root.pointerDevices.mouse.enabled
                            actionLabel: (root.pointerDevices.mouse.enabled ? "Desativar" : "Ativar") + " rato"
                            busy: pointerPowerProcess.running || !root.pointerDevices.mouse.available
                            onActivated: root.togglePointer("mouse")
                        }
                        Text { renderType: Text.QtRendering; id: mouseSensitivityPercent; width: 46; horizontalAlignment: Text.AlignRight; anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; text: Math.round(mouseSensitivitySlider.value) + "%"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        MenuSlider {
                            id: mouseSensitivitySlider
                            anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset; anchors.right: mouseSensitivityPercent.left; anchors.rightMargin: 8
                            anchors.verticalCenter: parent.verticalCenter
                            height: 16; topPadding: 0; bottomPadding: 0; from: 0; to: 100; stepSize: 1
                            activeFocusOnTab: true
                            Accessible.name: "Sensibilidade do rato"
                            enabled: root.pointerDevices.mouse.available && root.pointerDevices.mouse.enabled
                            wheelEnabled: false
                            onKeyboardValueChanged: nextValue => root.setMouseSensitivity(nextValue)
                            property real draggedValue: value
                            property bool dragStarted: false
                            onMoved: draggedValue = value
                            onPressedChanged: {
                                if (pressed) { dragStarted = true; draggedValue = value }
                                else if (dragStarted) { dragStarted = false; root.setMouseSensitivity(draggedValue) }
                            }
                            Binding { target: mouseSensitivitySlider; property: "value"; value: (root.mouseSensitivity + 100) / 2; when: !mouseSensitivitySlider.pressed }
                            background: Rectangle {
                                x: mouseSensitivitySlider.leftPadding
                                y: mouseSensitivitySlider.topPadding + mouseSensitivitySlider.availableHeight / 2 - height / 2
                                width: mouseSensitivitySlider.availableWidth; height: 5; radius: 3
                                color: root.controlButtonOutline
                                Rectangle {
                                    width: mouseSensitivitySlider.visualPosition * parent.width; height: parent.height; radius: 3
                                    color: root.textMain
                                }
                            }
                            handle: Item { width: 0; height: 0 }
                        }
                    }
                    Text { renderType: Text.QtRendering; visible: root.mouseSensitivityError.length > 0; width: parent.width; text: root.mouseSensitivityError; color: "#ff91a4"; wrapMode: Text.WordWrap; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                    MenuButton { height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; alignedIcon: true; iconName: "touchpad"; label: "Trackpad"; onActivated: { root.controlsActivityKind = "trackpad"; menuFlick.contentY = 0 } }
                    MenuButton { height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; alignedIcon: true; iconName: "list"; label: "Lista de atalhos"; onActivated: { root.shortcutsOpen = true; menuFlick.contentY = 0 } }
                }

                Column {
                    id: trackpadSettingsPage
                    width: parent.width; spacing: 8
                    visible: root.popupKind === "controls" && root.renderedControls.controlsMoreOpen && root.renderedControls.controlsActivityKind === "trackpad" && !root.renderedControls.controlsAppearanceOpen && !root.renderedControls.shortcutsOpen
                    MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar às opções"; onActivated: { root.controlsActivityKind = ""; menuFlick.contentY = 0 } }
                    Rectangle {
                        id: trackpadSensitivityCard
                        width: parent.width; height: 72; radius: Appearance.menuActionRadius; color: root.controlButtonSurface
                        border.width: 0; border.color: root.controlButtonOutline
                        RadioIconButton {
                            x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
                            cardHoverEnabled: false
                            iconName: (root.pointerDevices.trackpad.available && root.pointerDevices.trackpad.enabled ? "mouse-pointer-2" : "touchpad-off"); powered: root.pointerDevices.trackpad.available && root.pointerDevices.trackpad.enabled
                            actionLabel: (root.pointerDevices.trackpad.enabled ? "Desativar" : "Ativar") + " trackpad"
                            busy: pointerPowerProcess.running || !root.pointerDevices.trackpad.available
                            onActivated: root.togglePointer("trackpad")
                        }
                        Text { renderType: Text.QtRendering; anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset; y: 12; text: "Cursor"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        Text { renderType: Text.QtRendering; id: trackpadSensitivityPercent; width: 46; horizontalAlignment: Text.AlignRight; anchors.right: parent.right; anchors.rightMargin: 12; y: 12; text: Math.round(trackpadSensitivitySlider.value) + "%"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        MenuSlider {
                            id: trackpadSensitivitySlider
                            anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset; anchors.right: trackpadSensitivityPercent.left; anchors.rightMargin: 8
                            y: 44
                            height: 16; topPadding: 0; bottomPadding: 0; from: 0; to: 100; stepSize: 1
                            activeFocusOnTab: true
                            directArrowAdjustment: true
                            Accessible.name: "Velocidade do cursor do trackpad"
                            enabled: root.pointerDevices.trackpad.available && root.pointerDevices.trackpad.enabled
                            wheelEnabled: false
                            onKeyboardValueChanged: nextValue => root.setTrackpadSensitivity(nextValue)
                            property real draggedValue: value
                            property bool dragStarted: false
                            onMoved: draggedValue = value
                            onPressedChanged: {
                                if (pressed) { dragStarted = true; draggedValue = value }
                                else if (dragStarted) { dragStarted = false; root.setTrackpadSensitivity(draggedValue) }
                            }
                            Binding { target: trackpadSensitivitySlider; property: "value"; value: (root.trackpadSensitivity + 100) / 2; when: !trackpadSensitivitySlider.pressed }
                            background: Rectangle {
                                x: trackpadSensitivitySlider.leftPadding
                                y: trackpadSensitivitySlider.topPadding + trackpadSensitivitySlider.availableHeight / 2 - height / 2
                                width: trackpadSensitivitySlider.availableWidth; height: 5; radius: 3
                                color: root.controlButtonOutline
                                Rectangle {
                                    width: trackpadSensitivitySlider.visualPosition * parent.width; height: parent.height; radius: 3
                                    color: root.textMain
                                }
                            }
                            handle: Item { width: 0; height: 0 }
                        }
                    }
                    Text { renderType: Text.QtRendering; visible: root.trackpadSensitivityError.length > 0; width: parent.width; text: root.trackpadSensitivityError; color: "#ff91a4"; wrapMode: Text.WordWrap; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                    Rectangle {
                        id: trackpadScrollCard
                        width: parent.width; height: 72; radius: Appearance.menuActionRadius; color: root.controlButtonSurface
                        Rectangle {
                            x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
                            width: Appearance.menuIconCircleSize; height: width; radius: width / 2
                            color: Qt.lighter(parent.color, 1.6)
                            LucideIcon { anchors.centerIn: parent; width: Appearance.menuGlyphSize; height: width; name: "arrow-up-down" }
                        }
                        Text { renderType: Text.QtRendering; anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset; y: 12; text: "Scroll"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        Text { renderType: Text.QtRendering; id: trackpadScrollPercent; width: 46; horizontalAlignment: Text.AlignRight; anchors.right: parent.right; anchors.rightMargin: 12; y: 12; text: Math.round(trackpadScrollSlider.value) + "%"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        MenuSlider {
                            id: trackpadScrollSlider
                            anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset; anchors.right: trackpadScrollPercent.left; anchors.rightMargin: 8
                            y: 44; height: 16; topPadding: 0; bottomPadding: 0
                            from: 0; to: 100; directArrowAdjustment: true; stepSize: 1; activeFocusOnTab: true
                            Accessible.name: "Sensibilidade de Scroll"
                            enabled: root.pointerDevices.trackpad.available && root.pointerDevices.trackpad.enabled
                            wheelEnabled: false
                            onKeyboardValueChanged: nextValue => root.setTrackpadGesture("scroll", nextValue)
                            property real draggedValue: value
                            property bool dragStarted: false
                            onMoved: draggedValue = value
                            onPressedChanged: {
                                if (pressed) { dragStarted = true; draggedValue = value }
                                else if (dragStarted) { dragStarted = false; root.setTrackpadGesture("scroll", draggedValue) }
                            }
                            Binding { target: trackpadScrollSlider; property: "value"; value: (root.trackpadGestures.scroll - 25) / 1.75; when: !trackpadScrollSlider.pressed }
                            background: Rectangle {
                                x: trackpadScrollSlider.leftPadding
                                y: trackpadScrollSlider.topPadding + trackpadScrollSlider.availableHeight / 2 - height / 2
                                width: trackpadScrollSlider.availableWidth; height: 5; radius: 3
                                color: root.controlButtonOutline
                                Rectangle { width: trackpadScrollSlider.visualPosition * parent.width; height: parent.height; radius: 3; color: root.textMain }
                            }
                            handle: Item { width: 0; height: 0 }
                        }
                    }
                    Rectangle {
                        id: trackpadWorkspacesCard
                        width: parent.width; height: 72; radius: Appearance.menuActionRadius; color: root.controlButtonSurface
                        Rectangle {
                            x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
                            width: Appearance.menuIconCircleSize; height: width; radius: width / 2
                            color: Qt.lighter(parent.color, 1.6)
                            LucideIcon { anchors.centerIn: parent; width: Appearance.menuGlyphSize; height: width; name: "square-stack" }
                        }
                        Text { renderType: Text.QtRendering; anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset; y: 12; text: "Workspaces"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        Text { renderType: Text.QtRendering; id: trackpadWorkspacesPercent; width: 46; horizontalAlignment: Text.AlignRight; anchors.right: parent.right; anchors.rightMargin: 12; y: 12; text: Math.round(trackpadWorkspacesSlider.value) + "%"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        MenuSlider {
                            id: trackpadWorkspacesSlider
                            anchors.left: parent.left; anchors.leftMargin: Appearance.menuLabelInset; anchors.right: trackpadWorkspacesPercent.left; anchors.rightMargin: 8
                            y: 44; height: 16; topPadding: 0; bottomPadding: 0
                            from: 0; to: 100; directArrowAdjustment: true; stepSize: 1; activeFocusOnTab: true
                            Accessible.name: "Sensibilidade de Workspaces"
                            enabled: root.pointerDevices.trackpad.available && root.pointerDevices.trackpad.enabled
                            wheelEnabled: false
                            onKeyboardValueChanged: nextValue => root.setTrackpadGesture("workspaces", nextValue)
                            property real draggedValue: value
                            property bool dragStarted: false
                            onMoved: draggedValue = value
                            onPressedChanged: {
                                if (pressed) { dragStarted = true; draggedValue = value }
                                else if (dragStarted) { dragStarted = false; root.setTrackpadGesture("workspaces", draggedValue) }
                            }
                            Binding { target: trackpadWorkspacesSlider; property: "value"; value: (root.trackpadGestures.workspaces - 25) / 1.75; when: !trackpadWorkspacesSlider.pressed }
                            background: Rectangle {
                                x: trackpadWorkspacesSlider.leftPadding
                                y: trackpadWorkspacesSlider.topPadding + trackpadWorkspacesSlider.availableHeight / 2 - height / 2
                                width: trackpadWorkspacesSlider.availableWidth; height: 5; radius: 3
                                color: root.controlButtonOutline
                                Rectangle { width: trackpadWorkspacesSlider.visualPosition * parent.width; height: parent.height; radius: 3; color: root.textMain }
                            }
                            handle: Item { width: 0; height: 0 }
                        }
                    }
                    Text { renderType: Text.QtRendering; visible: root.trackpadGesturesError.length > 0; width: parent.width; text: root.trackpadGesturesError; color: "#ff91a4"; wrapMode: Text.WordWrap; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                }

                PersonalizationPanel {
                    id: personalizationPanel
                    width: parent.width
                    visible: root.popupKind === "controls" && root.renderedControls.controlsMoreOpen && root.renderedControls.controlsAppearanceOpen && !root.renderedControls.shortcutsOpen
                    wallpapers: root.wallpaperSources
                    onBack: { root.controlsAppearanceOpen = false; menuFlick.contentY = 0 }
                    onNavigation: menuFlick.contentY = 0
                    onChooseImage: { root.closePopup(); Appearance.chooseWallpaper() }
                }

                Column {
                    width: parent.width; spacing: 7
                    visible: root.popupKind === "controls" && root.renderedControls.shortcutsOpen
                    MenuButton {
                        outlined: true; iconName: "chevron-left"; label: "Voltar às opções"
                        onActivated: { root.shortcutsOpen = false; menuFlick.contentY = 0 }
                    }
                    Repeater {
                        model: root.shortcutList
                        Rectangle {
                            id: shortcutRow
                            required property var modelData
                            // Match other menu cards: no opaque row under the pinned title.
                            opacity: root.menuButtonFits(shortcutRow) ? 1 : 0
                            width: parent.width; height: 28; radius: 6; color: root.controlButtonSurface
                            Text { renderType: Text.QtRendering;
                                anchors.fill: parent; anchors.leftMargin: 9; verticalAlignment: Text.AlignVCenter
                                text: modelData.keys + "  ·  " + modelData.action
                                color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                            }
                        }
                    }
                }

                    Column {
                    width: parent.width
                    spacing: 6
                    visible: root.popupKind === "wifi"
                    Text { renderType: Text.QtRendering;
                        text: "Status :: " + (root.hostState.network_name || "disconnected")
                        color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                    }
                    MenuButton { label: "[ SCAN ] procurar redes"; onActivated: root.hostAction("wifi-scan") }
                    MenuButton {
                        visible: !!root.hostState.network_name
                        label: "[ DISCONNECT ] rede atual"
                        onActivated: root.hostAction("wifi-disconnect")
                    }
                    Text { renderType: Text.QtRendering; text: "Known networks"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                    Repeater {
                        model: root.hostState.known_networks || []
                        MenuButton {
                            required property string modelData
                            visible: modelData !== root.hostState.network_name
                            label: "[ Connect ] " + modelData
                            onActivated: root.hostAction("wifi-connect", modelData)
                        }
                    }
                }

                    Column {
                    width: parent.width
                    spacing: 6
                    visible: root.popupKind === "bluetooth"
                    MenuButton {
                        label: root.hostState.bluetooth_powered ? "[ POWER ] desligar" : "[ POWER ] ligar"
                        accent: true
                        onActivated: root.hostAction("bluetooth-power", root.hostState.bluetooth_powered ? "off" : "on")
                    }
                    Text { renderType: Text.QtRendering; text: "Paired devices"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                    Repeater {
                        model: root.hostState.bluetooth_devices || []
                        MenuButton {
                            required property var modelData
                            label: "[ " + (modelData.connected ? "Disconnect" : "Connect") + " ] " + modelData.name
                            onActivated: root.hostAction(modelData.connected ? "bluetooth-disconnect" : "bluetooth-connect", modelData.address)
                        }
                    }
                    Text { renderType: Text.QtRendering;
                        visible: !(root.hostState.bluetooth_devices || []).length
                        text: "-- nenhum dispositivo emparelhado --"
                        color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                    }
                }

                    Column {
                    width: parent.width
                    spacing: 6
                    visible: root.popupKind === "audio"
                    Text { renderType: Text.QtRendering; text: "Output :: " + root.volumeText; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                    MenuButton { label: "[ + 5% ] aumentar volume"; accent: true; onActivated: root.localAction(["/usr/bin/wpctl", "set-volume", "-l", "1", "@DEFAULT_AUDIO_SINK@", "5%+"]) }
                    MenuButton { label: "[ - 5% ] diminuir volume"; onActivated: root.localAction(["/usr/bin/wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"]) }
                    MenuButton { label: "[ MUTE ] alternar som"; onActivated: root.localAction(["/usr/bin/wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"]) }
                }

                    Column {
                    width: parent.width
                    spacing: 12
                    visible: root.popupKind === "battery"
                    Rectangle {
                        width: parent.width; height: root.batteryDischarging ? 130 : 98; radius: 14; color: root.controlButtonSurface
                        Text { renderType: Text.QtRendering; id: batteryCapacity; x: 14; y: 10; text: root.batteryText; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: 28; font.weight: Font.DemiBold }
                        Text { renderType: Text.QtRendering;
                            x: 14; y: 45; width: parent.width - 28
                            text: root.batteryStatus; elide: Text.ElideRight
                            color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                        }
                        Rectangle {
                            x: 14; y: 77; width: parent.width - 28; height: 6; radius: 3; color: root.controlButtonOutline
                            Rectangle { height: parent.height; radius: 3; color: parseInt(root.batteryText) <= 20 ? "#ffb15a" : "#9dc8bd"; width: parent.width * Math.max(0, Math.min(100, parseInt(root.batteryText) || 0)) / 100 }
                        }
                        LucideIcon { visible: root.batteryDischarging; x: 14; y: 99; width: Appearance.menuGlyphSize; height: width; name: "battery"; tint: root.textDim }
                        Text { renderType: Text.QtRendering;
                            visible: root.batteryDischarging
                            x: 38; y: 99; width: parent.width - 52; elide: Text.ElideRight
                            text: root.batteryMinutes >= 0 ? "Restam cerca de " + Math.floor(root.batteryMinutes / 60) + " h " + (root.batteryMinutes % 60) + " min" : "Autonomia indisponível"
                            color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                        }
                    }
                    Text { renderType: Text.QtRendering;
                        visible: root.hardwareStatusError.length > 0
                        width: parent.width; wrapMode: Text.WordWrap
                        text: "Controlos de energia indisponíveis. " + root.hardwareStatusError
                        color: "#ff91a4"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
                    }


                    Text { renderType: Text.QtRendering; width: parent.width; text: "Modo de energia"; elide: Text.ElideRight; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                    Column {
                        id: energyModeRow
                        width: parent.width; spacing: 8
                        Repeater {
                            model: [
                                { profile: "low-power", label: "Poupar", icon: "leaf" },
                                { profile: "balanced", label: "Equilibrado", icon: "scale" },
                                { profile: "performance", label: "Desempenho", icon: "zap" }
                            ]
                            MenuButton {
                                required property var modelData
                                width: energyModeRow.width
                                height: Appearance.menuActionHeight
                                alignedIcon: true; iconName: modelData.icon; label: modelData.label
                                selected: root.hardwareProfile.platform_profile === modelData.profile
                                accent: selected
                                enabled: !root.hardwareBusy && (root.hardwareProfile.platform_profiles || []).indexOf(modelData.profile) >= 0
                                Accessible.role: Accessible.RadioButton
                                Accessible.name: modelData.label
                                Accessible.checkable: true; Accessible.checked: selected
                                onActivated: root.setPlatformProfile(modelData.profile)
                            }
                        }
                    }
                    Text { renderType: Text.QtRendering;
                        visible: root.hardwareMessage.length > 0 && !root.hardwareConfirmOpen
                        text: root.hardwareMessage; color: root.platformProfileError.length ? "#ff91a4" : root.textDim; wrapMode: Text.WordWrap
                        width: parent.width; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
                    }
                    Rectangle {
                        width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius
                        color: "transparent"; border.width: 1; border.color: root.controlButtonOutline
                        antialiasing: true
                        enabled: !root.hardwareConfirmOpen
                        opacity: enabled ? 1 : .42
                        Accessible.role: Accessible.Button
                        Accessible.name: root.batteryDetailsOpen ? "Ocultar detalhes e gráficos" : "Mostrar detalhes e gráficos"
                        LucideIcon { x: 12; anchors.verticalCenter: parent.verticalCenter; width: Appearance.menuGlyphSize; height: width; name: "list"; tint: root.textMain }
                        Text { renderType: Text.QtRendering;
                            x: 38; width: parent.width - 76; anchors.verticalCenter: parent.verticalCenter
                            text: "Detalhes e gráficos"; elide: Text.ElideRight
                            color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                        }
                        LucideIcon {
                            anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter
                            width: Appearance.menuGlyphSize; height: width; name: "chevron-right"; tint: root.textMain
                            rotation: root.batteryDetailsOpen ? 270 : 90
                            Behavior on rotation { NumberAnimation { duration: 220; easing.type: Easing.OutCubic } }
                        }
                        BounceMouseArea {
                            anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                            onClicked: root.batteryDetailsOpen = !root.batteryDetailsOpen
                        }
                    }
                    Column {
                        width: parent.width; spacing: 12
                        visible: root.batteryDetailsOpen || root.hardwareConfirmOpen
                        Row {
                            width: parent.width; spacing: 8
                            Repeater {
                                model: [
                                    { title: "Potência", icon: "zap", value: root.batteryWatts >= 0 ? root.batteryWatts.toFixed(1) + " W" : "—" },
                                    { title: "Saúde", icon: "cross", value: root.batteryHealth >= 0 ? root.batteryHealth + "%" : "—" }
                                ]
                                Rectangle {
                                    required property var modelData
                                    width: (parent.width - 8) / 2; height: 72; radius: 14; color: root.controlButtonSurface
                                    LucideIcon { x: 12; anchors.verticalCenter: parent.verticalCenter; width: Appearance.menuGlyphSize; height: width; name: modelData.icon }
                                    Text { renderType: Text.QtRendering; x: 40; y: 14; width: parent.width - 50; text: modelData.title; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                                    Text { renderType: Text.QtRendering; x: 40; y: 36; width: parent.width - 50; text: modelData.value; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                                }
                            }
                        }
                        Rectangle { width: parent.width; height: 1; color: root.controlButtonOutline }
                        Text { renderType: Text.QtRendering;
                            text: "Modo"
                            color: root.textDim
                            font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
                            width: parent.width; wrapMode: Text.WordWrap
                        }
                        Column {
                            width: parent.width; spacing: 8
                            visible: !root.hardwareConfirmOpen
                            MenuButton {
                                height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; alignedIcon: true; iconName: "cpu"; label: "Híbrido"
                                accent: root.hardwareProfile.requested_gpu_profile === "hybrid"
                                selected: accent
                                enabled: !root.hardwareBusy && (root.hardwareProfile.gpu_profiles || []).indexOf("hybrid") >= 0
                                onActivated: root.beginGpuProfile("hybrid")
                            }
                            MenuButton {
                                height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; alignedIcon: true; iconName: "gpu"; label: "GPU Dedicada"
                                accent: root.hardwareProfile.requested_gpu_profile === "nvidia"
                                selected: accent
                                enabled: !root.hardwareBusy && (root.hardwareProfile.gpu_profiles || []).indexOf("nvidia") >= 0
                                onActivated: root.beginGpuProfile("nvidia")
                            }
                        }
                        Rectangle {
                            visible: root.hardwareConfirmOpen
                            width: parent.width; height: visible ? gpuConfirmationContent.implicitHeight + 28 : 0; radius: 14
                            color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                            antialiasing: true
                            Column {
                                id: gpuConfirmationContent
                                x: 14; y: 14; width: parent.width - 28; spacing: 12
                                Item {
                                    width: parent.width; height: 40
                                    Rectangle {
                                        width: Appearance.menuIconCircleSize; height: width; radius: width / 2; anchors.verticalCenter: parent.verticalCenter
                                        color: Qt.lighter(root.controlButtonSurface, 1.6)
                                        LucideIcon { anchors.centerIn: parent; width: Appearance.menuGlyphSize; height: width; name: "rotate-cw" }
                                    }
                                    Text { renderType: Text.QtRendering;
                                        x: 46; width: parent.width - 46; anchors.verticalCenter: parent.verticalCenter
                                        text: root.hardwareApplied ? "Reinício necessário" : "Alterar gráficos"
                                        color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold
                                        wrapMode: Text.WordWrap
                                    }
                                }
                                Text { renderType: Text.QtRendering;
                                    width: parent.width; text: root.hardwareMessage
                                    color: root.gpuProfileError.length ? "#ff91a4" : root.textDim
                                    font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                    wrapMode: Text.WordWrap
                                }
                                Row {
                                    width: parent.width; spacing: 8
                                    MenuButton {
                                        width: (parent.width - 8) * .38; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius; outlined: true
                                        label: root.hardwareApplied ? "Mais tarde" : "Cancelar"
                                        enabled: !root.hardwareBusy
                                        onActivated: root.cancelGpuProfile()
                                    }
                                    MenuButton {
                                        width: (parent.width - 8) * .62; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius
                                        visible: root.hardwareApplied || root.hardwareToken.length > 0
                                        iconName: root.hardwareApplied ? "rotate-cw" : "check"
                                        label: root.hardwareApplied ? "Reiniciar agora" : "Confirmar"
                                        enabled: !root.hardwareBusy
                                        accent: true
                                        onActivated: root.hardwareApplied ? root.rebootForGpuProfile() : root.confirmGpuProfile()
                                    }
                                }
                            }
                        }
                        Text { renderType: Text.QtRendering;
                            visible: !!root.hardwareProfile.gpu_error
                            text: root.hardwareProfile.gpu_error ? "Controlos de gráficos indisponíveis. " + root.hardwareProfile.gpu_error : ""
                            color: root.textDim; wrapMode: Text.WordWrap; width: parent.width
                            font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
                        }
                    }

                    }
                }
            }
            } // menuScrollClip
        }
        // The frame sits above the masked card so its top edge remains complete.
        Rectangle {
            z: 4
            visible: popup.open && !popupBackground.splitControls
            x: popupBackground.x; y: popupBackground.y
            width: popupBackground.width; height: popupBackground.height
            radius: popupBackground.radius
            color: "transparent"
            border.width: 1; border.color: root.shellBorder
            antialiasing: true
        }
        Rectangle {
            z: 4
            visible: popup.open && popupBackground.splitControls && compactDashboard.visible
            x: popupBackground.x + popupBackground.contentInset + root.controlPageOffset
            y: popupBackground.y + popupBackground.contentInset - menuFlick.contentY
            width: compactDashboard.width; height: compactDashboard.topCardHeight
            radius: popupBackground.radius
            color: "transparent"
            border.width: 1; border.color: root.shellBorder
            opacity: menuFlick.opacity
            antialiasing: true
        }
    }

}
