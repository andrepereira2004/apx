pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Window
import QtQuick.Controls
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Hyprland

ShellRoot {
    id: root

    // One bar per output; a single shared menu/service state follows its trigger.
    property var selectedBar: null
    readonly property var bar: selectedBar || (barVariants.instances.length ? barVariants.instances[0] : null)
    readonly property var calendarButton: bar ? bar.calendarButton : null
    readonly property var environmentButton: bar ? bar.environmentButton : null
    readonly property var modelStoreButton: bar ? bar.modelStoreButton : null
    readonly property var batteryButton: bar ? bar.batteryButton : null
    readonly property var controlCenterButton: bar ? bar.controlCenterButton : null


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

    property color cyan: "#55e6ff"
    property color cyanDim: "#246879"
    // Keep the bar and menus consistently readable while retaining a modest
    // amount of the background through both surfaces.
    // Original panel opacity.
    property color panel: "#d90a1014"
    property color popupPanel: "#d90a1014"
    // Opaque RGB, identical to Hyprland's inactive window outline.
    property color shellBorder: "#26343a"
    property color card: "#f21b1e22"
    property color textMain: "#eceef0"
    property color textDim: "#9ba3ac"
    // Control-centre actions use the same near-background surfaces as the
    // other menus. Cyan is reserved for state and emphasis, not large fills.
    readonly property color controlButtonSurface: "#191d22"
    readonly property color controlButtonHover: "#272c33"
    readonly property color controlButtonActive: "#30353b"
    readonly property color controlButtonOutline: "#343a41"
    readonly property var wallpaperSources: [
        "file:///home/apx/.config/apx/wallpapers/atlantic-coast.png",
        "file:///home/apx/.config/apx/wallpapers/alpine-lake.png",
        "file:///home/apx/.config/apx/wallpapers/rainforest-stream.png"
    ]
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
    property string environmentSystemKind: "arch"
    property int environmentNativeWindowsSizeGib: 80
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
        { key: "office", label: "Documentos e folhas de cálculo", detail: "Textos, apresentações, folhas de cálculo e correção ortográfica.", programs: "INSTALA · LibreOffice, Hunspell EN-GB", mib: 620, deps: ["desktop-integration", "locale-input"] },
        { key: "communication", label: "Câmara e videochamadas", detail: "Ferramentas de diagnóstico para webcam e vídeo.", programs: "INSTALA · v4l-utils", mib: 55, deps: ["desktop-integration", "network", "audio", "graphics"] },
        { key: "printing-scanning", label: "Impressoras e scanners", detail: "Configurar, imprimir e digitalizar documentos.", programs: "INSTALA · CUPS, SANE, Simple Scan, system-config-printer", mib: 145, deps: ["desktop-integration", "network", "devices-storage"] },
        { key: "development", label: "Programação e containers", detail: "Compilar software, desenvolver em várias linguagens e usar containers.", programs: "INSTALA · CMake, Ninja, Node.js, npm, Podman, pip, Rust", mib: 1150, deps: ["cli-aur"] },
        { key: "shortcuts", label: "Atalhos APX", detail: "Abrir rapidamente o controlo, calendário, bateria e Environments.", programs: "BASE · ponte de atalhos SUPER+A/B/D/E", mib: 8, deps: ["graphical"] }
    ]
    readonly property var environmentModuleGroups: [
        { key: "base", label: "1 · SISTEMA E AMBIENTE DE TRABALHO", description: "Terminal, janelas, idioma e integração do desktop", modules: ["system", "cli-aur", "graphical", "desktop-integration", "locale-input"] },
        { key: "hardware", label: "2 · INTERNET, SOM E DISPOSITIVOS", description: "Rede, Bluetooth, áudio, gráficos, bateria e USB", modules: ["network", "bluetooth", "audio", "graphics", "power", "devices-storage"] },
        { key: "daily", label: "3 · APLICAÇÕES DO DIA A DIA", description: "Ficheiros, browser, PDF, vídeo e codecs", modules: ["files", "web-documents", "multimedia"] },
        { key: "extras", label: "4 · TRABALHO E FERRAMENTAS AVANÇADAS", description: "Office, câmara, impressão, programação e containers", modules: ["office", "communication", "printing-scanning", "development"] },
        { key: "accessibility", label: "5 · ACESSIBILIDADE E ATALHOS", description: "Atalhos globais para abrir os menus APX", modules: ["shortcuts"] }
    ]
    property bool environmentKeyboardFocus: false
    property int environmentFocusIndex: -1
    property int environmentCreateFocusIndex: -1
    property int environmentEditFocusIndex: -1
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
    readonly property string environmentLabel: isHub ? "HUB" : String(environmentIdentity.display_name || environmentIdentity.name || "ENVIRONMENT").toUpperCase()
    readonly property int environmentPopupHeight: !isHub ? 214
        : (environmentCreateOpen ? (environmentSystemKind === "windows-native" && nativeCreationPreview.target ? 620 : 540) + (environmentManagementBusy ? 42 : 0)
           : (environmentEditOpen ? 276
           : 216 + Math.max(1, Math.min(5, environmentCatalog.length)) * 66
             + (environmentDeleteConfirm ? 88 : 0) + (environmentManagementBusy ? 42 : 0)
             + (nativeWindowsRecoveryAvailable() ? 100 : 0) + (environmentManagementState.native_v3 ? (environmentManagementState.native_v3_delete_retry ? 180 : 130) : 0)))
    property string popupKind: ""
    property Item popupTarget: null
    property bool popupAnimationPending: false
    property bool popupKeyboardRequested: false
    property bool menuKeyboardNavigation: false
    property string animatedBarOpenKind: ""
    property string animatedBarCloseKind: ""
    readonly property int popupLeftMargin: {
        if (!bar) return 19
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

    component MenuSlider: Slider {
        id: keyboardSlider
        activeFocusOnTab: true
        readonly property Item navigationTarget: parent
        readonly property bool keyboardSelected: activeFocus && root.menuKeyboardNavigation
        readonly property bool keyboardEditing: root.editingMenuSlider === keyboardSlider
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
                if (keyboardEditing) {
                    var direction = event.key === Qt.Key_Up || event.key === Qt.Key_Right ? 1 : -1
                    keyboardValueChanged(Math.max(from, Math.min(to, Math.round(value) + direction * 5)))
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
        if (focusedMenuItem !== item) clearPendingMenuFocus()
        focusedMenuItem = item
        item.forceActiveFocus(Qt.TabFocusReason)
        var point = item.mapToItem(menuFlick.contentItem, 0, 0)
        if (point.y < menuFlick.contentY) menuFlick.contentY = Math.max(0, point.y - 4)
        else if (point.y + item.height > menuFlick.contentY + menuFlick.height)
            menuFlick.contentY = Math.min(Math.max(0, menuFlick.contentHeight - menuFlick.height), point.y + item.height - menuFlick.height + 4)
    }

    function menuNavigationRect(item) {
        var target = item.navigationTarget || item
        var point = target.mapToItem(menuFlick.contentItem, 0, 0)
        return { x: point.x, y: point.y, width: target.width, height: target.height }
    }

    function spatialMenuIndex(rects, current, key) {
        var origin = rects[current]
        var horizontal = key === Qt.Key_Left || key === Qt.Key_Right
        var direction = key === Qt.Key_Left || key === Qt.Key_Up ? -1 : 1
        var best = current
        var bestDistance = Infinity
        var bestOffset = Infinity
        for (var i = 0; i < rects.length; ++i) {
            if (i === current) continue
            var candidate = rects[i]
            var along = horizontal ? candidate.x - origin.x : candidate.y - origin.y
            if (along * direction <= 1) continue
            var overlap = horizontal
                ? Math.min(origin.y + origin.height, candidate.y + candidate.height) - Math.max(origin.y, candidate.y)
                : Math.min(origin.x + origin.width, candidate.x + candidate.width) - Math.max(origin.x, candidate.x)
            // Arrows stay in the same row/column; Tab can visit every control.
            if (overlap <= 1) continue
            var distance = Math.abs(along)
            var offset = horizontal
                ? Math.abs(candidate.y + candidate.height / 2 - origin.y - origin.height / 2)
                : Math.abs(candidate.x + candidate.width / 2 - origin.x - origin.width / 2)
            if (distance < bestDistance - 1 || (Math.abs(distance - bestDistance) <= 1 && offset < bestOffset)) {
                best = i
                bestDistance = distance
                bestOffset = offset
            }
        }
        return best
    }

    function navigateGenericMenu(event) {
        if (popupKind === "calendar" || (popupKind === "environments" && isHub)) return
        var tab = event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab
        var arrow = [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right].indexOf(event.key) >= 0
        if (!tab && !arrow) return
        menuKeyboardNavigation = true
        var items = genericMenuItems()
        if (!items.length) return
        var current = -1
        for (var i = 0; i < items.length; ++i) if (items[i].activeFocus) current = i
        var next = 0
        if (current >= 0) {
            next = tab ? (current + (event.key === Qt.Key_Backtab ? -1 : 1) + items.length) % items.length
                       : spatialMenuIndex(items.map(menuNavigationRect), current, event.key)
        }
        focusMenuItem(items[next])
        event.accepted = true
    }

    Timer {
        interval: 100
        repeat: true
        running: popup.open && root.menuKeyboardNavigation && root.popupKind !== "calendar" && (root.popupKind !== "environments" || !root.isHub)
        onTriggered: {
            // The action temporarily disables its button; let it regain focus.
            if (root.focusedMenuItem && root.focusedMenuItem.visible && root.focusedMenuItem.keyboardActivationPending === true) return
            var items = root.genericMenuItems()
            for (var i = 0; i < items.length; ++i) if (items[i].activeFocus) return
            if (items.length) root.focusMenuItem(items[0])
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
    property string powerAction: ""
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
    property bool controlsWifiOpen: false
    property bool controlsBluetoothOpen: false
    property bool controlsAudioOpen: false
    property bool controlsMicrophoneOpen: false
    property string wifiSelectedSsid: ""
    property string wifiPassword: ""
    property string wifiMessage: ""
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
    property string bluetoothPairPin: ""
    property string bluetoothPairResponsePin: ""
    property string bluetoothRemoveAddress: ""
    property string bluetoothRemoveName: ""
    readonly property int menuTitleSize: 14
    property int menuBodySize: 11
    property int menuSmallSize: 10
    property int menuMetaSize: 9
    readonly property int environmentCreateModuleFocusBase: 9 + environmentModuleGroups.length
    readonly property int environmentCreateSubmitFocusIndex: environmentCreateModuleFocusBase + environmentModuleCatalog.length
    // Hyprland renders the display at 150%. Present the control centre at a
    // 125% physical compromise: readable on the internal panel while keeping
    // every common 16px icon aligned to an integer 20-device-pixel target.
    // Match the desktop scale exactly. Fractionally scaling the whole popup
    // forced SVG icons through an intermediate texture and softened corners.
    readonly property real controlCenterScale: 1
    property var modelStoreState: ({ state: "unknown", message: "A verificar o SSD do modelo…" })
    property bool modelStoreBusy: false
    property bool modelStoreConfirmDetach: false
    property string modelStoreError: ""
    property bool modelSwitchActive: false
    property string modelSwitchProfile: ""
    property string modelSwitchLabel: ""
    property int modelSwitchProgress: 0

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

    function wifiSecurityLabel(name) {
        if (wifiIsOpen(name)) return "ABERTA"
        if (wifiIsKnown(name)) return "GUARDADA"
        return "PALAVRA-PASSE"
    }

    function wifiDetails(name) {
        var details = hostState.network_details || []
        for (var i = 0; i < details.length; ++i)
            if (details[i].ssid === name) return details[i]
        return ({ ssid: name, signal: 0, security: "unknown", known: false })
    }

    function wifiSignalBars(signal) {
        if (signal >= 75) return "▂▄▆█"
        if (signal >= 50) return "▂▄▆·"
        if (signal >= 25) return "▂▄··"
        return "▂···"
    }

    function wifiConnectivityLabel() {
        var state = hostState.network_connectivity || "unknown"
        if (state === "full") return "● INTERNET DISPONÍVEL"
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
        wifiMessage = ""
        wifiSelectedSsid = name
        wifiPassword = ""
        wifiPasswordVisible = true
        if (!wifiIsKnown(name) && !wifiIsOpen(name))
            wifiPasswordInput.forceActiveFocus()
    }

    function cancelWifiPassword() {
        wifiPassword = ""
        wifiSelectedSsid = ""
        wifiPasswordVisible = false
    }

    function submitWifiPassword() {
        if (wifiIsKnown(wifiSelectedSsid) || wifiIsOpen(wifiSelectedSsid)) {
            wifiMessage = "A ligar a " + wifiSelectedSsid + "…"
            hostAction("wifi-connect", wifiSelectedSsid)
            return
        }
        if (wifiCredentialProcess.running || wifiPassword.length < 8) {
            wifiMessage = wifiPassword.length < 8 ? "A palavra-passe deve ter pelo menos 8 caracteres." : "Ligação em curso…"
            return
        }
        wifiMessage = "A ligar a " + wifiSelectedSsid + "…"
        wifiCredentialProcess.command = ["/run/apx/host-services-client-v3.py", "wifi-connect", wifiSelectedSsid, "--credential-stdin"]
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

    function wifiDisplayActive() {
        return wifiOptimisticOverride ? wifiOptimisticActive : !!hostState.network_name
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
        if (wifiPasswordVisible)
            cancelWifiPassword()
        var wasOpen = section === "wifi" ? controlsWifiOpen
                    : section === "bluetooth" ? controlsBluetoothOpen
                    : section === "microphone" ? controlsMicrophoneOpen
                    : controlsAudioOpen
        controlsWifiOpen = section === "wifi" && !wasOpen
        controlsBluetoothOpen = section === "bluetooth" && !wasOpen
        controlsAudioOpen = section === "audio" && !wasOpen
        controlsMicrophoneOpen = section === "microphone" && !wasOpen
        if (controlsAudioOpen)
            Qt.callLater(function() { if (root.menuKeyboardNavigation) volumeSlider.forceActiveFocus(); else popupBackground.forceActiveFocus() })
        else if (controlsMicrophoneOpen)
            Qt.callLater(function() { if (root.menuKeyboardNavigation) microphoneSlider.forceActiveFocus(); else popupBackground.forceActiveFocus() })
    }

    function controlsAllClosed() {
        return !controlsWifiOpen && !controlsBluetoothOpen && !controlsAudioOpen && !controlsMicrophoneOpen
    }

    function bluetoothConnectedDevices() {
        if (!bluetoothDisplayPowered()) return []
        return (hostState.bluetooth_devices || []).filter(function(device) {
            return device.paired === true && device.connected === true
                   && !(bluetoothDevicePendingAction === "bluetooth-disconnect" && bluetoothDevicePendingAddress === device.address)
        })
    }

    function bluetoothKnownDevices() {
        if (!bluetoothDisplayPowered()) return []
        return (hostState.bluetooth_devices || []).filter(function(device) {
            if (device.paired !== true) return false
            if (bluetoothDevicePendingAction === "bluetooth-disconnect" && bluetoothDevicePendingAddress === device.address) return true
            return device.connected !== true
        })
    }

    function bluetoothAvailableDevices() {
        if (!bluetoothDisplayPowered()) return []
        return (hostState.bluetooth_devices || []).filter(function(device) { return device.paired !== true })
    }

    function applyBluetoothPairResult(payload) {
        bluetoothPairSessionId = payload.session_id || bluetoothPairSessionId
        bluetoothPairPhase = payload.phase || "waiting"
        bluetoothPairChallenge = payload.challenge || ""
        bluetoothPairPasskey = payload.passkey === undefined || payload.passkey === null ? "" : String(payload.passkey)
        bluetoothMessage = payload.message || ""
        if (bluetoothPairPhase === "completed") {
            bluetoothMessage = bluetoothPairName + " emparelhado com sucesso."
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
        bluetoothMessage = "A iniciar o emparelhamento…"
        bluetoothPairAddress = device.address
        bluetoothPairName = device.name || device.address
        bluetoothPairPhase = "starting"
        bluetoothPairChallenge = ""
        bluetoothPairPasskey = ""
        bluetoothPairPin = ""
        bluetoothPairBeginProcess.command = ["/run/apx/host-services-client-v3.py", "bluetooth-pair", device.address]
        bluetoothPairBeginProcess.running = true
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
    }

    function confirmBluetoothRemove() {
        if (!bluetoothRemoveAddress.length || bluetoothRemoveProcess.running) return
        bluetoothRemoveProcess.command = ["/run/apx/host-services-client-v3.py", "bluetooth-remove", bluetoothRemoveAddress]
        bluetoothRemoveProcess.running = true
    }

    function beginEvent() {
        editingEventId = ""
        draftTitle = ""
        draftDate = dateKey(new Date())
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
        calendarEditor = true
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
        calendarEditor = true
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

    function moveCalendar(direction) {
        var d = calendarDate
        if (calendarView === "day")
            calendarDate = new Date(d.getFullYear(), d.getMonth(), d.getDate() + direction)
        else if (calendarView === "year")
            calendarDate = new Date(d.getFullYear() + direction, d.getMonth(), 1)
        else
            calendarDate = new Date(d.getFullYear(), d.getMonth() + direction, 1)
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
        else if (action.kind === "view") calendarView = action.key
        else if (action.kind === "date") {
            var parts = action.key.split("-")
            selectCalendarDate(new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])))
        } else if (action.kind === "month") {
            calendarDate = new Date(calendarDate.getFullYear(), Number(action.key), 1)
            calendarView = "month"
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
        clearPendingMenuFocus()
        editingMenuSlider = null
        popupKeyboardRequested = false
        animatedBarOpenKind = ""
        animatedBarCloseKind = ""
        popupOpenAnimation.stop()
        popup.open = false
        popupAnimationPending = false
        popupKind = ""
        controlsWifiOpen = false
        controlsBluetoothOpen = false
        controlsAudioOpen = false
        controlsMicrophoneOpen = false
        cancelWifiPassword()
        environmentCreateOpen = false
        environmentEditOpen = false
        environmentDeleteConfirm = false
        environmentKeyboardFocus = false
        calendarFocusAction = ({ kind: "", key: "" })
    }

    function showPopup() {
        popupOpenAnimation.stop()
        popupAnimationPending = false
        root.flushEnvironmentCatalog()
        popupBackground.opacity = 0.001
        popupBackground.scale = (popupKind === "controls" ? controlCenterScale : 1) * 0.96
        menuKeyboardNavigation = false
        environmentKeyboardFocus = false
        popup.open = true
        popupAnimationPending = true
        // Set focus after the card is visible, including on the first opening.
        Qt.callLater(function() {
            if (!popup.open) return
            if (root.popupKind === "calendar") calendarMenu.forceActiveFocus()
            else if (root.popupKind === "environments" && root.isHub) environmentMenu.forceActiveFocus()
            else popupBackground.forceActiveFocus()
        })
    }

    function popupBarTargetAt(x, y) {
        if (!bar || popup.screen !== bar.screen || y < 0 || y >= bar.implicitHeight) return null
        var buttons = [calendarButton, environmentButton, modelStoreButton, batteryButton, controlCenterButton]
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
        var buttons = ({ calendar: calendarButton, environments: environmentButton,
                         controls: controlCenterButton, battery: batteryButton, model: modelStoreButton })
        root.togglePopup(kind, buttons[kind], true)
    }

    function togglePopup(kind, target, keyboardRequested) {
        if (!target) return
        var targetBar = target.QsWindow.window
        if (targetBar && targetBar !== root.bar) {
            root.closePopup()
            root.selectedBar = targetBar
        }
        if (popupKind === kind && popup.open) {
            popupKeyboardRequested = false
            animatedBarOpenKind = ""
            animatedBarCloseKind = kind
            barAnimationReset.restart()
            popup.open = false
            popupKind = ""
            if (kind === "environments") environmentKeyboardFocus = false
            if (kind === "calendar") calendarFocusAction = ({ kind: "", key: "" })
            return
        }
        animatedBarCloseKind = ""
        animatedBarOpenKind = kind
        popupKeyboardRequested = keyboardRequested === true
        barAnimationReset.restart()
        popupOpenAnimation.stop()
        if (kind === "controls") {
            controlsWifiOpen = false
            controlsBluetoothOpen = false
            controlsAudioOpen = false
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
        if (kind === "model" && !modelStoreStatusProcess.running)
            modelStoreStatusProcess.running = true
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
        if (!item || !environmentStorageState.sizes) return ""
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
        if (position < 0) environmentFocusIndex = indices[0]
        else environmentFocusIndex = indices[(position + direction + indices.length) % indices.length]
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
                                              "--description", description]
        environmentMetadataProcess.running = true
    }

    function handleEnvironmentEditKey(event) {
        if (event.key === Qt.Key_Escape) cancelEnvironmentEdit()
        else if (event.key === Qt.Key_Up || event.key === Qt.Key_Backtab)
            environmentEditFocusIndex = (environmentEditFocusIndex + 3) % 4
        else if (event.key === Qt.Key_Down || event.key === Qt.Key_Tab)
            environmentEditFocusIndex = (environmentEditFocusIndex + 1) % 4
        else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
            if (environmentEditFocusIndex === 0) cancelEnvironmentEdit()
            else if (environmentEditFocusIndex === 1) environmentEditTitleInput.forceActiveFocus()
            else if (environmentEditFocusIndex === 2) environmentEditDescriptionInput.forceActiveFocus()
            else saveEnvironmentMetadata()
        } else return
        if (environmentEditFocusIndex === 0 || environmentEditFocusIndex === 3)
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
        if (environmentSystemKind !== "arch") {
            indices.push(6, 7, 8)
            indices.push(environmentCreateSubmitFocusIndex)
            return indices
        }
        indices.push(6, 7, 8)
        environmentModuleGroups.forEach(function(group, groupIndex) {
            indices.push(9 + groupIndex)
            if (environmentFeatureDrawer === group.key) group.modules.forEach(function(key) {
                var moduleIndex = environmentModuleIndex(key)
                if (moduleIndex >= 0) indices.push(environmentCreateModuleFocusBase + moduleIndex)
            })
        })
        indices.push(environmentCreateSubmitFocusIndex)
        return indices
    }

    function moveEnvironmentCreateFocus(direction) {
        var indices = environmentCreateVisibleFocusIndices()
        var position = indices.indexOf(environmentCreateFocusIndex)
        if (position < 0) environmentCreateFocusIndex = direction > 0 ? indices[0] : indices[indices.length - 1]
        else environmentCreateFocusIndex = indices[(position + direction + indices.length) % indices.length]
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
        var focusIndex = environmentCreateFocusIndex
        if (focusIndex < 0) { moveEnvironmentCreateFocus(direction); return }
        if (focusIndex === 0) environmentCreateFocusIndex = direction > 0 ? 1 : environmentCreateSubmitFocusIndex
        else if (focusIndex === 1) environmentCreateFocusIndex = direction > 0 ? 2 : 0
        else if (focusIndex === 2) environmentCreateFocusIndex = direction > 0 ? 4 : 1
        else if (focusIndex >= 3 && focusIndex <= 4)
            environmentCreateFocusIndex = direction > 0 ? 7 : 2
        else if (focusIndex >= 6 && focusIndex <= 8)
            environmentCreateFocusIndex = direction > 0 ? (environmentSystemKind === "arch" ? 9 : environmentCreateSubmitFocusIndex) : 4
        else if (focusIndex >= 9 && focusIndex <= 13) {
            var groupIndex = focusIndex - 9
            var group = environmentModuleGroups[groupIndex]
            if (direction > 0 && environmentFeatureDrawer === group.key && group.modules.length)
                environmentCreateFocusIndex = environmentCreateModuleFocusBase + environmentModuleIndex(group.modules[0])
            else if (direction > 0) environmentCreateFocusIndex = groupIndex < environmentModuleGroups.length - 1 ? focusIndex + 1 : environmentCreateSubmitFocusIndex
            else environmentCreateFocusIndex = groupIndex > 0 ? focusIndex - 1 : 4
        } else if (focusIndex >= environmentCreateModuleFocusBase && focusIndex < environmentCreateSubmitFocusIndex) {
            var module = environmentModuleCatalog[focusIndex - environmentCreateModuleFocusBase]
            for (var index = 0; index < environmentModuleGroups.length; ++index) {
                var groupModules = environmentModuleGroups[index].modules
                var position = groupModules.indexOf(module.key)
                if (position < 0) continue
                var verticalNeighbour = position + direction * 2
                if (verticalNeighbour >= 0 && verticalNeighbour < groupModules.length)
                    environmentCreateFocusIndex = environmentCreateModuleFocusBase + environmentModuleIndex(groupModules[verticalNeighbour])
                else if (direction < 0) environmentCreateFocusIndex = 9 + index
                else environmentCreateFocusIndex = index < environmentModuleGroups.length - 1 ? 10 + index : environmentCreateSubmitFocusIndex
                break
            }
        } else if (focusIndex === environmentCreateSubmitFocusIndex) environmentCreateFocusIndex = direction > 0 ? 0 : (environmentSystemKind === "arch" ? environmentModuleGroups.length + 8 : 7)
        environmentMenu.forceActiveFocus()
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
        if (focusIndex >= 6 && focusIndex <= 8) {
            if (environmentSystemKind === "arch") applyEnvironmentPreset(["basic", "intermediate", "complete"][focusIndex - 6])
            else environmentNativeWindowsSizeGib = [80, 120, 160][focusIndex - 6]
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
        if (preset === "complete") return environmentModuleCatalog.map(function(item) { return item.key })
        return environmentModuleCatalog.slice(0, 14).map(function(item) { return item.key }).concat(["shortcuts"])
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

    function modelStoreAction(mode, target) {
        if (modelStoreActionProcess.running || modelStoreBusy) return
        modelStoreBusy = true
        modelStoreError = ""
        modelStoreConfirmDetach = false
        if (mode === "model-select") {
            modelSwitchActive = true
            modelSwitchProfile = target
            modelSwitchLabel = target === "fast" ? "Qwen2.5-Coder 3B Fast" : (target === "balanced" ? "Qwen2.5-Coder 7B" : "Qwen3-Coder 30B")
            modelSwitchProgress = 2
        }
        modelStoreActionProcess.command = ["/home/apx/.local/libexec/apx-model-store-client-v1.py", mode]
        if (target !== undefined && target !== "")
            modelStoreActionProcess.command.push(target)
        modelStoreActionProcess.running = true
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
        hotkeyOsdIcon = icon
        hotkeyOsdTitle = title
        hotkeyOsdDetail = detail
        hotkeyOsdProgress = progress === undefined ? -1 : progress
        hotkeyOsdVisible = true
        hotkeyOsdOpacity = 1
        hotkeyOsdHideTimer.restart()
    }

    function applyRadioState(state) {
        if (state.airplane_mode === undefined) return
        var next = state.airplane_mode === true
        if (airplaneModeKnown && airplaneMode !== next) {
            showHotkeyOsd(
                next
                    ? "file:///usr/share/icons/Adwaita/symbolic/status/airplane-mode-symbolic.svg"
                    : "file:///usr/share/icons/Adwaita/symbolic/status/airplane-mode-disabled-symbolic.svg",
                "Modo de avião", next ? "Ativado" : "Desativado", -1)
        }
        airplaneMode = next
        airplaneModeKnown = true
    }

    function previewVolume(value) {
        volumeValue = Math.max(0, Math.min(100, Math.round(value)))

        showHotkeyOsd(
            volumeMuted
                ? "file:///usr/share/icons/Adwaita/symbolic/status/audio-volume-muted-symbolic.svg"
                : "file:///usr/share/icons/Adwaita/symbolic/status/audio-volume-high-symbolic.svg",
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

    function commitMicrophoneVolume(value) {
        var nextVolume = Math.round(value)
        microphoneVolume = nextVolume
        if (!microphoneMuted)
            microphoneText = nextVolume + "%"
        showHotkeyOsd(
            microphoneMuted
                ? "file:///usr/share/icons/Adwaita/symbolic/status/microphone-sensitivity-muted-symbolic.svg"
                : "file:///usr/share/icons/Adwaita/symbolic/devices/audio-input-microphone-symbolic.svg",
            "Microfone", microphoneMuted ? "Silenciado" : nextVolume + "%", nextVolume)
        localAction(["/usr/bin/wpctl", "set-volume", "-l", "1", "@DEFAULT_AUDIO_SOURCE@", nextVolume + "%"])
    }

    function toggleVolumeMute() {
        if (localActionProcess.running) return
        volumeMuted = !volumeMuted
        volumeText = volumeMuted ? "MUTE" : volumeValue + "%"
        showHotkeyOsd(
            volumeMuted
                ? "file:///usr/share/icons/Adwaita/symbolic/status/audio-volume-muted-symbolic.svg"
                : "file:///usr/share/icons/Adwaita/symbolic/status/audio-volume-high-symbolic.svg",
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
                ? "file:///usr/share/icons/Adwaita/symbolic/status/microphone-sensitivity-muted-symbolic.svg"
                : "file:///usr/share/icons/Adwaita/symbolic/devices/audio-input-microphone-symbolic.svg",
            "Microfone", microphoneMuted ? "Silenciado" : "Ativado · " + microphoneVolume + "%",
            microphoneMuted ? 0 : microphoneVolume)
        localAction(["/usr/bin/wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "toggle"])
    }

    function applyHardwareControls(state) {
        if (state.display_brightness !== undefined && displayBrightnessPending < 0
                && !displayBrightnessProcess.running && !displayBrightnessSlider.pressed)
            displayBrightness = Number(state.display_brightness)
        if (state.keyboard_brightness !== undefined)
            keyboardBrightness = Number(state.keyboard_brightness)
        if (state.keyboard_brightness_max !== undefined)
            keyboardBrightnessMax = Number(state.keyboard_brightness_max)
    }

    function previewDisplayBrightness(value) {
        displayBrightness = Math.max(5, Math.min(100, Math.round(value)))
        showHotkeyOsd(
            "file:///usr/share/icons/Adwaita/symbolic/status/display-brightness-symbolic.svg",
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
        if (profile === "hybrid") return "HÍBRIDO"
        if (profile === "nvidia") return "NVIDIA"
        return "Indisponível"
    }

    function setPlatformProfile(profile) {
        if (hardwareBusy) return
        hardwareBusy = true
        platformProfileTarget = profile
        platformProfileError = ""
        hardwareMessage = "A aplicar modo " + platformLabel(profile) + "..."
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
        command: ["/run/apx/host-services-ui-v3.py", "status"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    root.hostState = JSON.parse(text)
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
        id: radioStatusProcess
        // rfkill state is kernel-owned and read-only here. Reading sysfs directly
        // also keeps the OSD alive if the host-service socket is replaced while
        // an environment is already running.
        command: ["/usr/bin/bash", "--noprofile", "--norc", "-c",
            "blocked=1; wlan=0; bluetooth=0; "
            + "for directory in /sys/class/rfkill/rfkill*; do "
            + "[ -d \"$directory\" ] || continue; kind=$(<\"$directory/type\"); "
            + "case \"$kind\" in wlan) wlan=1;; bluetooth) bluetooth=1;; *) continue;; esac; "
            + "[ \"$(<\"$directory/soft\")\" = 1 ] || blocked=0; done; "
            + "[ $wlan = 1 ] && [ $bluetooth = 1 ] || exit 1; "
            + "if [ $blocked = 1 ]; then value=true; else value=false; fi; "
            + "printf '{\"airplane_mode\":%s}\\n' \"$value\""]
        stdout: StdioCollector {
            onStreamFinished: {
                try { root.applyRadioState(JSON.parse(text)) }
                catch (error) {}
            }
        }
    }

    Process {
        id: hostActionProcess
        onExited: hostStatusProcess.running = true
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
        onStarted: root.bluetoothMessage = "A procurar dispositivos…"
        onExited: (exitCode, exitStatus) => {
            root.bluetoothMessage = exitCode === 0 ? "Pesquisa concluída." : (root.bluetoothMessage || "Não foi possível procurar dispositivos.")
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
            write(root.wifiPassword + "\n")
            root.wifiPassword = ""
        }
        onExited: (exitCode, exitStatus) => {
            if (exitCode === 0) {
                root.wifiMessage = "Ligação efetuada."
                root.wifiPasswordVisible = false
                root.wifiSelectedSsid = ""
            } else if (!root.wifiMessage.length) {
                root.wifiMessage = "Não foi possível estabelecer a ligação."
            }
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
        command: ["/usr/bin/wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"]
        stdout: StdioCollector {
            onStreamFinished: {
                var match = text.match(/Volume:\s+([0-9.]+)/)
                if (match) root.microphoneVolume = Math.round(parseFloat(match[1]) * 100)
                root.microphoneMuted = text.indexOf("MUTED") >= 0
                root.microphoneText = match ? (root.microphoneMuted ? "MUTE" : root.microphoneVolume + "%") : "--"
            }
        }
    }

    Process {
        id: batteryProcess
        command: ["/usr/bin/bash", "-lc", "for d in /sys/class/power_supply/BAT*; do test -r \"$d/capacity\" || continue; for field in capacity status power_now energy_now energy_full energy_full_design; do if test -r \"$d/$field\"; then tr -d '\\n' < \"$d/$field\"; fi; printf '\\n'; done; exit; done; printf -- '--\\n'"]
        stdout: StdioCollector { onStreamFinished: root.applyBatteryReport(text) }
    }

    Process {
        id: hardwareProfileProcess
        command: ["/home/apx/.local/libexec/apx-system-power-client-v1.py", "hardware-status"]
        property string response: ""
        onStarted: { response = ""; root.hardwareStatusError = "" }
        stderr: StdioCollector { onStreamFinished: root.hardwareStatusError = text.trim() }
        stdout: StdioCollector { onStreamFinished: hardwareProfileProcess.response = text }
        onExited: (exitCode, exitStatus) => {
            // A status request started before a mutation must not undo its UI.
            if (root.hardwareBusy) return
            try {
                if (exitCode !== 0) throw new Error("status failed")
                var result = JSON.parse(response)
                if (!Array.isArray(result.platform_profiles)) throw new Error("invalid status")
                root.hardwareProfile = result
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
                root.hardwareMessage = "Perfil " + root.platformLabel(result.platform_profile) + " confirmado pelo sistema."
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
                    "file:///usr/share/icons/Adwaita/symbolic/status/display-brightness-symbolic.svg",
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
    Process { id: environmentAppsProcess; command: ["/usr/bin/rofi", "-show", "drun"] }
    Process { id: updateUiProcess; command: root.isHub
        ? ["/home/apx/.local/bin/apx-detached-launch", "/usr/bin/kitty", "--title", "APX Atualizações", "/run/apx/coordinated-update-client-v1.py", "environments-ui"]
        : ["/home/apx/.local/bin/apx-detached-launch", "/usr/bin/kitty", "--title", "APX Atualizações", "/home/apx/.local/bin/apx-environment-update-v1"] }
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
    Process {
        id: modelStoreStatusProcess
        command: ["/home/apx/.local/libexec/apx-model-store-client-v1.py", "status"]
        stdout: StdioCollector { onStreamFinished: { try { var nextState = JSON.parse(text); root.modelStoreState = nextState; root.modelStoreError = ""; if (nextState.model_transition === true) { root.modelSwitchActive = true; root.modelSwitchProfile = nextState.transition_profile || ""; root.modelSwitchLabel = nextState.transition_model || "Novo modelo"; root.modelSwitchProgress = nextState.transition_progress || 1 } else if (!modelStoreActionProcess.running) { root.modelSwitchActive = false; root.modelSwitchProgress = 0 } } catch (error) { root.modelStoreError = "Não foi possível ler o estado do modelo." } } }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.modelStoreError = text.trim() }
    }
    Process {
        id: modelStoreActionProcess
        stdout: StdioCollector { onStreamFinished: { try { root.modelStoreState = JSON.parse(text); root.modelStoreError = "" } catch (error) { root.modelStoreError = "Resposta inválida do Host." } } }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) root.modelStoreError = text.trim() }
        onExited: { root.modelStoreBusy = false; root.modelSwitchActive = false; root.modelSwitchProgress = 0; if (!modelStoreStatusProcess.running) modelStoreStatusProcess.running = true }
    }
    IpcHandler {
        target: "host"
        function transitionStatus(): string {
            return JSON.stringify({ startup: root.startupCover, ready: root.startupReady,
                bar_rendered: root.startupBarRendered, identity_ready: root.identityReady,
                outgoing: root.environmentSwitchPending, dispatched: root.environmentSwitchDispatched })
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
                root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/status/dialog-warning-symbolic.svg", "Aplicações", "Launcher não instalado no Hub", -1)
                return
            }
            if (!environmentAppsProcess.running)
                environmentAppsProcess.running = true
        }

        function openEnvironments(): void {
            root.environmentKeyboardFocus = false
            root.toggleFocusedPopup("environments")
        }

        function refreshModel(): void {
            if (!modelStoreStatusProcess.running && !modelStoreActionProcess.running)
                modelStoreStatusProcess.running = true
        }

        function prepareShutdown(): void { openControls(); root.beginPower("poweroff") }
        function cancelShutdown(): void { root.cancelPower() }
        function shutdownStatus(): string {
            return JSON.stringify({ open: root.powerConfirmOpen, busy: root.powerBusy, prepared: root.powerToken.length > 0, message: root.powerMessage })
        }

        function hardwareStatus(): string {
            return JSON.stringify({ profile: root.hardwareProfile.platform_profile, pending: root.platformProfileTarget, busy: root.hardwareBusy, error: root.platformProfileError || root.hardwareStatusError })
        }

        function modelStatus(): string {
            return JSON.stringify(root.modelStoreState)
        }

        function popupStatus(): string {
            return JSON.stringify({ kind: root.popupKind, visible: popup.open,
                                    screen: popup.screen ? popup.screen.name : "",
                                    bars: barVariants.instances.map(function(b) { return b.screen.name }),
                                    width: popup.menuWidth, height: popup.menuHeight,
                                    animation_pending: root.popupAnimationPending,
                                    animation_running: popupOpenAnimation.running,
                                    popup_opacity: popupBackground.opacity,
                                    keyboard_items: root.genericMenuItems().length,
                                    keyboard_index: root.genericMenuItems().findIndex(function(item) { return item.activeFocus }),
                                    calendar_focus_kind: root.calendarFocusAction.kind,
                                    calendar_focus_key: root.calendarFocusAction.key,
                                    calendar_selected_date: root.calendarSelectedDateKey,
                                    environment_selected_name: root.selectedEnvironmentName,
                                    environment_focus_index: root.environmentFocusIndex,
                                    environment_error: root.environmentSwitchError,
                                    environment_form_name: environmentNameInput.text,
                                    environment_description_length: environmentDescriptionInput.text.length })
        }

        function toggleControls(): void {
            root.toggleFocusedPopup("controls")
        }

        function toggleCalendar(): void {
            root.toggleFocusedPopup("calendar")
        }

        function toggleModel(): void {
            if (root.isHub)
                root.toggleFocusedPopup("model")
        }

        function toggleBattery(): void {
            root.toggleFocusedPopup("battery")
        }

        function openControls(): void {
            root.popupKeyboardRequested = true
            root.popupKind = "controls"
            root.popupTarget = controlCenterButton
            root.showPopup()
        }

        function openWifiControls(): void {
            openControls()
            root.controlsWifiOpen = true
            root.controlsBluetoothOpen = false
            root.controlsAudioOpen = false
            root.controlsMicrophoneOpen = false
        }

        function openBluetoothControls(): void {
            openControls()
            root.controlsWifiOpen = false
            root.controlsBluetoothOpen = true
            root.controlsAudioOpen = false
            root.controlsMicrophoneOpen = false
        }

        function openVolumeControls(): void {
            openControls()
            root.controlsWifiOpen = false
            root.controlsBluetoothOpen = false
            root.controlsAudioOpen = true
            root.controlsMicrophoneOpen = false
            Qt.callLater(function() { if (root.menuKeyboardNavigation) volumeSlider.forceActiveFocus(); else popupBackground.forceActiveFocus() })
        }

        function openMicrophoneControls(): void {
            openControls()
            root.controlsWifiOpen = false
            root.controlsBluetoothOpen = false
            root.controlsAudioOpen = false
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
        function hotkeyApps(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/actions/view-grid-symbolic.svg", "Aplicações", "A abrir", -1) }
        function hotkeyAirplaneOff(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/status/airplane-mode-disabled-symbolic.svg", "Modo de avião", "Desativado", -1) }
        function hotkeyAirplaneOn(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/status/airplane-mode-symbolic.svg", "Modo de avião", "Ativado", -1) }
        function hotkeyAirplaneUnavailable(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/status/dialog-warning-symbolic.svg", "Modo de avião", "Estado indisponível", -1) }
        function hotkeyCalculator(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/legacy/accessories-calculator-symbolic.svg", "Calculadora", "A abrir", -1) }
        function hotkeyCalculatorMissing(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/legacy/accessories-calculator-symbolic.svg", "Calculadora", "Não está instalada", -1) }
        function hotkeyDisplayExtended(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/legacy/preferences-desktop-display-symbolic.svg", "Ecrãs", "Ambiente estendido", -1) }
        function hotkeyDisplayExternal(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/legacy/preferences-desktop-display-symbolic.svg", "Ecrãs", "Apenas ecrã externo", -1) }
        function hotkeyDisplayInternal(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/legacy/preferences-desktop-display-symbolic.svg", "Ecrãs", "Apenas ecrã do portátil", -1) }
        function hotkeyDisplayInternalOnly(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/legacy/preferences-desktop-display-symbolic.svg", "Ecrãs", "Nenhum ecrã externo", -1) }
        function hotkeyDisplayMirrored(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/legacy/preferences-desktop-display-symbolic.svg", "Ecrãs", "Imagem duplicada", -1) }
        function hotkeyFailed(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/status/dialog-warning-symbolic.svg", "Atalho", "A ação falhou", -1) }
        function hotkeyOverview(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/ui/focus-windows-symbolic.svg", "Janelas abertas", "A mostrar", -1) }
        function hotkeyScreenshot(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/devices/camera-photo-symbolic.svg", "Captura de ecrã", "Guardada em Imagens", -1) }
        function hotkeyScreenshotUnavailable(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/status/dialog-warning-symbolic.svg", "Captura de ecrã", "Ferramenta não instalada", -1) }
        function hotkeyTouchpadOff(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/devices/input-touchpad-symbolic.svg", "Touchpad", "Desativado", -1) }
        function hotkeyTouchpadOn(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/devices/input-touchpad-symbolic.svg", "Touchpad", "Ativado", -1) }
        function hotkeyTouchpadToggled(): void { root.showHotkeyOsd("file:///usr/share/icons/Adwaita/symbolic/devices/input-touchpad-symbolic.svg", "Touchpad", "Estado alterado", -1) }
    }
    Process {
        id: audioStateProcess
        command: ["/run/apx/audio-state-client-v1.py", "get"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var state = JSON.parse(text)
                    root.microphoneActive = state.microphone_active === true
                } catch (error) {
                    root.microphoneActive = false
                    root.microphoneText = "--"
                }
            }
        }
    }
    Process {
        id: powerPrepareProcess
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
                    } else {
                        root.powerToken = ""
                        root.powerMessage = "AÇÃO BLOQUEADA :: " + (result.blockers || []).join(" | ")
                    }
                } catch (error) {
                    root.powerBusy = false
                    root.powerToken = ""
                    root.powerMessage = "Não foi possível consultar o Host."
                }
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
                } catch (error) { root.powerMessage = "O Host recusou a ação." }
            }
        }
        onExited: root.powerBusy = false
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
        interval: 750
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
        interval: 10000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            if (!hostStatusProcess.running) hostStatusProcess.running = true
            if (!volumeProcess.running) volumeProcess.running = true
            if (!microphoneProcess.running) microphoneProcess.running = true
            if (!batteryProcess.running) batteryProcess.running = true
            if (!hardwareProfileProcess.running) hardwareProfileProcess.running = true
        }
    }
    Timer {
        interval: root.modelStoreBusy ? 500 : 5000; running: root.isHub; repeat: true; triggeredOnStart: true
        onTriggered: if (root.isHub && !modelStoreStatusProcess.running) modelStoreStatusProcess.running = true
    }

    Timer {
        interval: 250; running: !root.identityReady; repeat: true; triggeredOnStart: true
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
        interval: 1000
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
        property string title: ""
        width: parent.width
        height: 30
        Text {
            anchors.left: parent.left
            anchors.right: parent.right
            height: 24
            verticalAlignment: Text.AlignVCenter
            text: parent.title
            color: root.textMain
            font.family: "Selawik"
            font.pixelSize: parent.title === "Environments" || parent.title === "Calendário" ? root.menuTitleSize + 1 : root.menuTitleSize
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

    component MenuButton: Rectangle {
        id: menuButton
        property string label: ""
        property bool accent: false
        property bool selected: false
        property bool keyboardFocused: false
        signal activated()
        width: parent ? parent.width : 250
        height: 34
        opacity: enabled ? 1 : 0.42
        radius: 6
        color: keyboardFocused ? root.controlButtonActive : (menuMouse.containsMouse ? root.controlButtonHover : (accent ? root.controlButtonActive : root.controlButtonSurface))
        border.width: keyboardFocused ? 1 : 0
        border.color: keyboardFocused ? root.cyan : root.cyan
        Text {
            anchors.left: parent.left
            anchors.leftMargin: 11
            anchors.right: parent.right
            anchors.rightMargin: 11
            elide: Text.ElideRight
            anchors.verticalCenter: parent.verticalCenter
            text: menuButton.label
            color: root.textMain
            font.family: "Selawik"
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
            font.family: "Selawik"
            font.pixelSize: root.menuBodySize
            clip: true
            Text {
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
        signal activated()
        activeFocusOnTab: true
        height: 30
        radius: 6
        color: keyboardFocused ? root.controlButtonActive : (checked ? root.controlButtonActive : root.controlButtonSurface)
        border.width: keyboardFocused || activeFocus ? 1 : 0
        border.color: keyboardFocused || activeFocus ? root.cyan : root.cyan
        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                toggle.activated()
                event.accepted = true
            }
        }
        Text {
            anchors.left: parent.left
            anchors.leftMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            text: (toggle.checked ? "[✓] " : "[ ] ") + toggle.label
            color: toggle.checked ? root.textMain : root.textDim
            font.family: "Selawik"
            font.pixelSize: root.menuBodySize
            font.weight: Font.Normal
        }
        SelectionIndicator { visible: toggle.checked }
        BounceMouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: toggle.activated() }
    }

    component PresetCard: Rectangle {
        id: presetCard
        property string title: ""
        property string description: ""
        property string additions: ""
        property bool selected: false
        property bool keyboardFocused: false
        signal activated()
        opacity: enabled ? 1 : 0.42
        radius: 8
        color: keyboardFocused ? root.controlButtonActive : (presetMouse.containsMouse ? root.controlButtonHover : (selected ? root.controlButtonActive : root.controlButtonSurface))
        border.width: keyboardFocused ? 1 : 0
        border.color: keyboardFocused ? root.cyan : root.cyan
        Column {
            anchors.fill: parent; anchors.margins: 9; spacing: 3
            Text { width: parent.width; text: presetCard.title; color: presetCard.selected ? root.textMain : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
            Text { width: parent.width; text: presetCard.description; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight }
            Text { width: parent.width; text: presetCard.additions; color: presetCard.selected ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal; elide: Text.ElideRight }
        }
        SelectionIndicator { visible: presetCard.selected }
        BounceMouseArea { id: presetMouse; anchors.fill: parent; enabled: presetCard.enabled; hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor; onClicked: presetCard.activated() }
    }

    component FeatureCard: Rectangle {
        id: featureCard
        property string label: ""
        property string detail: ""
        property string programs: ""
        property bool checked: false
        property bool keyboardFocused: false
        property bool infoVisible: false
        signal activated()
        signal infoRequested()
        height: infoVisible ? 72 : 34
        radius: 7
        color: keyboardFocused ? root.controlButtonActive : (featureMouse.containsMouse ? root.controlButtonHover : (checked ? root.controlButtonActive : root.controlButtonSurface))
        border.width: keyboardFocused ? 1 : 0
        border.color: keyboardFocused ? root.cyan : root.controlButtonOutline
        Rectangle {
            anchors.left: parent.left; anchors.leftMargin: 10; anchors.top: parent.top; anchors.topMargin: 8
            width: 18; height: 18; radius: 5
            color: featureCard.checked ? root.controlButtonActive : root.controlButtonSurface
            border.width: 1; border.color: "#52656d"
            Text { anchors.centerIn: parent; text: featureCard.checked ? "✓" : ""; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
        }
        Text { anchors.left: parent.left; anchors.leftMargin: 36; anchors.right: parent.right; anchors.rightMargin: 10; anchors.top: parent.top; anchors.topMargin: 9; text: featureCard.label; color: featureCard.checked ? root.textMain : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal; elide: Text.ElideRight }
        Text { visible: featureCard.infoVisible; anchors.left: parent.left; anchors.leftMargin: 10; anchors.right: parent.right; anchors.rightMargin: 10; anchors.top: parent.top; anchors.topMargin: 31; text: featureCard.detail; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; elide: Text.ElideRight }
        Text { visible: featureCard.infoVisible; anchors.left: parent.left; anchors.leftMargin: 10; anchors.right: parent.right; anchors.rightMargin: 10; anchors.bottom: parent.bottom; anchors.bottomMargin: 8; text: featureCard.programs; color: featureCard.programs.indexOf("INSTALA") === 0 ? root.textMain : "#73929a"; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal; elide: Text.ElideRight }
        SelectionIndicator { visible: featureCard.checked }
        BounceMouseArea { id: featureMouse; anchors.fill: parent; acceptedButtons: Qt.LeftButton; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: featureCard.activated() }
        MouseArea { anchors.fill: parent; acceptedButtons: Qt.RightButton; cursorShape: Qt.WhatsThisCursor; onClicked: featureCard.infoRequested() }
    }

    // One background-layer surface per monitor. Rotation is Environment-local,
    // requires no extra daemon/package, and never reserves space or accepts
    // pointer/keyboard input.
    Timer {
        interval: 15 * 60 * 1000
        running: true
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
                source: root.wallpaperSources[root.wallpaperIndex]
                fillMode: Image.PreserveAspectCrop
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
        property alias modelStoreButton: modelStoreButton
        property alias batteryButton: batteryButton
        property alias controlCenterButton: controlCenterButton
        anchors { top: true; left: true; right: true }
        // Include the 1px outer contour: the inner surface stays aligned at 20px.
        margins { left: 19; right: 19 }
        implicitHeight: 46
        exclusiveZone: 46
        color: "transparent"
        // Top panels are covered by fullscreen clients; Overlay is not.
        WlrLayershell.layer: WlrLayer.Top
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None

        Rectangle {
            anchors.fill: parent
            anchors.topMargin: 5
            anchors.bottomMargin: 5
            radius: 10
            color: root.panel
            border.width: 1
            border.color: root.shellBorder

            MouseArea {
                anchors.fill: parent
                enabled: popup.open
                onClicked: root.closePopup()
            }

            Row {
                anchors.left: parent.left
                anchors.leftMargin: 2
                anchors.verticalCenter: parent.verticalCenter
                spacing: 4
                BarButton {
                    id: calendarButton
                    hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === calendarButton : null
                    activeSurface: root.controlButtonHover
                    accentColor: root.textMain
                    textColor: root.textMain
                    activeBorderWidth: 1
                    label: "[ " + root.clockText + " ]"
                    alternateLabel: calendarButton.label
                    alternateActive: root.bar === screenBar && popup.open && root.popupKind === "calendar"
                    animateActivation: root.animatedBarOpenKind === "calendar"
                    animateDeactivation: root.animatedBarCloseKind === "calendar"
                    onActivated: root.togglePopup("calendar", this, true)
                }
            }

            BarButton {
                id: environmentButton
                    hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === environmentButton : null
                activeSurface: root.controlButtonHover
                accentColor: root.textMain
                textColor: root.textMain
                anchors.centerIn: parent
                // The button is a compact context label; actions live in the popup.
                label: "[ " + root.environmentLabel + " ]"
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
                anchors.right: parent.right
                anchors.rightMargin: 2
                anchors.verticalCenter: parent.verticalCenter
                spacing: 2
                BarButton {
                    id: modelStoreButton
                    hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === modelStoreButton : null
                activeSurface: root.controlButtonHover
                    accentColor: root.textMain
                    textColor: root.textMain
                    visible: root.isHub
                    label: root.modelStoreState.state === "active" ? "[ IA ON ]" : (root.modelStoreState.state === "safe-to-remove" ? "[ SSD OK ]" : "[ IA OFF ]")
                    alternateLabel: modelStoreButton.label
                    alternateActive: root.bar === screenBar && popup.open && root.popupKind === "model"
                    animateActivation: root.animatedBarOpenKind === "model"
                    animateDeactivation: root.animatedBarCloseKind === "model"
                    onActivated: root.togglePopup("model", this, true)
                }
                BarButton {
                activeSurface: root.controlButtonHover
                    accentColor: root.textMain
                    textColor: root.textMain
                    visible: root.microphoneActive
                    label: "[ MIC ATIVO ]"
                }
                BarButton {
                    id: batteryButton
                    hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === batteryButton : null
                activeSurface: root.controlButtonHover
                    accentColor: root.textMain
                    textColor: root.textMain
                    label: "[ BAT " + root.batteryText + " ]"
                    alternateLabel: batteryButton.label
                    alternateActive: root.bar === screenBar && popup.open && root.popupKind === "battery"
                    animateActivation: root.animatedBarOpenKind === "battery"
                    animateDeactivation: root.animatedBarCloseKind === "battery"
                    onActivated: root.togglePopup("battery", this, true)
                }
                BarButton {
                    id: controlCenterButton
                    compactSymbol: true
                    hoverOverride: popup.open ? popupBarPointer.hoveredBarTarget === controlCenterButton : null
                    activeSurface: root.controlButtonHover
                    accentColor: root.textMain
                    textColor: root.textMain
                    activeBorderWidth: 1
                    label: "[|]"
                    alternateLabel: "[A]"
                    alternateActive: root.bar === screenBar && popup.open && root.popupKind === "controls"
                    animateActivation: root.animatedBarOpenKind === "controls"
                    animateDeactivation: root.animatedBarCloseKind === "controls"
                    onActivated: root.togglePopup("controls", this, true)
                }
            }
        }
    }
    }

    PanelWindow {
        id: hotkeyOsdWindow
        screen: root.bar ? root.bar.screen : null
        visible: root.hotkeyOsdVisible
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
                tint: root.textMain
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 57
                text: root.hotkeyOsdTitle
                color: root.textMain
                font.family: "Selawik"
                font.pixelSize: 14
                font.bold: true
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 80
                text: root.hotkeyOsdDetail
                color: root.textDim
                font.family: "Selawik"
                font.pixelSize: 12
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
        visible: root.environmentSwitchPending || root.startupCover
        exclusionMode: ExclusionMode.Ignore
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive
        anchors { top: true; bottom: true; left: true; right: true }
        WlrLayershell.layer: WlrLayer.Overlay
        exclusiveZone: 0
        color: "#000000"

        MouseArea { anchors.fill: parent; cursorShape: Qt.BlankCursor; acceptedButtons: Qt.AllButtons }
        // Loading belongs to the Host; keep only a black readiness cover here.
    }
    }

    Connections {
        target: popupBackground.Window.window
        // Wait for glyphs, icons and layout to render before starting the reveal.
        function onFrameSwapped() {
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

    // Layer-shell Exclusive traps pointer delivery on the other monitor in
    // this Hyprland build. Use the compositor's dismissible focus grab instead.
    HyprlandFocusGrab {
        id: popupFocusGrab
        windows: [popup]
        active: popup.open
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
        WlrLayershell.keyboardFocus: open && root.popupKeyboardRequested
                                     ? WlrKeyboardFocus.OnDemand
                                     : WlrKeyboardFocus.None
        property real menuWidth: root.popupKind === "calendar" ? 500
                                                     : (root.popupKind === "environments" ? (root.environmentCreateOpen ? 620 : 460)
                                                        : (root.popupKind === "controls" ? 340 * root.controlCenterScale : (root.popupKind === "battery" ? 340 : 300)))
        property real menuHeight: root.popupKind === "calendar"
                        ? (root.calendarEditor ? 500
                           : (root.calendarView === "day"
                              ? 205 + Math.min(4, root.eventsForDate(root.calendarDate).length) * 50
                              : 410 + Math.min(4, root.eventsForDate(root.calendarDate).length) * 44))
                                                       : (root.popupKind === "controls"
                                                          ? (root.controlsAllClosed() ? ((root.isHub ? 470 : 394) + (root.hasExternalDisplay ? 100 : 0)) * root.controlCenterScale
                                                             : ((root.controlsAudioOpen || root.controlsMicrophoneOpen) ? Math.max(232, menuContent.implicitHeight + 20)
                                                                : (root.controlsBluetoothOpen ? 320 : 480)) * root.controlCenterScale)
                                                          : (root.popupKind === "model" ? 370 : (root.popupKind === "environments" ? root.environmentPopupHeight : (root.popupKind === "battery" ? 650 : 440))))
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
            onClicked: (mouse) => {
                var target = root.popupBarTargetAt(mouse.x, mouse.y)
                if (mouse.button === Qt.LeftButton && target && target === pressedBarTarget)
                    target.activated()
                else
                    root.closePopup()
                pressedBarTarget = null
            }
        }

        Rectangle {
            id: popupBackground
            visible: popup.open
            x: root.popupLeftMargin
            // Match the outer window contour; the inner top is at bar + 20px.
            y: 46 + 19
            width: root.popupKind === "controls" ? popup.menuWidth / root.controlCenterScale : popup.menuWidth
            height: Math.min(popup.menuHeight, popup.height - y - 8,
                             root.popupKind === "calendar" || root.popupKind === "environments"
                             ? popup.menuHeight : menuContent.implicitHeight + 20)
                    / (root.popupKind === "controls" ? root.controlCenterScale : 1)
            Keys.onPressed: function(event) { root.navigateGenericMenu(event) }
            scale: root.popupKind === "controls" ? root.controlCenterScale : 1
            opacity: 1
            transformOrigin: Item.TopLeft
            radius: 10
            color: root.popupPanel
            border.width: 1
            border.color: root.shellBorder

            // Animators run on the render thread; menu refreshes cannot stall them.
            ParallelAnimation {
                id: popupOpenAnimation
                onFinished: root.flushEnvironmentCatalog()
                OpacityAnimator { target: popupBackground; from: 0.001; to: 1; duration: 160; easing.type: Easing.OutCubic }
                ScaleAnimator {
                    target: popupBackground
                    from: (root.popupKind === "controls" ? root.controlCenterScale : 1) * 0.96
                    to: root.popupKind === "controls" ? root.controlCenterScale : 1
                    duration: 160; easing.type: Easing.OutCubic
                }
            }


            // Blank space inside the card must not fall through to dismissal.
            MouseArea { anchors.fill: parent; acceptedButtons: Qt.AllButtons }

            HoverHandler {
                id: popupHover
            }

            TapHandler {
                acceptedButtons: Qt.LeftButton
                onTapped: function(eventPoint) {
                    if (root.popupKind !== "controls" || !root.wifiPasswordVisible)
                        return
                    var corner = wifiPasswordCard.mapToItem(popupBackground, 0, 0)
                    var insidePassword = eventPoint.position.x >= corner.x
                                      && eventPoint.position.x <= corner.x + wifiPasswordCard.width
                                      && eventPoint.position.y >= corner.y
                                      && eventPoint.position.y <= corner.y + wifiPasswordCard.height
                    if (!insidePassword) {
                        Qt.callLater(function() {
                            if (!root.wifiSelectionTap)
                                root.cancelWifiPassword()
                            root.wifiSelectionTap = false
                        })
                    }
                }
            }

            Flickable {
                id: menuFlick
                anchors.fill: parent
                anchors.margins: 10
                contentWidth: width
                contentHeight: menuContent.implicitHeight
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                flickableDirection: Flickable.VerticalFlick
                pixelAligned: true
                ScrollBar.vertical: ScrollBar {
                    policy: menuContent.implicitHeight > popupBackground.height - 20
                            ? ScrollBar.AsNeeded : ScrollBar.AlwaysOff
                }

                Column {
                    id: menuContent
                    // Keep edge antialiasing inside the scroll viewport.
                    x: 1
                    width: parent.width - 2
                    spacing: 5

                    Column {
                        id: calendarMenu
                        width: parent.width
                        spacing: 5
                        visible: root.popupKind === "calendar" && !root.calendarEditor
                        focus: visible
                        Keys.onPressed: function(event) { root.handleCalendarKey(event) }

                        MenuHeader { title: "Calendário" }

                        Row {
                            width: parent.width
                            spacing: 4
                            Rectangle {
                                    width: 32; height: 28; radius: 6
                                    color: root.calendarActionIsFocused("previous", "previous") ? root.controlButtonActive : (previousMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                                    border.width: root.calendarActionIsFocused("previous", "previous") ? 1 : 0; border.color: root.cyan
                                Text { anchors.centerIn: parent; text: "‹"; color: root.textMain; font.pixelSize: 22 }
                                BounceMouseArea { id: previousMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.moveCalendar(-1) }
                            }
                            Text {
                                width: parent.width - 72; height: 28; text: root.calendarTitle(); color: root.textMain
                                horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                                font.family: "Selawik"; font.pixelSize: root.menuTitleSize; font.weight: Font.DemiBold
                            }
                            Rectangle {
                                    width: 32; height: 28; radius: 6
                                    color: root.calendarActionIsFocused("next", "next") ? root.controlButtonActive : (nextMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                                    border.width: root.calendarActionIsFocused("next", "next") ? 1 : 0; border.color: root.cyan
                                Text { anchors.centerIn: parent; text: "›"; color: root.textMain; font.pixelSize: 22 }
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
                                    width: (menuContent.width - 10) / 3; height: 25; radius: 6
                                    color: root.calendarActionIsFocused("view", modelData.key) ? root.controlButtonActive : (root.calendarView === modelData.key ? root.controlButtonActive : root.controlButtonSurface)
                                    border.width: root.calendarActionIsFocused("view", modelData.key) ? 1 : 0
                                    border.color: root.calendarActionIsFocused("view", modelData.key) ? root.cyan : root.cyan
                                    Text { anchors.centerIn: parent; text: modelData.label; color: root.calendarView === modelData.key ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                    BounceMouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.calendarView = modelData.key }
                                }
                            }
                        }

                        Rectangle {
                            id: calendarMonthDaysSurface
                            width: parent.width
                            height: visible ? calendarMonthGrid.implicitHeight + 12 : 0
                            visible: root.calendarView === "month"
                            radius: 8
                            color: root.card
                            border.width: 1
                            border.color: root.controlButtonOutline

                            Grid {
                                id: calendarMonthGrid
                                anchors.fill: parent
                                anchors.margins: 6
                                columns: 7; rowSpacing: 1; columnSpacing: 3
                                Repeater {
                                    model: root.weekNames
                                    Text {
                                        required property string modelData
                                        width: (calendarMonthGrid.width - 18) / 7; height: 18; text: modelData
                                        color: root.textDim; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                                        font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                                    }
                                }
                                Repeater {
                                    model: root.monthDays()
                                    Rectangle {
                                        required property var modelData
                                        property bool today: modelData !== null && root.sameDay(modelData, root.currentDate)
                                        property bool selected: modelData !== null && root.dateKey(modelData) === root.calendarSelectedDateKey
                                        width: (calendarMonthGrid.width - 18) / 7; height: 30; radius: 6
                                        color: modelData !== null && root.calendarActionIsFocused("date", root.dateKey(modelData)) ? root.controlButtonActive : (selected ? root.controlButtonActive : (dayMouse.containsMouse && modelData !== null ? root.controlButtonHover : "transparent"))
                                        SelectionIndicator { visible: parent.selected }
                                        border.width: modelData !== null && root.calendarActionIsFocused("date", root.dateKey(modelData)) ? 1 : 0
                                        border.color: modelData !== null && root.calendarActionIsFocused("date", root.dateKey(modelData)) ? root.cyan : root.cyan
                                        Rectangle {
                                            visible: parent.today && !parent.selected
                                            anchors.fill: parent; anchors.margins: parent.selected ? 4 : 2
                                            radius: 4; color: "transparent"
                                            border.width: 1; border.color: "#ffb15a"
                                        }
                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData === null ? "" : modelData.getDate()
                                            color: parent.selected ? root.textMain : (parent.today ? "#ffc36b" : root.textMain)
                                            font.family: "Selawik"; font.pixelSize: root.menuBodySize
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
                                    width: (menuContent.width - 8) / 3; height: 44; radius: 7
                                    color: root.calendarActionIsFocused("month", index) ? root.controlButtonActive : (currentMonth ? root.controlButtonActive : (monthMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface))
                                    border.width: root.calendarActionIsFocused("month", index) ? 1 : 0
                                    border.color: root.calendarActionIsFocused("month", index) ? root.cyan : root.cyan
                                    Text { anchors.centerIn: parent; text: modelData.slice(0, 3); color: parent.currentMonth ? root.textMain : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                    BounceMouseArea {
                                        id: monthMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                        onClicked: { root.calendarDate = new Date(root.calendarDate.getFullYear(), index, 1); root.calendarView = "month" }
                                    }
                                }
                            }
                        }

                        Column {
                            width: parent.width
                            spacing: 6
                            visible: root.calendarView === "day"

                            Text {
                                visible: root.eventsForDate(root.calendarDate).length === 0
                                text: "Nenhum Evento neste Dia"
                                color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                            }
                            ListView {
                                id: dayTimeline
                                width: parent.width
                                height: Math.min(4, count) * 50
                                spacing: 3
                                clip: true
                                interactive: count > 4
                                model: root.sortedEventsForDate(root.calendarDate)
                                ScrollBar.vertical: ScrollBar {
                                    policy: dayTimeline.count > 4 ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff
                                }
                                delegate: Item {
                                    required property var modelData
                                    width: dayTimeline.width
                                    height: 47

                                    Text {
                                        width: 52; anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                                        text: modelData.time
                                        color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
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
                                        height: 44; radius: 7; color: root.controlButtonSurface
                                        Text {
                                            anchors.left: parent.left; anchors.leftMargin: 11; anchors.top: parent.top; anchors.topMargin: 7
                                            width: parent.width - 112
                                            text: modelData.title
                                            elide: Text.ElideRight; color: root.textMain
                                            font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                                        }
                                        Text {
                                            anchors.left: parent.left; anchors.leftMargin: 11; anchors.bottom: parent.bottom; anchors.bottomMargin: 6
                                            width: parent.width - 112
                                            text: modelData.category + (modelData.notes ? " · " + modelData.notes : "")
                                            elide: Text.ElideRight; color: root.textDim
                                            font.family: "Selawik"; font.pixelSize: root.menuSmallSize
                                        }
                                        Rectangle {
                                            id: timelineEdit
                                            anchors.right: timelineRemove.left; anchors.rightMargin: 5; anchors.verticalCenter: parent.verticalCenter
                                            width: 54; height: 28; radius: 5
                                            color: root.calendarActionIsFocused("edit", modelData.id) ? root.controlButtonActive : (timelineEditMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                                            border.width: root.calendarActionIsFocused("edit", modelData.id) ? 1 : 0; border.color: root.cyan
                                            Text { anchors.centerIn: parent; text: "Editar"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                            BounceMouseArea { id: timelineEditMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.beginEditEvent(modelData) }
                                        }
                                        Rectangle {
                                            id: timelineRemove
                                            anchors.right: parent.right; anchors.rightMargin: 7; anchors.verticalCenter: parent.verticalCenter
                                            width: 28; height: 28; radius: 5
                                            color: root.calendarActionIsFocused("delete", modelData.id) ? "#743541" : (timelineRemoveMouse.containsMouse ? "#743541" : root.controlButtonSurface)
                                            border.width: root.calendarActionIsFocused("delete", modelData.id) ? 1 : 0; border.color: "#ffd3da"
                                            Text { anchors.centerIn: parent; text: "×"; color: "#ff91a4"; font.pixelSize: 16 }
                                            BounceMouseArea { id: timelineRemoveMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.deleteEvent(modelData.id) }
                                        }
                                    }
                                }
                            }
                        }

                        Row {
                            width: parent.width
                            spacing: 6
                            Rectangle {
                                width: (parent.width - 6) / 2; height: 34; radius: 6
                                color: root.calendarActionIsFocused("today", "today") ? root.controlButtonActive : (todayMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                                border.width: root.calendarActionIsFocused("today", "today") ? 1 : 0; border.color: root.cyan
                                Text { anchors.centerIn: parent; text: "[ Hoje ]"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                BounceMouseArea { id: todayMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.selectCalendarDate(root.currentDate) }
                            }
                            Rectangle {
                                width: (parent.width - 6) / 2; height: 34; radius: 6
                                color: root.calendarActionIsFocused("new", "new") ? root.controlButtonActive : (addMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                                border.width: root.calendarActionIsFocused("new", "new") ? 1 : 0; border.color: root.cyan
                                Text { anchors.centerIn: parent; text: "[ + ] Novo evento"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                BounceMouseArea { id: addMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.beginEvent() }
                            }
                        }

                        Text {
                            visible: root.calendarView !== "day"
                            text: "Eventos : " + root.dateKey(root.calendarDate)
                            color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                        }
                        Text {
                            visible: root.calendarView !== "day" && root.eventsForDate(root.calendarDate).length === 0
                            text: "Nenhum Evento neste Dia"
                            color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize
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
                            ScrollBar.vertical: ScrollBar {
                                policy: dayEventList.count > 4 ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff
                            }
                            delegate: Rectangle {
                                required property var modelData
                                width: menuContent.width; height: 42; radius: 6
                                color: root.controlButtonSurface; opacity: modelData.active ? 1 : 0.55
                                Rectangle { width: 4; height: parent.height; radius: 2; color: root.textMain }
                                Text {
                                    anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter
                                    width: parent.width - 108
                                    text: modelData.time + "  " + modelData.title + "  [" + modelData.category + "]"
                                    elide: Text.ElideRight; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                                }
                                Rectangle {
                                    id: editEvent
                                    anchors.right: removeEvent.left; anchors.rightMargin: 5; anchors.verticalCenter: parent.verticalCenter
                                    width: 54; height: 28; radius: 5
                                    color: root.calendarActionIsFocused("edit", modelData.id) ? root.controlButtonActive : (editMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                                    border.width: root.calendarActionIsFocused("edit", modelData.id) ? 1 : 0; border.color: root.cyan
                                    Text { anchors.centerIn: parent; text: "Editar"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                    BounceMouseArea { id: editMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.beginEditEvent(modelData) }
                                }
                                Rectangle {
                                    id: removeEvent
                                    anchors.right: parent.right; anchors.rightMargin: 6; anchors.verticalCenter: parent.verticalCenter
                                    width: 28; height: 28; radius: 5
                                    color: root.calendarActionIsFocused("delete", modelData.id) ? "#743541" : (removeMouse.containsMouse ? "#743541" : root.controlButtonSurface)
                                    border.width: root.calendarActionIsFocused("delete", modelData.id) ? 1 : 0; border.color: "#ffd3da"
                                    Text { anchors.centerIn: parent; text: "×"; color: "#ff91a4"; font.pixelSize: 16 }
                                    BounceMouseArea { id: removeMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.deleteEvent(modelData.id) }
                                }
                            }
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 6
                        visible: root.popupKind === "calendar" && root.calendarEditor

                        Row {
                            width: parent.width
                            Text {
                                width: parent.width - 42; height: 30; verticalAlignment: Text.AlignVCenter
                                text: root.editingEventId ? "[ Editar evento ]" : "[ + ] Novo evento"
                                color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuTitleSize; font.weight: Font.DemiBold
                            }
                            Rectangle {
                                width: 34; height: 30; radius: 6; color: cancelTopMouse.containsMouse ? "#743541" : root.controlButtonSurface
                                Text { anchors.centerIn: parent; text: "×"; color: "#ff91a4"; font.pixelSize: 18 }
                                BounceMouseArea { id: cancelTopMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.cancelCalendarEditor() }
                            }
                        }
                        Text { text: "Título"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                        EventField { id: calendarTitleField; text: root.draftTitle; placeholder: "Nome do evento"; onTextChanged: root.draftTitle = text }

                        Row {
                            width: parent.width; spacing: 6
                            Column {
                                width: (parent.parent.width - 6) * 0.62; spacing: 4
                                Text { text: "Data (AAAA-MM-DD)"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                                EventField { id: calendarDateField; width: parent.width; text: root.draftDate; placeholder: "2026-08-02"; onTextChanged: root.draftDate = text }
                            }
                            Column {
                                width: (parent.parent.width - 6) * 0.38; spacing: 4
                                Text { text: "Hora"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                                EventField { id: calendarTimeField; width: parent.width; text: root.draftTime; placeholder: "09:00"; onTextChanged: root.draftTime = text }
                            }
                        }

                        Text { text: "Categoria"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                        Rectangle {
                            id: categoryButton
                            width: parent.width; height: 34; radius: 6
                            activeFocusOnTab: true
                            color: activeFocus ? root.controlButtonActive : (categoryButtonMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                            border.width: root.categoryPickerOpen || activeFocus ? 1 : 0; border.color: activeFocus ? root.cyan : root.controlButtonOutline
                            Keys.onPressed: function(event) {
                                if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                    root.categoryPickerOpen = !root.categoryPickerOpen
                                    event.accepted = true
                                }
                            }
                            Text {
                                anchors.left: parent.left; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter
                                text: root.draftCategory || "Escolher categoria"
                                color: root.draftCategory ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                            }
                            Text { anchors.right: parent.right; anchors.rightMargin: 10; anchors.verticalCenter: parent.verticalCenter; text: root.categoryPickerOpen ? "▴" : "▾"; color: root.textMain }
                            BounceMouseArea { id: categoryButtonMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.categoryPickerOpen = !root.categoryPickerOpen }
                        }
                        Column {
                            width: parent.width; spacing: 4; visible: root.categoryPickerOpen
                            Text {
                                visible: root.calendarCategories.length === 0
                                text: "-- ainda não existem categorias --"
                                color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize
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
                                    Text { anchors.left: parent.left; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter; text: modelData; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                                    BounceMouseArea {
                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                        onClicked: { root.draftCategory = modelData; root.categoryPickerOpen = false }
                                    }
                                }
                            }
                            Rectangle {
                                width: parent.width; height: 30; radius: 5; activeFocusOnTab: true
                                color: activeFocus ? root.controlButtonActive : (newCategoryMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                                border.width: activeFocus ? 1 : 0; border.color: root.cyan
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                        root.newCategoryOpen = true
                                        event.accepted = true
                                    }
                                }
                                Text { anchors.centerIn: parent; text: "[ + ] Criar nova categoria"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                BounceMouseArea { id: newCategoryMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.newCategoryOpen = true }
                            }
                        }
                        Row {
                            width: parent.width; spacing: 6; visible: root.newCategoryOpen
                            EventField { id: newCategoryField; width: parent.width - 86; text: root.newCategoryName; placeholder: "Nome da categoria"; onTextChanged: root.newCategoryName = text }
                            Rectangle {
                                width: 80; height: 34; radius: 6; activeFocusOnTab: true
                                color: activeFocus ? root.controlButtonHover : (createCategoryMouse.containsMouse ? root.controlButtonHover : root.controlButtonOutline)
                                border.width: activeFocus ? 1 : 0; border.color: root.cyan
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                        root.createCategory()
                                        event.accepted = true
                                    }
                                }
                                Text { anchors.centerIn: parent; text: "Criar"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                BounceMouseArea { id: createCategoryMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.createCategory() }
                            }
                        }

                        Text { text: "Notas (opcional)"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                        EventField { id: calendarNotesField; text: root.draftNotes; placeholder: "Local, descrição, ligação…"; onTextChanged: root.draftNotes = text }

                        Text { text: "Partilha"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                        EventToggle {
                            width: parent.width
                            label: root.draftShared ? "Partilhar entre Environments" : "Não Partilhar entre Environments"
                            checked: root.draftShared
                            onActivated: root.draftShared = !root.draftShared
                        }

                        Text { text: "Avisar antes"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
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
                                    width: (menuContent.width - 73) / 4; height: 34; radius: 5
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
                                    Text {
                                        anchors.centerIn: parent; text: modelData
                                        color: root.draftReminderUnit === modelData ? root.textMain : root.textDim
                                        font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                                    }
                                    BounceMouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.draftReminderUnit = modelData }
                                }
                            }
                        }
                        Rectangle {
                            width: parent.width; height: 34; radius: 6; activeFocusOnTab: true
                            color: activeFocus ? root.controlButtonHover : (addReminderMouse.containsMouse ? root.controlButtonHover : root.controlButtonOutline)
                            border.width: 1; border.color: activeFocus ? root.cyan : root.controlButtonOutline
                            Keys.onPressed: function(event) {
                                if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                    root.addDraftReminder()
                                    event.accepted = true
                                }
                            }
                            Text {
                                anchors.centerIn: parent
                                text: "[ + ] Adicionar lembrete"
                                color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                            }
                            BounceMouseArea {
                                id: addReminderMouse
                                anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                onClicked: root.addDraftReminder()
                            }
                        }
                        Text {
                            visible: root.draftReminders.length === 0
                            text: "-- sem lembretes adicionados --"
                            color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                        }
                        Flow {
                            width: parent.width
                            spacing: 5
                            Repeater {
                                model: root.draftReminders
                                Rectangle {
                                    required property int modelData
                                    height: 30
                                    width: reminderText.implicitWidth + 42
                                    radius: 6; color: activeFocus ? "#49242c" : root.controlButtonSurface
                                    activeFocusOnTab: true
                                    border.width: 1; border.color: activeFocus ? "#ffd3da" : root.controlButtonOutline
                                    Keys.onPressed: function(event) {
                                        if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space || event.key === Qt.Key_Delete) {
                                            root.removeDraftReminder(modelData)
                                            event.accepted = true
                                        }
                                    }
                                    Text {
                                        id: reminderText
                                        anchors.left: parent.left; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter
                                        text: root.reminderLabel(modelData)
                                        color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                                    }
                                    Text {
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

                        Text {
                            visible: root.eventError.length > 0
                            text: root.eventError; color: "#ff91a4"; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                        }
                        Row {
                            width: parent.width; spacing: 6
                            Rectangle {
                                width: (parent.width - 6) / 2; height: 36; radius: 6; activeFocusOnTab: true
                                color: activeFocus ? root.controlButtonActive : (cancelMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                                border.width: activeFocus ? 1 : 0; border.color: root.cyan
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                        root.cancelCalendarEditor()
                                        event.accepted = true
                                    }
                                }
                                Text { anchors.centerIn: parent; text: "Cancelar"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                                BounceMouseArea { id: cancelMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.cancelCalendarEditor() }
                            }
                            Rectangle {
                                width: (parent.width - 6) / 2; height: 36; radius: 6; activeFocusOnTab: true
                                color: activeFocus ? root.controlButtonHover : (saveMouse.containsMouse ? root.controlButtonHover : root.controlButtonOutline)
                                border.width: 1; border.color: activeFocus ? root.cyan : root.controlButtonOutline
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                                        root.saveDraftEvent()
                                        event.accepted = true
                                    }
                                }
                                Text { anchors.centerIn: parent; text: root.editingEventId ? "Guardar alterações" : "Guardar evento"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                BounceMouseArea { id: saveMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.saveDraftEvent() }
                            }
                        }
                    }

                MenuHeader {
                    visible: root.popupKind !== "calendar"
                    title: root.popupKind === "battery" ? "Bateria e Energia" : (root.popupKind === "controls" ? "Central de Controlo" : (root.popupKind === "model" ? "Modelo Local" : (root.popupKind === "environments" ? "Environments" : "[ " + root.popupKind.toUpperCase() + " Control ]")))
                }

                Column {
                    width: parent.width; spacing: 10; visible: root.popupKind === "model"
                    Rectangle {
                        width: parent.width; height: 82; radius: 11; color: root.controlButtonSurface
                        Text { anchors.left: parent.left; anchors.leftMargin: 12; anchors.top: parent.top; anchors.topMargin: 14; anchors.right: parent.right; anchors.rightMargin: 12; elide: Text.ElideRight; text: root.modelStoreState.model || "Qwen2.5-Coder 3B Fast"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                        Text { anchors.left: parent.left; anchors.leftMargin: 12; anchors.bottom: parent.bottom; anchors.bottomMargin: 11; text: root.modelStoreState.state === "active" ? "● IA ativa" : (root.modelStoreState.state === "model-stopped" ? "○ IA desligada · SSD ligado" : (root.modelStoreState.state === "safe-to-remove" ? "● SSD pronto a remover" : "○ SSD não ligado")); color: root.modelStoreState.state === "active" ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize }
                    }
                    Text { width: parent.width; text: "Selecionar modelo"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                    Row {
                        id: modelSelectorRow
                        property real cellWidth: (width - 8) / 3
                        width: parent.width; height: 36; spacing: 4
                        Repeater {
                            model: root.modelStoreState.models || []
                            delegate: MenuButton {
                                required property var modelData
                                width: modelSelectorRow.cellWidth; height: modelSelectorRow.height
                                enabled: !root.modelStoreBusy && root.modelStoreState.mounted === true
                                label: (root.modelStoreState.selected_profile === modelData.profile ? "● " : "") + (modelData.profile === "fast" ? "3B" : (modelData.profile === "balanced" ? "7B" : "30B"))
                                accent: root.modelStoreState.selected_profile === modelData.profile
                                selected: accent
                                onActivated: if (!root.modelStoreBusy && root.modelStoreState.mounted === true && root.modelStoreState.selected_profile !== modelData.profile) root.modelStoreAction("model-select", modelData.profile)
                            }
                        }
                    }
                    Rectangle {
                        width: parent.width; height: root.modelSwitchActive ? 52 : modelDetail.implicitHeight + 8; radius: 8; color: root.modelSwitchActive ? root.controlButtonSurface : "transparent"
                        Text { id: modelDetail; visible: !root.modelSwitchActive; anchors.left: parent.left; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; wrapMode: Text.WordWrap; text: root.modelStoreState.model_detail || ""; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize }
                        Text { visible: root.modelSwitchActive; anchors.left: parent.left; anchors.leftMargin: 9; anchors.right: parent.right; anchors.rightMargin: 9; anchors.top: parent.top; anchors.topMargin: 7; text: "A ligar ao novo modelo · " + root.modelSwitchProgress + "%"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                        Text { visible: root.modelSwitchActive; anchors.left: parent.left; anchors.leftMargin: 9; anchors.right: parent.right; anchors.rightMargin: 9; anchors.top: parent.top; anchors.topMargin: 23; elide: Text.ElideRight; text: root.modelSwitchLabel; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize }
                        Rectangle { visible: root.modelSwitchActive; anchors.left: parent.left; anchors.leftMargin: 9; anchors.right: parent.right; anchors.rightMargin: 9; anchors.bottom: parent.bottom; anchors.bottomMargin: 5; height: 4; radius: 2; color: root.controlButtonOutline; Rectangle { width: parent.width * Math.max(0, Math.min(100, root.modelSwitchProgress)) / 100; height: parent.height; radius: 2; color: root.textMain } }
                    }
                    Text { width: parent.width; wrapMode: Text.WordWrap; text: root.modelStoreError.length ? root.modelStoreError : (root.modelStoreState.message || "A verificar…"); color: root.modelStoreError.length ? "#ff91a4" : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize }
                    Column {
                        width: parent.width; spacing: 6
                        MenuButton { width: parent.width; height: 36; enabled: !root.modelStoreBusy && root.modelStoreState.mounted === true; label: root.modelStoreState.server_active ? "Desativar IA" : "Ativar IA"; accent: true; onActivated: if (!root.modelStoreBusy && root.modelStoreState.mounted === true) root.modelStoreAction(root.modelStoreState.server_active ? "model-stop" : "model-start") }
                        MenuButton { width: parent.width; height: 36; enabled: !root.modelStoreBusy && root.modelStoreState.device_present === true; label: root.modelStoreState.mounted ? (root.modelStoreConfirmDetach ? "Confirmar remoção do SSD" : "Remover SSD em segurança") : "Ligar SSD"; onActivated: { if (!root.modelStoreBusy && root.modelStoreState.device_present === true) { if (!root.modelStoreState.mounted) root.modelStoreAction("storage-activate"); else if (root.modelStoreConfirmDetach) root.modelStoreAction("safe-detach"); else root.modelStoreConfirmDetach = true } } }
                    }
                    Text { visible: root.modelStoreConfirmDetach; width: parent.width; wrapMode: Text.WordWrap; text: "Segundo toque: para a IA, sincroniza, desmonta e fecha a cifra."; color: "#ffd09a"; font.family: "Selawik"; font.pixelSize: root.menuMetaSize }
                }

                Column {
                    id: environmentMenu
                    width: parent.width; spacing: 8
                    visible: root.popupKind === "environments"
                    focus: visible && root.isHub
                    Keys.onPressed: function(event) {
                        if (!root.isHub) { root.navigateGenericMenu(event); return }
                        if (!root.environmentKeyboardFocus && [Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down, Qt.Key_Return, Qt.Key_Enter].indexOf(event.key) >= 0) {
                            root.environmentKeyboardFocus = true
                            root.menuKeyboardNavigation = true
                            if (!root.environmentEditOpen && !root.environmentCreateOpen && !root.environmentDeleteConfirm) {
                                root.environmentFocusIndex = -1
                                root.moveEnvironmentFocus(1)
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
                        property bool keyboardFocused: false
                        width: parent.width; height: 62; radius: 9
                        color: keyboardFocused ? root.controlButtonActive : root.controlButtonSurface
                        border.width: 1
                        border.color: keyboardFocused ? root.cyan : root.controlButtonOutline
                        Rectangle { anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter; width: 9; height: 9; radius: 5; color: root.textMain }
                        Column {
                            anchors.left: parent.left; anchors.leftMargin: 34; anchors.right: activeEnvironmentBadge.left; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; spacing: 3
                            Text { width: parent.width; text: root.environmentLabel; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuTitleSize; font.weight: Font.DemiBold; elide: Text.ElideRight }
                            Text { width: parent.width; text: root.isHub ? "Centro de gestão e segurança" : "Environment isolado em execução"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; elide: Text.ElideRight }
                        }
                        Rectangle {
                            id: activeEnvironmentBadge
                            anchors.right: parent.right; anchors.rightMargin: 10; anchors.verticalCenter: parent.verticalCenter
                            width: 58; height: 24; radius: 12; color: root.controlButtonActive
                            Text { anchors.centerIn: parent; text: "Ativo"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                        }
                    }

                    Column {
                        width: parent.width; spacing: 7
                        visible: root.isHub && !root.environmentCreateOpen && !root.environmentEditOpen
                        Row {
                            width: parent.width; height: 24
                            Text { width: parent.width * 0.42; anchors.verticalCenter: parent.verticalCenter; text: "Os teus Environments"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                            Text { width: parent.width * 0.58; anchors.verticalCenter: parent.verticalCenter; horizontalAlignment: Text.AlignRight; text: root.environmentStorageSummary(); color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; elide: Text.ElideLeft }
                        }
                        Repeater {
                            model: root.environmentCatalog.length ? root.environmentCatalog : [{ name: "", display_name: "Ainda não tens Environments", state: "empty", generation: "", category: "general" }]
                            Rectangle {
                                required property var modelData
                                required property int index
                                width: parent ? parent.width : 400; height: 59; radius: 9
                                property bool selected: modelData.name.length > 0 && root.selectedEnvironmentName === modelData.name
                                property bool keyboardFocused: root.environmentIsOpenable(modelData) && root.environmentKeyboardFocus && root.environmentFocusIndex === index
                                color: keyboardFocused ? root.controlButtonActive : (selected ? root.controlButtonActive : (environmentChoiceMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface))
                                SelectionIndicator { visible: parent.selected }
                                border.width: 1; border.color: keyboardFocused ? root.cyan : root.controlButtonOutline
                                Rectangle { anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter; width: 8; height: 8; radius: 4; color: root.environmentIsOpenable(modelData) ? (parent.selected ? root.textMain : "#5d7b82") : "#79505a" }
                                Column {
                                    anchors.left: parent.left; anchors.leftMargin: 32; anchors.right: environmentRowStatus.left; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; spacing: 3
                                    Text { width: parent.width; text: String(modelData.display_name || modelData.name); color: modelData.state === "empty" ? root.textDim : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal; elide: Text.ElideRight }
                                    Row {
                                        width: parent.width; height: 16; spacing: 6
                                        Rectangle {
                                            visible: !!modelData.system_kind && modelData.system_kind !== "arch"
                                            width: visible ? systemTagText.implicitWidth + 10 : 0; height: 16; radius: 5
                                            color: root.controlButtonActive; border.width: 1; border.color: root.controlButtonOutline
                                            Text { id: systemTagText; anchors.centerIn: parent; text: String(modelData.system_label || "Sistema"); color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                                        }
                                        Text { width: parent.width - (modelData.system_kind && modelData.system_kind !== "arch" ? systemTagText.implicitWidth + 16 : 0); text: root.environmentMeta(modelData); color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; elide: Text.ElideRight }
                                    }
                                }
                                Text { id: environmentRowStatus; anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; text: root.environmentIsOpenable(modelData) ? root.environmentSizeLabel(modelData) : (modelData.state === "preparing" ? "A preparar" : (modelData.state === "empty" ? "" : "Indisponível")); color: parent.selected ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
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
                            width: parent.width; height: 42; spacing: 6
                            MenuButton { width: (parent.width - 12) * 0.44; height: parent.height; label: "Criar"; keyboardFocused: root.environmentKeyboardFocus && root.environmentFocusIndex === root.environmentCatalog.length; enabled: !root.environmentManagementBusy && !root.environmentMetadataBusy; onActivated: { root.environmentFocusIndex = root.environmentCatalog.length; root.beginEnvironmentCreate() } }
                            MenuButton { width: (parent.width - 12) * 0.31; height: parent.height; label: "Editar"; keyboardFocused: root.environmentKeyboardFocus && root.environmentFocusIndex === root.environmentCatalog.length + 1; enabled: root.selectedEnvironmentName.length > 0 && !root.environmentManagementBusy && !root.environmentMetadataBusy; onActivated: { root.environmentFocusIndex = root.environmentCatalog.length + 1; root.beginEnvironmentEdit() } }
                            MenuButton { width: (parent.width - 12) * 0.25; height: parent.height; label: "Apagar"; keyboardFocused: root.environmentKeyboardFocus && root.environmentFocusIndex === root.environmentCatalog.length + 2; enabled: root.selectedEnvironmentName.length > 0 && !root.environmentManagementBusy && !root.environmentMetadataBusy; onActivated: { root.environmentFocusIndex = root.environmentCatalog.length + 2; root.requestEnvironmentDelete() } }
                        }

                        Rectangle {
                            visible: root.environmentDeleteConfirm
                            width: parent.width; height: visible ? 80 : 0; radius: 8; color: "#29181d"; border.width: 1; border.color: "#7d3947"
                            Column { anchors.left: parent.left; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter; width: parent.width - 162; spacing: 2
                                Text { width: parent.width; text: "Apagar " + root.selectedEnvironmentName + "?"; color: "#ffb2bf"; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal; elide: Text.ElideRight }
                                Text { width: parent.width; text: root.environmentSelection() && root.environmentSelection().native_version === 3 ? "Apaga só este Windows e o seu EFI. Os 80 GiB ficam reservados para outro Windows; não é apagamento seguro." : (root.environmentIsNative(root.environmentSelection()) ? "Apaga a partição e devolve todo o espaço ao APX após reiniciar." : "Purga total: dados, VM, cópias e metadados."); color: "#b98992"; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; wrapMode: Text.WordWrap }
                            }
                            Row { anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter; spacing: 5
                                Rectangle { width: 62; height: 31; radius: 6; color: root.environmentDeleteFocusIndex === 0 ? root.controlButtonActive : "#21161a"; border.width: root.environmentDeleteFocusIndex === 0 ? 1 : 0; border.color: root.cyan
                                    Text { anchors.centerIn: parent; text: "Cancelar"; color: root.environmentDeleteFocusIndex === 0 ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                                    BounceMouseArea { id: cancelDeleteMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: { root.environmentDeleteFocusIndex = 0; root.cancelEnvironmentDelete() } }
                                }
                                Rectangle { width: 70; height: 31; radius: 6; color: root.environmentDeleteFocusIndex === 1 ? "#8a4050" : "#21161a"; border.width: root.environmentDeleteFocusIndex === 1 ? 1 : 0; border.color: "#ffd3da"
                                    Text { anchors.centerIn: parent; text: "Apagar"; color: root.environmentDeleteFocusIndex === 1 ? "#ffd3da" : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                                    BounceMouseArea { id: confirmDeleteMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: { root.environmentDeleteFocusIndex = 1; root.destroySelectedEnvironment() } }
                                }
                            }
                        }
                    }

                    Column {
                        width: parent.width; spacing: 9
                        visible: root.isHub && root.environmentEditOpen
                        Row {
                            width: parent.width; height: 32; spacing: 8
                            Rectangle {
                                width: 92; height: parent.height; radius: 6
                                color: root.environmentEditFocusIndex === 0 ? root.controlButtonActive : (environmentEditBackMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                                border.width: root.environmentEditFocusIndex === 0 ? 1 : 0
                                border.color: root.cyan
                                Text { anchors.centerIn: parent; text: "‹  Voltar"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                                BounceMouseArea { id: environmentEditBackMouse; anchors.fill: parent; enabled: !root.environmentMetadataBusy; hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor; onClicked: { root.environmentEditFocusIndex = 0; root.cancelEnvironmentEdit() } }
                            }
                            Text { width: parent.width - 100; anchors.verticalCenter: parent.verticalCenter; text: "Editar apresentação"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                        }
                        Text { width: parent.width; text: "O identificador interno “" + root.selectedEnvironmentName + "” não muda."; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; elide: Text.ElideRight }
                        Rectangle {
                            width: parent.width; height: 42; radius: 7; color: root.controlButtonSurface; border.width: 1; border.color: environmentEditTitleInput.activeFocus || root.environmentEditFocusIndex === 1 ? root.cyan : root.controlButtonOutline
                            TextInput {
                                id: environmentEditTitleInput; anchors.fill: parent; anchors.leftMargin: 11; anchors.rightMargin: 11; verticalAlignment: TextInput.AlignVCenter
                                text: root.environmentEditTitle; onTextChanged: root.environmentEditTitle = text; maximumLength: 64; enabled: !root.environmentMetadataBusy
                                color: root.textMain; selectionColor: root.controlButtonOutline; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                                onActiveFocusChanged: if (activeFocus) root.environmentEditFocusIndex = 1
                                onAccepted: { root.environmentEditFocusIndex = 2; environmentEditDescriptionInput.forceActiveFocus() }
                                Keys.priority: Keys.BeforeItem
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Tab) { root.environmentEditFocusIndex = 2; environmentEditDescriptionInput.forceActiveFocus(); event.accepted = true }
                                    else if (event.key === Qt.Key_Backtab) { root.environmentEditFocusIndex = 0; environmentMenu.forceActiveFocus(); event.accepted = true }
                                    else if (event.key === Qt.Key_Escape) { root.cancelEnvironmentEdit(); event.accepted = true }
                                }
                            }
                            Text { anchors.left: parent.left; anchors.leftMargin: 11; anchors.verticalCenter: parent.verticalCenter; visible: !environmentEditTitleInput.text.length; text: "Título do Environment"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                        }
                        Rectangle {
                            width: parent.width; height: 42; radius: 7; color: root.controlButtonSurface; border.width: 1; border.color: environmentEditDescriptionInput.activeFocus || root.environmentEditFocusIndex === 2 ? root.cyan : root.controlButtonOutline
                            TextInput {
                                id: environmentEditDescriptionInput; anchors.fill: parent; anchors.leftMargin: 11; anchors.rightMargin: 11; verticalAlignment: TextInput.AlignVCenter
                                text: root.environmentEditDescription; onTextChanged: root.environmentEditDescription = text; maximumLength: 120; enabled: !root.environmentMetadataBusy
                                color: root.textMain; selectionColor: root.controlButtonOutline; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                                onActiveFocusChanged: if (activeFocus) root.environmentEditFocusIndex = 2
                                onAccepted: { root.environmentEditFocusIndex = 3; environmentMenu.forceActiveFocus() }
                                Keys.priority: Keys.BeforeItem
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Tab) { root.environmentEditFocusIndex = 3; environmentMenu.forceActiveFocus(); event.accepted = true }
                                    else if (event.key === Qt.Key_Backtab) { root.environmentEditFocusIndex = 1; environmentEditTitleInput.forceActiveFocus(); event.accepted = true }
                                    else if (event.key === Qt.Key_Escape) { root.cancelEnvironmentEdit(); event.accepted = true }
                                }
                            }
                            Text { anchors.left: parent.left; anchors.leftMargin: 11; anchors.verticalCenter: parent.verticalCenter; visible: !environmentEditDescriptionInput.text.length; text: "Legenda (opcional)"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                        }
                        MenuButton {
                            width: parent.width; height: 42
                            label: root.environmentMetadataBusy ? "A guardar…" : "Guardar alterações"
                            accent: true
                            keyboardFocused: root.environmentEditFocusIndex === 3
                            enabled: !root.environmentMetadataBusy && root.environmentEditTitle.trim().length > 0
                            onActivated: { root.environmentEditFocusIndex = 3; root.saveEnvironmentMetadata() }
                        }
                    }

                    Column {
                        width: parent.width; spacing: 9
                        visible: root.isHub && root.environmentCreateOpen
                        Row {
                            width: parent.width; height: 32; spacing: 8
                            Rectangle {
                                width: 92; height: parent.height; radius: 6
                                color: root.environmentCreateFocusIndex === 0 ? root.controlButtonActive : (environmentBackMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                                border.width: root.environmentCreateFocusIndex === 0 ? 1 : 0
                                border.color: root.cyan
                                Text { anchors.centerIn: parent; text: "‹  Voltar"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                                BounceMouseArea { id: environmentBackMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: { root.environmentCreateFocusIndex = 0; root.cancelEnvironmentCreate() } }
                            }
                            Text { width: parent.width - 100; anchors.verticalCenter: parent.verticalCenter; text: "Novo environment"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                        }
                        Rectangle {
                            width: parent.width; height: 42; radius: 7; color: root.controlButtonSurface; border.width: 1; border.color: environmentNameInput.activeFocus || root.environmentCreateFocusIndex === 1 ? root.cyan : root.controlButtonOutline
                            TextInput {
                                id: environmentNameInput; anchors.fill: parent; anchors.leftMargin: 11; anchors.rightMargin: 11; verticalAlignment: TextInput.AlignVCenter
                                text: root.environmentDraftName; onTextChanged: root.environmentDraftName = text; maximumLength: 27
                                color: root.textMain; selectionColor: root.controlButtonOutline; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                                onActiveFocusChanged: if (activeFocus) root.environmentCreateFocusIndex = 1
                                onAccepted: { root.environmentCreateFocusIndex = 2; environmentDescriptionInput.forceActiveFocus() }
                                Keys.priority: Keys.BeforeItem
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Tab) {
                                        root.environmentCreateFocusIndex = 2
                                        environmentDescriptionInput.forceActiveFocus()
                                        event.accepted = true
                                    } else if (event.key === Qt.Key_Backtab) {
                                        root.environmentCreateFocusIndex = 0
                                        environmentMenu.forceActiveFocus()
                                        event.accepted = true
                                    }
                                }
                            }
                            Text { anchors.left: parent.left; anchors.leftMargin: 11; anchors.verticalCenter: parent.verticalCenter; visible: !environmentNameInput.text.length; text: "nome-do-environment"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                        }
                        Rectangle {
                            width: parent.width; height: 42; radius: 7; color: root.controlButtonSurface; border.width: 1; border.color: environmentDescriptionInput.activeFocus || root.environmentCreateFocusIndex === 2 ? root.cyan : root.controlButtonOutline
                            TextInput {
                                id: environmentDescriptionInput; anchors.fill: parent; anchors.leftMargin: 11; anchors.rightMargin: 11; verticalAlignment: TextInput.AlignVCenter
                                text: root.environmentDraftDescription; onTextChanged: root.environmentDraftDescription = text; maximumLength: 120
                                color: root.textMain; selectionColor: root.controlButtonOutline; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                                onActiveFocusChanged: if (activeFocus) root.environmentCreateFocusIndex = 2
                                onAccepted: { root.environmentCreateFocusIndex = 3; environmentMenu.forceActiveFocus() }
                                Keys.priority: Keys.BeforeItem
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Backtab) {
                                        root.environmentCreateFocusIndex = 1
                                        environmentNameInput.forceActiveFocus()
                                        event.accepted = true
                                    } else if (event.key === Qt.Key_Tab) {
                                        root.environmentCreateFocusIndex = 3
                                        environmentMenu.forceActiveFocus()
                                        event.accepted = true
                                    }
                                }
                            }
                            Text { anchors.left: parent.left; anchors.leftMargin: 11; anchors.verticalCenter: parent.verticalCenter; visible: !environmentDescriptionInput.text.length; text: "Descrição (opcional)"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                        }
                        Text { width: parent.width; text: "Base do environment"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                        Row {
                            width: parent.width; height: 78; spacing: 6
                            PresetCard { width: (parent.width - 6) / 2; height: parent.height; title: "APX · nativo"; description: "Environment isolado diretamente sobre o kernel do Host."; additions: "Máxima integração"; selected: root.environmentSystemKind === "arch"; keyboardFocused: root.environmentCreateFocusIndex === 3; onActivated: { root.environmentCreateFocusIndex = 3; root.environmentSystemKind = "arch" } }
                            PresetCard { width: (parent.width - 6) / 2; height: parent.height; title: "Windows · nativo"; description: "Uma instalação independente, com nome e espaço próprios."; additions: "Neste SSD · arranque nativo"; selected: root.environmentSystemKind === "windows-native"; keyboardFocused: root.environmentCreateFocusIndex === 4; onActivated: { root.environmentCreateFocusIndex = 4; root.environmentSystemKind = "windows-native"; if (!root.environmentDraftName.length || root.environmentDraftName === "windows") root.environmentDraftName = "windows-2" } }
                        }
                        Text { visible: root.environmentSystemKind === "windows-native"; width: parent.width; text: "Tamanho da partição Windows"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                        Row {
                            visible: root.environmentSystemKind === "windows-native"; height: visible ? 62 : 0
                            width: parent.width; spacing: 6
                            PresetCard { width: (parent.width - 12) / 3; height: parent.height; title: "80 GiB"; description: "Uso essencial"; additions: "Mínimo"; selected: root.environmentNativeWindowsSizeGib === 80; keyboardFocused: root.environmentCreateFocusIndex === 6; onActivated: { root.environmentCreateFocusIndex = 6; root.environmentNativeWindowsSizeGib = 80 } }
                            PresetCard { width: (parent.width - 12) / 3; height: parent.height; title: "120 GiB"; description: "Apps e estudo"; additions: "Mais espaço"; selected: root.environmentNativeWindowsSizeGib === 120; keyboardFocused: root.environmentCreateFocusIndex === 7; onActivated: { root.environmentCreateFocusIndex = 7; root.environmentNativeWindowsSizeGib = 120 } }
                            PresetCard { width: (parent.width - 12) / 3; height: parent.height; title: "160 GiB"; description: "Jogos e projetos"; additions: "Máximo"; selected: root.environmentNativeWindowsSizeGib === 160; keyboardFocused: root.environmentCreateFocusIndex === 8; onActivated: { root.environmentCreateFocusIndex = 8; root.environmentNativeWindowsSizeGib = 160 } }
                        }
                        Text { visible: root.environmentSystemKind === "arch"; width: parent.width; text: "Escolhe um ponto de partida"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                        Row {
                            visible: root.environmentSystemKind === "arch"; height: visible ? 78 : 0
                            width: parent.width; spacing: 6
                            PresetCard { width: (parent.width - 12) / 3; height: parent.height; title: "Básico · base APX"; description: "Desktop APX sem aplicações adicionais."; additions: "Extras · nenhum"; selected: root.environmentDesktopPreset === "basic"; keyboardFocused: root.environmentCreateFocusIndex === 6; onActivated: { root.environmentCreateFocusIndex = 6; root.applyEnvironmentPreset("basic") } }
                            PresetCard { width: (parent.width - 12) / 3; height: parent.height; title: "Intermédio · dia a dia"; description: "Base APX, Internet, ficheiros e multimédia."; additions: "+ Brave · PDF · MPV"; selected: root.environmentDesktopPreset === "intermediate"; keyboardFocused: root.environmentCreateFocusIndex === 7; onActivated: { root.environmentCreateFocusIndex = 7; root.applyEnvironmentPreset("intermediate") } }
                            PresetCard { width: (parent.width - 12) / 3; height: parent.height; title: "Completo · trabalho"; description: "Tudo do Intermédio, Office, periféricos e programação."; additions: "+ LibreOffice · dev · impressão"; selected: root.environmentDesktopPreset === "complete"; keyboardFocused: root.environmentCreateFocusIndex === 8; onActivated: { root.environmentCreateFocusIndex = 8; root.applyEnvironmentPreset("complete") } }
                        }
                        Row {
                            visible: root.environmentSystemKind === "arch"; height: visible ? 20 : 0
                            width: parent.width
                            Text { width: parent.width * 0.65; text: "Funcionalidades"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                            Text { width: parent.width * 0.35; horizontalAlignment: Text.AlignRight; text: root.selectedEnvironmentModuleKeys().length + "/18  ·  ~" + root.environmentEstimatedMib() + " MiB"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                        }
                        Column {
                            visible: root.environmentSystemKind === "arch"
                            width: parent.width; spacing: 5
                            Repeater {
                                model: root.environmentModuleGroups
                                Column {
                                    id: featureGroup
                                    required property var modelData
                                    required property int index
                                    width: parent ? parent.width : 660; spacing: 4
                                    Rectangle {
                                        width: parent.width; height: 34; radius: 7
                                        property bool keyboardFocused: root.environmentCreateFocusIndex === 9 + index
                                        color: keyboardFocused ? root.controlButtonActive : (featureDrawerMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface)
                                        border.width: keyboardFocused || root.environmentFeatureDrawer === modelData.key ? 1 : 0
                                        border.color: keyboardFocused ? root.cyan : root.controlButtonOutline
                                        Text { anchors.left: parent.left; anchors.leftMargin: 11; anchors.right: parent.right; anchors.rightMargin: 34; anchors.verticalCenter: parent.verticalCenter; text: modelData.label; color: root.environmentFeatureDrawer === modelData.key ? root.textMain : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal; elide: Text.ElideRight }
                                        Text { anchors.right: parent.right; anchors.rightMargin: 11; anchors.verticalCenter: parent.verticalCenter; text: root.environmentFeatureDrawer === modelData.key ? "▴" : "▾"; color: root.textDim; font.pixelSize: root.menuTitleSize }
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
                        Text { width: parent.width; text: root.environmentSystemKind === "windows-native" ? "Verifica primeiro o espaço para este Windows. O Windows atual será preservado; qualquer alteração necessária será apresentada antes da criação." : "A palavra-passe de sudo será herdada do HUB. Dependências são ativadas automaticamente."; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; wrapMode: Text.WordWrap }
                        Text {
                            visible: root.environmentSystemKind === "windows-native" && !!root.nativeCreationPreview.target
                            width: parent.width
                            text: root.nativeCreationPreview.target ? ("Windows atual: " + root.nativeCreationPreview.existing_windows_gib + " GiB · Novo: " + root.nativeCreationPreview.size_gib + " GiB · APX: " + root.nativeCreationPreview.apx_gib + " GiB\n" + root.nativeCreationPreview.message) : ""
                            color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; wrapMode: Text.WordWrap
                        }
                        MenuButton { width: parent.width; height: 42; label: root.environmentSystemKind === "windows-native" ? (nativeCreationPreviewProcess.running ? "A verificar…" : (root.nativeCreationPreview.can_create === true ? "Preparar Windows" : "Verificar espaço")) : (root.environmentManagementBusy ? "A criar…" : "Criar environment"); accent: true; keyboardFocused: root.environmentCreateFocusIndex === root.environmentCreateSubmitFocusIndex; enabled: !root.environmentManagementBusy && !nativeCreationPreviewProcess.running; onActivated: { root.environmentCreateFocusIndex = root.environmentCreateSubmitFocusIndex; root.createEnvironment(environmentNameInput.text, environmentDescriptionInput.text) } }
                    }

                    Rectangle {
                        visible: root.environmentManagementBusy
                        width: parent.width; height: visible ? 34 : 0; radius: 7; color: root.controlButtonSurface
                        Text { anchors.left: parent.left; anchors.leftMargin: 9; anchors.top: parent.top; anchors.topMargin: 5; text: root.environmentManagementState.message || "A preparar…"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                        Rectangle { anchors.left: parent.left; anchors.leftMargin: 9; anchors.right: parent.right; anchors.rightMargin: 9; anchors.bottom: parent.bottom; anchors.bottomMargin: 6; height: 4; radius: 2; color: root.controlButtonOutline; Rectangle { width: parent.width * Math.max(2, Math.min(100, root.environmentManagementState.progress || 2)) / 100; height: parent.height; radius: 2; color: root.textMain } }
                    }

                    Column {
                        visible: root.isHub && root.environmentManagementState.native_v3 === true
                        width: parent.width; spacing: 6
                        Text { width: parent.width; wrapMode: Text.WordWrap; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize
                            text: root.environmentManagementState.pending_stage === "deleting" ? "A eliminar apenas o Windows novo. Se a operação parou, podes continuá-la sem tocar no Windows atual." : (root.environmentManagementState.native_v3_activate ? (root.environmentManagementState.pending_mode === "slot-reuse" ? "O espaço reservado de " + root.environmentManagementState.new_size_gib + " GiB está pronto para receber outro Windows. A instalação reinicia o computador automaticamente e regressa ao Hub." : "A cópia está verificada. O Windows atual ficará com " + root.environmentManagementState.existing_size_gib + " GiB e o novo terá " + root.environmentManagementState.new_size_gib + " GiB. A instalação reinicia o computador automaticamente e regressa ao Hub.") : (root.environmentManagementState.native_v3_rollback ? "Podes repor o Windows anterior a partir da cópia guardada. A instalação nova incompleta será removida." : (root.environmentManagementState.native_v3_retry ? "A instalação nova falhou. Podes recomeçá-la; isso apaga apenas o Windows novo incompleto. O Windows atual e o APX ficam preservados." : (root.environmentManagementState.native_v3_manual_recovery ? "A instalação parou. Os dados e as partições foram preservados; é necessária uma recuperação assistida antes de tentar novamente." : "A preparar Windows. Acompanha o progresso acima."))))
                        }
                        MenuButton { visible: root.environmentManagementState.native_v3_activate === true; width: parent.width; height: visible ? 42 : 0
                            label: root.nativeV3Confirmation === "activate:" + root.environmentManagementState.pending_generation ? "Confirmar instalação e reinício" : "Instalar e reiniciar"
                            enabled: !environmentActionProcess.running; accent: true; onActivated: root.nativeV3Action("activate") }
                        MenuButton { visible: root.environmentManagementState.native_v3_rollback === true; width: parent.width; height: visible ? 42 : 0
                            label: root.nativeV3Confirmation === "rollback:" + root.environmentManagementState.pending_generation ? "Confirmar reposição" : "Repor Windows anterior"
                            enabled: !environmentActionProcess.running; onActivated: root.nativeV3Action("rollback") }
                        MenuButton { visible: root.environmentManagementState.native_v3_retry === true; width: parent.width; height: visible ? 42 : 0
                            label: root.nativeV3Confirmation === "retry:" + root.environmentManagementState.pending_generation ? "Confirmar nova tentativa" : "Recomeçar instalação nova"
                            enabled: !environmentActionProcess.running; onActivated: root.nativeV3Action("retry") }
                        MenuButton { visible: root.environmentManagementState.native_v3_delete_retry === true; width: parent.width; height: visible ? 42 : 0
                            label: root.nativeV3Confirmation === "delete:" + root.environmentManagementState.pending_generation ? "Confirmar continuar eliminação" : "Continuar eliminação"
                            enabled: !environmentActionProcess.running; onActivated: root.nativeV3Action("delete") }
                    }

                    Rectangle {
                        visible: root.isHub && root.nativeWindowsRecoveryAvailable()
                        width: parent.width; height: visible ? 92 : 0; radius: 8
                        color: "#291f18"; border.width: 1; border.color: "#765334"
                        Column {
                            anchors.fill: parent; anchors.margins: 8; spacing: 6
                            Text { width: parent.width; text: "A criação Windows parou em segurança. Podes recomeçar apenas essa instalação ou devolver o espaço ao APX."; wrapMode: Text.WordWrap; color: "#e5c29c"; font.family: "Selawik"; font.pixelSize: root.menuSmallSize }
                            Row {
                                width: parent.width; height: 34; spacing: 6
                                MenuButton { visible: root.environmentManagementState.native_retry === true; width: visible ? (root.environmentManagementState.native_discard === true ? (parent.width - 6) * 0.5 : parent.width) : 0; height: parent.height; label: root.environmentManagementState.pending_stage === "boot-prepared" ? "Prosseguir Windows" : "Retomar Windows"; accent: true; enabled: !environmentActionProcess.running; onActivated: root.recoverNativeWindows("retry") }
                                MenuButton { visible: root.environmentManagementState.native_discard === true; width: visible ? (root.environmentManagementState.native_retry === true ? (parent.width - 6) * 0.5 : parent.width) : 0; height: parent.height; label: root.nativeRecoveryDiscardConfirm ? "Confirmar apagar" : (root.environmentManagementState.native_retry === true ? "Apagar incompleto" : "Tentar apagar"); enabled: !environmentActionProcess.running; onActivated: { if (root.nativeRecoveryDiscardConfirm) root.recoverNativeWindows("discard"); else root.nativeRecoveryDiscardConfirm = true } }
                            }
                        }
                    }

                    MenuButton {
                        visible: !root.isHub
                        width: parent.width; height: visible ? 46 : 0; label: root.environmentSwitchPending ? "A regressar…" : "Voltar ao Hub"; accent: true
                        enabled: root.sessionKindReady && !root.environmentSwitchPending
                        onActivated: root.returnToHub()
                    }
                    Text { visible: !root.isHub; width: parent.width; horizontalAlignment: Text.AlignHCenter; text: "O Environment será fechado em segurança antes da troca."; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize }
                    Text { visible: root.environmentSwitchError.length > 0; width: parent.width; wrapMode: Text.WordWrap; text: root.environmentSwitchError; color: "#ff91a4"; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                }

                    Column {
                    width: parent.width
                    spacing: 5
                    visible: root.popupKind === "controls"

                    Row {
                        visible: root.controlsAllClosed() && !root.powerConfirmOpen
                        width: parent.width
                        height: visible ? 46 : 0
                        spacing: 6

                        Rectangle {
                            width: (parent.width - 6) / 2; height: parent.height; radius: 11
                            color: wifiSummaryMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            border.width: 1; border.color: root.controlButtonOutline
                            Text {
                                anchors.centerIn: parent
                                text: "Wi-Fi"; color: root.textMain
                                font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                            }
                            BounceMouseArea { id: wifiSummaryMouse; anchors.fill: parent; z: 1; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.openControlSection("wifi") }
                        }

                        Rectangle {
                            width: (parent.width - 6) / 2; height: parent.height; radius: 11
                            color: bluetoothSummaryMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            border.width: 1; border.color: root.controlButtonOutline
                            Text {
                                anchors.centerIn: parent
                                text: "Bluetooth"; color: root.textMain
                                font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                            }
                            BounceMouseArea { id: bluetoothSummaryMouse; anchors.fill: parent; z: 1; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.openControlSection("bluetooth") }
                        }
                    }

                    Rectangle {
                        visible: root.controlsWifiOpen
                        width: parent.width; height: visible ? 44 : 0; radius: 11
                        color: root.controlButtonSurface
                        border.width: 1; border.color: root.controlButtonOutline
                        Rectangle {
                            anchors.left: parent.left; anchors.leftMargin: 8; anchors.verticalCenter: parent.verticalCenter
                            width: 62; height: 28; radius: 8
                            color: wifiHeaderMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            Text { anchors.centerIn: parent; text: "‹ Voltar"; color: wifiHeaderMouse.containsMouse ? "#ffffff" : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                            BounceMouseArea { id: wifiHeaderMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.openControlSection("wifi") }
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter; anchors.verticalCenter: parent.verticalCenter
                            text: "Wi-Fi"
                            color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                        }
                        Text {
                            anchors.right: parent.right; anchors.rightMargin: 11; anchors.verticalCenter: parent.verticalCenter
                            text: root.wifiTogglePhase === "connecting" ? "A ligar…" : (root.wifiDisplayActive() ? "Ligado" : "Sem ligação")
                            color: root.wifiDisplayActive() ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize
                        }
                    }
                    Column {
                        width: parent.width; spacing: 4; visible: root.controlsWifiOpen
                        Rectangle {
                            width: parent.width; height: 56; radius: 11
                            color: root.wifiDisplayActive() ? root.controlButtonActive : root.controlButtonSurface
                            border.width: 1; border.color: root.wifiDisplayActive() ? root.controlButtonOutline : root.controlButtonOutline
                            Text {
                                anchors.left: parent.left; anchors.leftMargin: 14; anchors.top: parent.top; anchors.topMargin: 8
                                width: parent.width - 130; elide: Text.ElideRight
                                text: root.wifiDisplayActive() ? root.hostState.network_name : (root.wifiTogglePhase === "connecting" ? "A ligar a " + root.wifiLastNetwork : "Sem ligação")
                                color: root.wifiDisplayActive() ? root.textMain : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuTitleSize; font.weight: Font.DemiBold
                            }
                            Text {
                                anchors.left: parent.left; anchors.leftMargin: 14; anchors.bottom: parent.bottom; anchors.bottomMargin: 8
                                text: root.wifiDisplayActive()
                                    ? "● Ligado · " + root.wifiDetails(root.hostState.network_name).signal + "%"
                                    : (root.wifiTogglePhase === "connecting" ? "◌ A estabelecer ligação…" : "○ Sem ligação")
                                color: root.wifiDisplayActive() ? "#55dfa1" : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize
                            }
                            Rectangle {
                                visible: root.wifiDisplayActive() && root.wifiTogglePhase !== "connecting"
                                anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter
                                width: 84; height: 28; radius: 8
                                color: disconnectMouse.containsMouse ? "#743541" : root.controlButtonSurface
                                Text { anchors.centerIn: parent; text: "Desligar"; color: "#ffb0bd"; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                                BounceMouseArea { id: disconnectMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: { root.cancelWifiPassword(); root.toggleWifiConnection() } }
                            }
                        }

                        Item {
                            visible: !!root.hostState.network_name
                            width: parent.width
                            height: visible ? 6 : 0
                            BounceMouseArea { anchors.fill: parent; onClicked: root.cancelWifiPassword() }
                        }
                        Item {
                            width: parent.width; height: 18
                            BounceMouseArea { anchors.fill: parent; onClicked: root.cancelWifiPassword() }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: "Redes próximas  ·  " + (root.hostState.available_networks || []).length
                                color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal
                            }
                        }
                        Rectangle {
                            id: wifiPasswordCard
                            visible: root.wifiPasswordVisible
                            width: parent.width
                            height: visible ? ((!root.wifiIsKnown(root.wifiSelectedSsid) && !root.wifiIsOpen(root.wifiSelectedSsid)) ? 86 : 50) : 0
                            radius: 11
                            color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                            Column {
                                anchors.fill: parent; anchors.margins: 8; spacing: 5
                                Text { text: "Ligar a " + root.wifiSelectedSsid; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal; elide: Text.ElideRight; width: parent.width }
                                Rectangle {
                                    visible: !root.wifiIsKnown(root.wifiSelectedSsid) && !root.wifiIsOpen(root.wifiSelectedSsid)
                                    width: parent.width; height: visible ? 30 : 0; radius: 5; color: root.controlButtonSurface; border.width: wifiPasswordInput.activeFocus ? 1 : 0; border.color: root.cyan
                                    TextInput {
                                        id: wifiPasswordInput; anchors.fill: parent; anchors.leftMargin: 9; anchors.rightMargin: 9; verticalAlignment: TextInput.AlignVCenter
                                        activeFocusOnTab: true
                                        text: root.wifiPassword; onTextChanged: root.wifiPassword = text; echoMode: TextInput.Password; passwordCharacter: "•"
                                        color: root.textMain; selectionColor: root.controlButtonOutline; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                                        onAccepted: root.submitWifiPassword()
                                    }
                                    Text { anchors.left: parent.left; anchors.leftMargin: 9; anchors.verticalCenter: parent.verticalCenter; visible: !wifiPasswordInput.text.length; text: "Palavra-passe"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize }
                                }
                                Row {
                                    spacing: 14
                                    Text { text: "Cancelar"; color: cancelWifiMouse.containsMouse ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; BounceMouseArea { id: cancelWifiMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.cancelWifiPassword() } }
                                    Text { text: wifiCredentialProcess.running ? "A ligar…" : (root.wifiSelectedSsid === root.hostState.network_name ? "Já ligada" : "Ligar"); color: connectWifiMouse.containsMouse ? "#ffffff" : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal; BounceMouseArea { id: connectWifiMouse; anchors.fill: parent; enabled: root.wifiSelectedSsid !== root.hostState.network_name; hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor; onClicked: root.submitWifiPassword() } }
                                }
                            }
                        }
                        Text { visible: root.wifiMessage.length > 0; width: parent.width; wrapMode: Text.Wrap; text: root.wifiMessage; color: root.wifiMessage.indexOf("Não") === 0 ? "#ff91a4" : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize }
                        Repeater {
                            model: root.hostState.available_networks || []
                            Rectangle {
                                required property string modelData
                                visible: modelData !== root.hostState.network_name
                                      && (!root.wifiPasswordVisible || modelData !== root.wifiSelectedSsid)
                                width: parent ? parent.width : 300; height: visible ? 40 : 0; radius: 10
                                color: nearbyWifiMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                                border.width: nearbyWifiMouse.containsMouse ? 1 : 0; border.color: root.controlButtonOutline
                                Text {
                                    anchors.left: parent.left; anchors.leftMargin: 12; anchors.top: parent.top; anchors.topMargin: 6
                                    width: parent.width - 145; elide: Text.ElideRight
                                    text: modelData; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                                }
                                Text {
                                    anchors.left: parent.left; anchors.leftMargin: 12; anchors.bottom: parent.bottom; anchors.bottomMargin: 5
                                    text: root.wifiDetails(modelData).signal + "%  ·  " + root.wifiSecurityLabel(modelData)
                                    color: root.textDim
                                    font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal
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
                        Text {
                            visible: !(root.hostState.available_networks || []).length
                            text: "-- nenhuma rede encontrada --"
                            color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                        }
                    }

                    Rectangle {
                        visible: root.controlsBluetoothOpen
                        width: parent.width; height: visible ? 44 : 0; radius: 11
                        color: root.controlButtonSurface
                        border.width: 1; border.color: root.controlButtonOutline
                        Rectangle {
                            anchors.left: parent.left; anchors.leftMargin: 8; anchors.verticalCenter: parent.verticalCenter
                            width: 62; height: 28; radius: 8
                            color: bluetoothHeaderMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            Text { anchors.centerIn: parent; z: 2; text: "‹ Voltar"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                            BounceMouseArea { id: bluetoothHeaderMouse; anchors.fill: parent; z: 1; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.openControlSection("bluetooth") }
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter; anchors.verticalCenter: parent.verticalCenter
                            text: "Bluetooth"
                            color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                        }
                        Text {
                            anchors.right: parent.right; anchors.rightMargin: 11; anchors.verticalCenter: parent.verticalCenter
                            text: root.bluetoothPowerPhase === "turning-on" ? "A ligar…" : (root.bluetoothDisplayPowered() ? "Ligado" : "Desligado")
                            color: root.bluetoothDisplayPowered() ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize
                        }
                    }
                    Flickable {
                        visible: root.controlsBluetoothOpen
                        width: parent.width; height: visible ? 216 : 0
                        contentWidth: width; contentHeight: bluetoothContent.implicitHeight
                        clip: true; boundsBehavior: Flickable.StopAtBounds
                        ScrollBar.vertical: ScrollBar { policy: bluetoothContent.implicitHeight > 216 ? ScrollBar.AsNeeded : ScrollBar.AlwaysOff }

                        Column {
                            id: bluetoothContent
                            width: parent.width - (implicitHeight > 216 ? 7 : 0); spacing: 5

                            Rectangle {
                                width: parent.width; height: 56; radius: 11
                                color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                                Text {
                                    anchors.left: parent.left; anchors.leftMargin: 14; anchors.top: parent.top; anchors.topMargin: 8
                                    text: root.bluetoothPowerPhase === "turning-on" ? "A ligar Bluetooth…" : (root.bluetoothDisplayPowered() ? "Bluetooth ativo" : "Bluetooth desligado")
                                    color: root.bluetoothDisplayPowered() ? root.textMain : root.textDim
                                    font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                                }
                                Text {
                                    anchors.left: parent.left; anchors.leftMargin: 14; anchors.bottom: parent.bottom; anchors.bottomMargin: 8
                                    text: root.bluetoothConnectedDevices().length + " ligado" + (root.bluetoothConnectedDevices().length === 1 ? "" : "s")
                                    color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal
                                }
                                Rectangle {
                                    anchors.right: parent.right; anchors.rightMargin: 9; anchors.verticalCenter: parent.verticalCenter
                                    width: 84; height: 28; radius: 8
                                    color: bluetoothPowerMouse.containsMouse ? (root.bluetoothDisplayPowered() ? "#743541" : root.controlButtonHover) : root.controlButtonSurface
                                    border.width: root.bluetoothDisplayPowered() ? 0 : 1; border.color: root.controlButtonOutline
                                    Text { anchors.centerIn: parent; text: root.bluetoothPowerPhase === "turning-on" ? "A ligar…" : (root.bluetoothDisplayPowered() ? "Desligar" : "Ligar"); color: root.bluetoothDisplayPowered() ? "#ffb0bd" : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                                    BounceMouseArea { id: bluetoothPowerMouse; anchors.fill: parent; enabled: !root.bluetoothPowerPhase.length; hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor; onClicked: root.toggleBluetoothPower() }
                                }
                            }

                            Rectangle {
                                visible: root.bluetoothDisplayPowered()
                                width: parent.width; height: visible ? 30 : 0; radius: 8
                                color: bluetoothScanMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                                border.width: 1; border.color: root.controlButtonOutline
                                Text { anchors.centerIn: parent; text: bluetoothScanProcess.running ? "A procurar…" : "Procurar dispositivos"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                                BounceMouseArea { id: bluetoothScanMouse; anchors.fill: parent; enabled: !bluetoothScanProcess.running; hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor; onClicked: bluetoothScanProcess.running = true }
                            }

                            Rectangle {
                                visible: root.bluetoothPairSessionId.length > 0
                                width: parent.width
                                height: visible ? (root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "pin" ? 108 : 78) : 0
                                radius: 10; color: root.controlButtonActive; border.width: 1; border.color: root.controlButtonOutline
                                Column {
                                    anchors.fill: parent; anchors.margins: 9; spacing: 5
                                    Text { width: parent.width; elide: Text.ElideRight; text: "Emparelhar " + root.bluetoothPairName; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                    Text {
                                        width: parent.width; wrapMode: Text.Wrap
                                        text: root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "confirm"
                                              ? "Confirma que o código " + (root.bluetoothPairPasskey || "------") + " coincide."
                                              : (root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "pin"
                                                 ? "Introduz o PIN apresentado pelo dispositivo."
                                                 : (root.bluetoothPairPhase === "waiting-device"
                                                    ? "Escreve no dispositivo o código " + (root.bluetoothPairPasskey || "------") + "."
                                                    : (root.bluetoothMessage || "A aguardar o dispositivo…")))
                                        color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize
                                    }
                                    Rectangle {
                                        visible: root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "pin"
                                        width: parent.width; height: visible ? 28 : 0; radius: 5; color: root.controlButtonSurface; border.width: bluetoothPinInput.activeFocus ? 1 : 0; border.color: root.cyan
                                        TextInput {
                                            id: bluetoothPinInput; anchors.fill: parent; anchors.leftMargin: 9; anchors.rightMargin: 9; verticalAlignment: TextInput.AlignVCenter
                                            activeFocusOnTab: true
                                            text: root.bluetoothPairPin; onTextChanged: root.bluetoothPairPin = text; echoMode: TextInput.Password; maximumLength: 16
                                            color: root.textMain; selectionColor: root.controlButtonOutline; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                                            onAccepted: if (text.length) root.respondBluetoothPair(true, text)
                                        }
                                        Text { anchors.left: parent.left; anchors.leftMargin: 9; anchors.verticalCenter: parent.verticalCenter; visible: !bluetoothPinInput.text.length; text: "Pin"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize }
                                    }
                                    Row {
                                        spacing: 12
                                        Text { text: root.bluetoothPairPhase === "completed" || root.bluetoothPairPhase === "failed" ? "Fechar" : "Cancelar"; color: pairCancelMouse.containsMouse ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; BounceMouseArea { id: pairCancelMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.bluetoothPairPhase === "completed" || root.bluetoothPairPhase === "failed" ? root.dismissBluetoothPairing() : root.cancelBluetoothPairing() } }
                                        Text { visible: root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "confirm"; text: "Confirmar"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal; BounceMouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.respondBluetoothPair(true, "") } }
                                        Text { visible: root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "pin"; text: "Emparelhar"; color: root.bluetoothPairPin.length ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal; BounceMouseArea { anchors.fill: parent; enabled: root.bluetoothPairPin.length > 0; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor; onClicked: root.respondBluetoothPair(true, root.bluetoothPairPin) } }
                                    }
                                }
                            }

                            Rectangle {
                                visible: root.bluetoothRemoveAddress.length > 0
                                width: parent.width; height: visible ? 58 : 0; radius: 10
                                color: "#2b2026"; border.width: 1; border.color: "#743541"
                                Text { anchors.left: parent.left; anchors.leftMargin: 10; anchors.top: parent.top; anchors.topMargin: 8; width: parent.width - 20; elide: Text.ElideRight; text: "Esquecer " + root.bluetoothRemoveName + "?"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                                Row {
                                    anchors.left: parent.left; anchors.leftMargin: 10; anchors.bottom: parent.bottom; anchors.bottomMargin: 8; spacing: 14
                                    Text { text: "Cancelar"; color: removeCancelMouse.containsMouse ? root.textMain : root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; BounceMouseArea { id: removeCancelMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: { root.bluetoothRemoveAddress = ""; root.bluetoothRemoveName = "" } } }
                                    Text { text: bluetoothRemoveProcess.running ? "A esquecer…" : "Confirmar"; color: "#ffb0bd"; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal; BounceMouseArea { anchors.fill: parent; enabled: !bluetoothRemoveProcess.running; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor; onClicked: root.confirmBluetoothRemove() } }
                                }
                            }

                            Text { visible: root.bluetoothMessage.length > 0 && root.bluetoothPairSessionId.length === 0; width: parent.width; wrapMode: Text.Wrap; text: root.bluetoothMessage; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize }

                            Item { width: parent.width; height: 18; Text { anchors.verticalCenter: parent.verticalCenter; text: "Dispositivos ligados  ·  " + root.bluetoothConnectedDevices().length; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal } }
                            Repeater {
                                model: root.bluetoothConnectedDevices()
                                Rectangle {
                                    required property var modelData
                                    width: parent ? parent.width : 300; height: 36; radius: 10
                                    color: connectedBtMouse.containsMouse ? root.controlButtonHover : root.controlButtonActive; border.width: 1; border.color: root.controlButtonOutline
                                    Rectangle { width: 8; height: 8; radius: 4; color: root.textMain; anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter }
                                    Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.verticalCenter: parent.verticalCenter; width: parent.width - 130; elide: Text.ElideRight; text: modelData.name || modelData.address; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                                    Text { anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; text: "Desligar"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal }
                                    BounceMouseArea { id: connectedBtMouse; anchors.fill: parent; enabled: !root.bluetoothDevicePendingAddress.length; hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor; onClicked: root.bluetoothDeviceAction("bluetooth-disconnect", modelData) }
                                }
                            }
                            Text { visible: root.bluetoothConnectedDevices().length === 0; text: "-- nenhum dispositivo ligado --"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize }

                            Item { width: parent.width; height: 4 }
                            Item { width: parent.width; height: 18; Text { anchors.verticalCenter: parent.verticalCenter; text: "Dispositivos anteriores  ·  " + root.bluetoothKnownDevices().length; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal } }
                            Repeater {
                                model: root.bluetoothKnownDevices()
                                Rectangle {
                                    required property var modelData
                                    width: parent ? parent.width : 300; height: 36; radius: 10; color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                                    Rectangle { width: 8; height: 8; radius: 4; color: "#405058"; anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter }
                                    Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.verticalCenter: parent.verticalCenter; width: parent.width - 148; elide: Text.ElideRight; text: modelData.name || modelData.address; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                                    Row {
                                        anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter; spacing: 4
                                        Rectangle {
                                            width: root.bluetoothDevicePendingAction === "bluetooth-connect" && root.bluetoothDevicePendingAddress === modelData.address ? 58 : 38
                                            height: 24; radius: 6; color: knownConnectMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                                            Text {
                                                anchors.centerIn: parent
                                                text: root.bluetoothDevicePendingAction === "bluetooth-connect" && root.bluetoothDevicePendingAddress === modelData.address ? "A ligar…" : "Ligar"
                                                color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal
                                                SequentialAnimation on opacity {
                                                    running: root.bluetoothDevicePendingAction === "bluetooth-connect" && root.bluetoothDevicePendingAddress === modelData.address
                                                    loops: Animation.Infinite
                                                    NumberAnimation { to: 0.35; duration: 380 }
                                                    NumberAnimation { to: 1; duration: 380 }
                                                }
                                            }
                                            BounceMouseArea { id: knownConnectMouse; anchors.fill: parent; enabled: !root.bluetoothDevicePendingAddress.length; hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor; onClicked: root.bluetoothDeviceAction("bluetooth-connect", modelData) }
                                        }
                                        Rectangle { width: 52; height: 24; radius: 6; color: knownRemoveMouse.containsMouse ? "#59303a" : root.controlButtonSurface; Text { anchors.centerIn: parent; text: "Esquecer"; color: "#ffb0bd"; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal } BounceMouseArea { id: knownRemoveMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.beginBluetoothRemove(modelData) } }
                                    }
                                }
                            }
                            Text { visible: root.bluetoothKnownDevices().length === 0; text: "-- nenhum dispositivo anterior --"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize }

                            Item { width: parent.width; height: 4 }
                            Item { width: parent.width; height: 18; Text { anchors.verticalCenter: parent.verticalCenter; text: "Dispositivos disponíveis  ·  " + root.bluetoothAvailableDevices().length; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal } }
                            Repeater {
                                model: root.bluetoothAvailableDevices()
                                Rectangle {
                                    required property var modelData
                                    width: parent ? parent.width : 300; height: 36; radius: 10; color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                                    Text { anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter; width: parent.width - 104; elide: Text.ElideRight; text: modelData.name || modelData.address; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                                    Rectangle { anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter; width: 78; height: 24; radius: 6; color: availablePairMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface; Text { anchors.centerIn: parent; text: "Emparelhar"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal } BounceMouseArea { id: availablePairMouse; anchors.fill: parent; enabled: !root.bluetoothPairSessionId.length; hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor; onClicked: root.beginBluetoothPair(modelData) } }
                                }
                            }
                            Text { visible: root.bluetoothAvailableDevices().length === 0; width: parent.width; wrapMode: Text.Wrap; text: root.hostState.bluetooth_powered ? (bluetoothScanProcess.running ? "-- a procurar dispositivos --" : "-- nenhum dispositivo disponível --") : "-- liga o Bluetooth para procurar dispositivos --"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuSmallSize }
                        }
                    }

                    Row {
                        visible: root.controlsAllClosed() && !root.powerConfirmOpen
                        width: parent.width; height: visible ? 58 : 0; spacing: 6
                        Rectangle {
                            width: parent.width - 90; height: parent.height; radius: 11
                            color: volumeSummaryMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            border.width: 1; border.color: root.controlButtonOutline
                            Text { anchors.left: parent.left; anchors.leftMargin: 12; anchors.top: parent.top; anchors.topMargin: 12; text: "Volume"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            Text {
                                anchors.right: parent.right; anchors.rightMargin: 12
                                anchors.top: parent.top; anchors.topMargin: 12
                                text: (root.volumeMuted ? 0 : Math.round(root.volumeValue)) + "%"
                                color: root.volumeMuted ? root.textDim : root.textMain
                                font.family: "Selawik"; font.pixelSize: root.menuBodySize
                                font.weight: Font.Normal
                            }
                            MenuSlider {
                                id: volumeSummarySlider
                                onKeyboardValueChanged: (nextValue) => root.commitVolume(nextValue)
                                anchors.left: parent.left; anchors.leftMargin: 12; anchors.right: parent.right; anchors.rightMargin: 12
                                anchors.bottom: parent.bottom; anchors.bottomMargin: 3
                                height: 22; from: 0; to: 100; stepSize: 1; enabled: !localActionProcess.running
                                onMoved: root.previewVolume(value)
                                onPressedChanged: { if (!pressed) root.commitVolume(value) }
                                Binding { target: volumeSummarySlider; property: "value"; value: root.volumeMuted ? 0 : root.volumeValue; when: !volumeSummarySlider.pressed }
                                background: Rectangle {
                                    x: volumeSummarySlider.leftPadding; y: volumeSummarySlider.topPadding + volumeSummarySlider.availableHeight / 2 - height / 2
                                    width: volumeSummarySlider.availableWidth; height: 3; radius: 2; color: volumeSummarySlider.keyboardEditing ? Qt.darker(root.cyan, 2.5) : "#34454e"
                                    Rectangle { width: volumeSummarySlider.visualPosition * parent.width; height: parent.height; radius: 2; color: volumeSummarySlider.keyboardEditing ? root.cyan : (root.volumeMuted ? root.textDim : root.textMain) }
                                }
                                handle: Rectangle {
                                    x: volumeSummarySlider.leftPadding + volumeSummarySlider.visualPosition * (volumeSummarySlider.availableWidth - width)
                                    y: volumeSummarySlider.topPadding + volumeSummarySlider.availableHeight / 2 - height / 2
                                    width: volumeSummarySlider.pressed ? 12 : 10; height: width; radius: width / 2; color: volumeSummarySlider.keyboardEditing ? root.cyan : (volumeSummarySlider.pressed ? "#ffffff" : root.textMain); border.width: 2; border.color: root.controlButtonSurface
                                }
                            }
                            BounceMouseArea { id: volumeSummaryMouse; activeFocusOnTab: false; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; z: 1; height: 36; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.openControlSection("audio") }
                        }
                        Rectangle {
                            width: 84; height: parent.height; radius: 11
                            property int microphoneState: root.microphoneText === "--" ? -1 : (root.microphoneMuted ? 0 : (root.microphoneActive ? 2 : 1))
                            property color stateSurface: microphoneState <= 0 ? root.controlButtonSurface : (microphoneState === 1 ? "#3b4850" : "#b8d8dc")
                            color: microphoneSummaryMouse.containsMouse ? Qt.lighter(stateSurface, 1.12) : stateSurface
                            border.width: 1; border.color: root.controlButtonOutline
                            Behavior on color { ColorAnimation { duration: 140 } }
                            Text {
                                anchors.centerIn: parent
                                width: parent.width - 8; horizontalAlignment: Text.AlignHCenter
                                text: "Microfone"
                                color: parent.microphoneState === 2 ? "#172126" : root.textMain
                                font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                            }
                            BounceMouseArea { id: microphoneSummaryMouse; anchors.fill: parent; z: 1; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.openControlSection("microphone") }
                        }
                    }
                    Row {
                        visible: root.controlsAllClosed() && !root.powerConfirmOpen
                        width: parent.width; height: visible ? 58 : 0; spacing: 6
                        Rectangle {
                            width: parent.width - 90; height: parent.height; radius: 11
                            color: root.controlButtonSurface
                            border.width: 1; border.color: root.controlButtonOutline
                            Text {
                                anchors.left: parent.left; anchors.leftMargin: 12; anchors.top: parent.top; anchors.topMargin: 12
                                text: "Brilho do ecrã"; color: root.textMain; font.family: "Selawik"
                                font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                            }
                            Text {
                                anchors.right: parent.right; anchors.rightMargin: 12; anchors.top: parent.top; anchors.topMargin: 12
                                text: root.displayBrightness + "%"; color: root.textMain; font.family: "Selawik"
                                font.pixelSize: root.menuSmallSize; font.weight: Font.Normal
                            }
                            MenuSlider {
                                id: displayBrightnessSlider
                                onKeyboardValueChanged: (nextValue) => root.commitDisplayBrightness(nextValue)
                                anchors.left: parent.left; anchors.leftMargin: 12
                                anchors.right: parent.right; anchors.rightMargin: 12
                                anchors.bottom: parent.bottom; anchors.bottomMargin: 3
                                height: 22; from: 5; to: 100; stepSize: 1
                                onMoved: root.previewDisplayBrightness(value)
                                onPressedChanged: { if (!pressed) root.commitDisplayBrightness(value) }
                                Binding { target: displayBrightnessSlider; property: "value"; value: root.displayBrightness; when: !displayBrightnessSlider.pressed }
                                background: Rectangle {
                                    x: displayBrightnessSlider.leftPadding
                                    y: displayBrightnessSlider.topPadding + displayBrightnessSlider.availableHeight / 2 - height / 2
                                    width: displayBrightnessSlider.availableWidth; height: 3; radius: 2; color: displayBrightnessSlider.keyboardEditing ? Qt.darker(root.cyan, 2.5) : "#34454e"
                                    Rectangle { width: displayBrightnessSlider.visualPosition * parent.width; height: parent.height; radius: 2; color: displayBrightnessSlider.keyboardEditing ? root.cyan : (root.textMain) }
                                }
                                handle: Rectangle {
                                    x: displayBrightnessSlider.leftPadding + displayBrightnessSlider.visualPosition * (displayBrightnessSlider.availableWidth - width)
                                    y: displayBrightnessSlider.topPadding + displayBrightnessSlider.availableHeight / 2 - height / 2
                                    width: displayBrightnessSlider.pressed ? 12 : 10; height: width; radius: width / 2
                                    color: displayBrightnessSlider.keyboardEditing ? root.cyan : (displayBrightnessSlider.pressed ? "#ffffff" : root.textMain); border.width: 2; border.color: root.controlButtonSurface
                                }
                            }
                        }
                        Rectangle {
                            width: 84; height: parent.height; radius: 11
                            property int lightState: root.keyboardBrightness <= 0 ? 0 : (root.keyboardBrightness >= root.keyboardBrightnessMax ? 2 : 1)
                            property color stateSurface: lightState === 0 ? root.controlButtonSurface : (lightState === 1 ? "#3b4850" : "#b8d8dc")
                            color: keyboardBrightnessSummaryMouse.containsMouse ? Qt.lighter(stateSurface, 1.12) : stateSurface
                            border.width: 1
                            border.color: root.controlButtonOutline
                            Behavior on color { ColorAnimation { duration: 140 } }
                            Text {
                                anchors.centerIn: parent
                                width: parent.width - 8; horizontalAlignment: Text.AlignHCenter
                                text: "Teclado"; color: parent.lightState === 2 ? "#172126" : root.textMain
                                font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                            }
                            BounceMouseArea {
                                id: keyboardBrightnessSummaryMouse
                                anchors.fill: parent; enabled: !keyboardBrightnessProcess.running
                                hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                                onClicked: root.cycleKeyboardBrightness()
                            }
                        }
                    }
                    Column {
                        visible: root.controlsAllClosed() && root.hasExternalDisplay
                        width: parent.width
                        spacing: 6
                        Text {
                            text: "Posição do monitor externo"
                            color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                        }
                        Row {
                            width: parent.width; spacing: 6
                            MenuButton {
                                width: (parent.width - 6) / 2; label: "À esquerda"
                                enabled: !displayLayoutProcess.running
                                onActivated: root.setDisplayLayout("left")
                                SelectionIndicator { visible: root.displayLayoutSide === "left" }
                            }
                            MenuButton {
                                width: (parent.width - 6) / 2; label: "À direita"
                                enabled: !displayLayoutProcess.running
                                onActivated: root.setDisplayLayout("right")
                                SelectionIndicator { visible: root.displayLayoutSide === "right" }
                            }
                        }
                        Text {
                            width: parent.width; wrapMode: Text.WordWrap
                            text: "Super+Ctrl+Home traz o ponteiro para o portátil."
                            color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize
                        }
                    }
                    Text {
                        visible: root.controlsAllClosed() && root.hasExternalDisplay && root.displayLayoutError.length > 0
                        width: parent.width; text: root.displayLayoutError; color: "#ff91a4"
                        wrapMode: Text.WordWrap; font.family: "Selawik"; font.pixelSize: root.menuMetaSize
                    }
                    Text {
                        visible: root.controlsAllClosed() && root.hardwareControlError.length > 0
                        width: parent.width; text: root.hardwareControlError; color: "#ff91a4"
                        wrapMode: Text.WordWrap; font.family: "Selawik"; font.pixelSize: root.menuMetaSize
                    }
                    Rectangle {
                        visible: root.controlsAudioOpen
                        width: parent.width; height: visible ? 44 : 0; radius: 11
                        color: root.controlButtonSurface
                        border.width: 1; border.color: root.controlButtonOutline
                        Rectangle {
                            anchors.left: parent.left; anchors.leftMargin: 8; anchors.verticalCenter: parent.verticalCenter
                            width: 62; height: 28; radius: 8
                            color: audioHeaderMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            Text { anchors.centerIn: parent; text: "‹ Voltar"; color: audioHeaderMouse.containsMouse ? "#ffffff" : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                            BounceMouseArea { id: audioHeaderMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.openControlSection("audio") }
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter; anchors.verticalCenter: parent.verticalCenter
                            text: "Volume"
                            color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                        }
                        Text {
                            anchors.right: parent.right; anchors.rightMargin: 11; anchors.verticalCenter: parent.verticalCenter
                            text: root.volumeText
                            color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuMetaSize
                        }
                    }
                    Column {
                        width: parent.width; spacing: 5; visible: root.controlsAudioOpen

                        Rectangle {
                            width: parent.width; height: 68; radius: 11
                            color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                            Text {
                                anchors.left: parent.left; anchors.leftMargin: 16; anchors.top: parent.top; anchors.topMargin: 8
                                text: root.volumeMuted ? "Volume silenciado" : "Volume de saída"
                                color: root.volumeMuted ? root.textDim : root.textMain
                                font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
                            }
                            Text {
                                anchors.right: parent.right; anchors.rightMargin: 12; anchors.top: parent.top; anchors.topMargin: 8
                                text: Math.round(volumeSlider.value) + "%"
                                color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal
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
                                handle: Rectangle {
                                    x: volumeSlider.leftPadding + volumeSlider.visualPosition * (volumeSlider.availableWidth - width)
                                    y: volumeSlider.topPadding + volumeSlider.availableHeight / 2 - height / 2
                                    width: 16; height: 16; radius: 8
                                    color: volumeSlider.keyboardEditing ? root.cyan : (volumeSlider.pressed ? "#ffffff" : root.textMain)
                                    border.width: 2; border.color: root.controlButtonSurface
                                }
                            }
                        }

                        Row {
                            width: parent.width; height: 30; spacing: 4
                            MenuButton {
                                width: (parent.width - 6) / 2; height: parent.height; label: "Ajuste −5%"
                                onActivated: root.localAction(["/usr/bin/wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"])
                            }
                            MenuButton {
                                width: (parent.width - 6) / 2; height: parent.height; label: "Ajuste +5%"
                                onActivated: root.localAction(["/usr/bin/wpctl", "set-volume", "-l", "1", "@DEFAULT_AUDIO_SINK@", "5%+"])
                            }
                        }
                        Rectangle {
                            width: parent.width; height: 30; radius: 7
                            color: volumeMuteMouse.containsMouse ? root.controlButtonHover : (root.volumeMuted ? root.controlButtonActive : root.controlButtonSurface)
                            SelectionIndicator { visible: root.volumeMuted }
                            border.width: root.volumeMuted ? 1 : 0; border.color: root.controlButtonOutline
                            Text { anchors.centerIn: parent; text: root.volumeMuted ? "Reativar som" : "Silenciar"; color: root.volumeMuted ? root.textMain : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            BounceMouseArea { id: volumeMuteMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.toggleVolumeMute() }
                        }
                    }

                    Rectangle {
                        visible: root.controlsMicrophoneOpen
                        width: parent.width; height: visible ? 44 : 0; radius: 11
                        color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                        Rectangle {
                            anchors.left: parent.left; anchors.leftMargin: 8; anchors.verticalCenter: parent.verticalCenter
                            width: 62; height: 28; radius: 8
                            color: microphoneHeaderMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            Text { anchors.centerIn: parent; text: "‹ Voltar"; color: microphoneHeaderMouse.containsMouse ? "#ffffff" : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuSmallSize; font.weight: Font.Normal }
                            BounceMouseArea { id: microphoneHeaderMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.openControlSection("microphone") }
                        }
                        Text { anchors.horizontalCenter: parent.horizontalCenter; anchors.verticalCenter: parent.verticalCenter; text: "Microfone"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                        Text { anchors.right: parent.right; anchors.rightMargin: 11; anchors.verticalCenter: parent.verticalCenter; text: root.microphoneText; color: root.microphoneMuted ? root.textDim : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuMetaSize }
                    }
                    Column {
                        width: parent.width; spacing: 5; visible: root.controlsMicrophoneOpen
                        Rectangle {
                            width: parent.width; height: 68; radius: 11
                            color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                            Text { anchors.left: parent.left; anchors.leftMargin: 16; anchors.top: parent.top; anchors.topMargin: 8; text: root.microphoneMuted ? "Microfone silenciado" : "Volume de entrada"; color: root.microphoneMuted ? root.textDim : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            Text { anchors.right: parent.right; anchors.rightMargin: 12; anchors.top: parent.top; anchors.topMargin: 8; text: Math.round(microphoneSlider.value) + "%"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
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
                                handle: Rectangle {
                                    x: microphoneSlider.leftPadding + microphoneSlider.visualPosition * (microphoneSlider.availableWidth - width)
                                    y: microphoneSlider.topPadding + microphoneSlider.availableHeight / 2 - height / 2
                                    width: 16; height: 16; radius: 8; color: microphoneSlider.keyboardEditing ? root.cyan : (microphoneSlider.pressed ? "#ffffff" : root.textMain); border.width: 2; border.color: root.controlButtonSurface
                                }
                            }
                        }
                        Row {
                            width: parent.width; height: 30; spacing: 4
                            MenuButton { width: (parent.width - 6) / 2; height: parent.height; label: "Ajuste −5%"; onActivated: root.localAction(["/usr/bin/wpctl", "set-volume", "@DEFAULT_AUDIO_SOURCE@", "5%-"]) }
                            MenuButton { width: (parent.width - 6) / 2; height: parent.height; label: "Ajuste +5%"; onActivated: root.localAction(["/usr/bin/wpctl", "set-volume", "-l", "1", "@DEFAULT_AUDIO_SOURCE@", "5%+"]) }
                        }
                        Rectangle {
                            width: parent.width; height: 30; radius: 7
                            color: microphoneMuteMouse.containsMouse ? root.controlButtonHover : (root.microphoneMuted ? root.controlButtonActive : root.controlButtonSurface)
                            SelectionIndicator { visible: root.microphoneMuted }
                            border.width: root.microphoneMuted ? 1 : 0; border.color: root.controlButtonOutline
                            Text { anchors.centerIn: parent; text: root.microphoneMuted ? "Reativar microfone" : "Silenciar microfone"; color: root.microphoneMuted ? root.textMain : root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            BounceMouseArea { id: microphoneMuteMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.toggleMicrophoneMute() }
                        }
                    }

                    Row {
                        visible: root.isHub && root.controlsAllClosed() && !root.powerConfirmOpen
                        width: parent.width
                        height: visible ? 40 : 0
                        spacing: 6
                        Rectangle {
                            width: parent.width; height: parent.height; radius: 10
                            color: terminalMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            border.width: 1; border.color: root.controlButtonOutline
                            Text { anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter; text: "Terminal do Host"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            BounceMouseArea {
                                id: terminalMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    popup.open = false
                                    if (!hostConsoleProcess.running) hostConsoleProcess.running = true
                                }
                            }
                        }
                    }
                    Row {
                        visible: root.isHub && root.controlsAllClosed() && !root.powerConfirmOpen
                        width: parent.width
                        height: visible ? 40 : 0
                        spacing: 6
                        Rectangle {
                            width: parent.width; height: parent.height; radius: 10
                            color: environmentsControlMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            border.width: 1; border.color: root.controlButtonOutline
                            Text { anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter; text: "Sair para o Host"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            BounceMouseArea {
                                id: environmentsControlMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                onClicked: { popup.open = false; if (!hostExitProcess.running) hostExitProcess.running = true }
                            }
                        }
                    }
                    Item {
                        visible: root.controlsAllClosed() && !root.powerConfirmOpen
                        width: parent.width; height: visible ? 9 : 0
                    }
                    Text {
                        visible: root.controlsAllClosed() && !root.powerConfirmOpen
                        width: parent.width; height: 18
                        text: "Ações da sessão"
                        color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuMetaSize; font.weight: Font.Normal
                    }
                    Grid {
                        visible: root.controlsAllClosed() && !root.powerConfirmOpen
                        width: parent.width
                        height: visible ? 85 : 0
                        columns: 2
                        rowSpacing: 5
                        columnSpacing: 5
                        Rectangle {
                            width: (parent.width - 5) / 2; height: 40; radius: 10
                            color: lockMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            border.width: 1; border.color: root.controlButtonOutline
                            Text { anchors.centerIn: parent; text: "Bloquear"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            BounceMouseArea { id: lockMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: {
                                popup.open = false
                                if (!lockProcess.running) lockProcess.running = true
                            } }
                        }
                        Rectangle {
                            width: (parent.width - 5) / 2; height: 40; radius: 10
                            color: rebootMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            border.width: 1; border.color: root.controlButtonOutline
                            Text { anchors.centerIn: parent; text: root.isHub ? "Reiniciar" : "Ficheiros"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            BounceMouseArea {
                                id: rebootMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (root.isHub)
                                        root.beginPower("reboot")
                                    else
                                        environmentFilesProcess.running = true
                                }
                            }
                        }
                        Rectangle {
                            width: (parent.width - 5) / 2; height: 40; radius: 10
                            color: updateMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
                            border.width: 1; border.color: root.controlButtonOutline
                            Text { anchors.centerIn: parent; text: "Atualizar"; color: root.textMain; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            BounceMouseArea { id: updateMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: {
                                popup.open = false
                                if (!updateUiProcess.running) updateUiProcess.running = true
                            } }
                        }
                        Rectangle {
                            width: (parent.width - 5) / 2; height: 40; radius: 10
                            color: poweroffMouse.containsMouse ? "#422a31" : root.controlButtonSurface
                            border.width: 1; border.color: "#71414b"
                            Text { anchors.centerIn: parent; text: "Encerrar"; color: "#ff9dab"; font.family: "Selawik"; font.pixelSize: root.menuBodySize; font.weight: Font.Normal }
                            BounceMouseArea {
                                id: poweroffMouse
                                anchors.fill: parent
                                enabled: root.isHub || (root.sessionKindReady && !root.environmentSwitchPending)
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    root.beginPower("poweroff")
                                }
                            }
                        }
                    }
                    Rectangle {
                        visible: root.controlsAllClosed() && root.powerConfirmOpen
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
                            Text {
                                width: parent.width
                                text: root.powerMessage
                                color: root.powerToken.length ? "#ffd09a" : root.textDim
                                font.family: "Selawik"
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
                    width: parent.width
                    spacing: 6
                    visible: root.popupKind === "wifi"
                    Text {
                        text: "Status :: " + (root.hostState.network_name || "disconnected")
                        color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                    }
                    MenuButton { label: "[ SCAN ] procurar redes"; onActivated: root.hostAction("wifi-scan") }
                    MenuButton {
                        visible: !!root.hostState.network_name
                        label: "[ DISCONNECT ] rede atual"
                        onActivated: root.hostAction("wifi-disconnect")
                    }
                    Text { text: "Known networks"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
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
                    Text { text: "Paired devices"; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                    Repeater {
                        model: root.hostState.bluetooth_devices || []
                        MenuButton {
                            required property var modelData
                            label: "[ " + (modelData.connected ? "Disconnect" : "Connect") + " ] " + modelData.name
                            onActivated: root.hostAction(modelData.connected ? "bluetooth-disconnect" : "bluetooth-connect", modelData.address)
                        }
                    }
                    Text {
                        visible: !(root.hostState.bluetooth_devices || []).length
                        text: "-- nenhum dispositivo emparelhado --"
                        color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize
                    }
                }

                    Column {
                    width: parent.width
                    spacing: 6
                    visible: root.popupKind === "audio"
                    Text { text: "Output :: " + root.volumeText; color: root.textDim; font.family: "Selawik"; font.pixelSize: root.menuBodySize }
                    MenuButton { label: "[ + 5% ] aumentar volume"; accent: true; onActivated: root.localAction(["/usr/bin/wpctl", "set-volume", "-l", "1", "@DEFAULT_AUDIO_SINK@", "5%+"]) }
                    MenuButton { label: "[ - 5% ] diminuir volume"; onActivated: root.localAction(["/usr/bin/wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"]) }
                    MenuButton { label: "[ MUTE ] alternar som"; onActivated: root.localAction(["/usr/bin/wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"]) }
                }

                    Column {
                    width: parent.width
                    spacing: 12
                    visible: root.popupKind === "battery"
                    Rectangle {
                        width: parent.width; height: 110; radius: 11; color: root.controlButtonSurface
                        Text { id: batteryCapacity; x: 14; y: 10; text: root.batteryText; color: root.textMain; font.family: "Selawik"; font.pixelSize: 32; font.bold: true }
                        Text {
                            anchors.left: batteryCapacity.right; anchors.leftMargin: 16
                            anchors.right: parent.right; anchors.rightMargin: 14
                            y: 24; text: root.batteryStatus; elide: Text.ElideRight
                            color: root.textDim; font.family: "Selawik"; font.pixelSize: 11
                        }
                        Rectangle {
                            x: 14; y: 61; width: parent.width - 28; height: 6; radius: 3; color: root.controlButtonOutline
                            Rectangle { height: parent.height; radius: 3; color: parseInt(root.batteryText) <= 20 ? "#ffb15a" : "#9dc8bd"; width: parent.width * Math.max(0, Math.min(100, parseInt(root.batteryText) || 0)) / 100 }
                        }
                        Text {
                            x: 14; y: 82; width: parent.width - 28; elide: Text.ElideRight
                            text: root.batteryMinutes >= 0 ? "Estimativa · " + Math.floor(root.batteryMinutes / 60) + " h " + (root.batteryMinutes % 60) + " min" : "Autonomia indisponível"
                            color: root.textDim; font.family: "Selawik"; font.pixelSize: 11
                        }
                    }
                    Text {
                        visible: root.hardwareStatusError.length > 0
                        width: parent.width; wrapMode: Text.WordWrap
                        text: "Controlos de energia indisponíveis. " + root.hardwareStatusError
                        color: "#ff91a4"; font.family: "Selawik"; font.pixelSize: 11
                    }
                    Text {
                        visible: true
                        text: "Modo de energia · " + root.platformLabel(root.hardwareProfile.platform_profile)
                        color: root.textDim; font.family: "Selawik"; font.pixelSize: 11
                    }
                    Text {
                        visible: root.batteryDischarging
                        width: parent.width
                        wrapMode: Text.WordWrap
                        text: "Liga o carregador para usar o modo Desempenho do portátil."
                        color: root.textDim
                        font.family: "Selawik"
                        font.pixelSize: root.menuSmallSize
                    }
                    Row {
                        id: energyModeRow
                        visible: true
                        width: parent.width; spacing: 6
                        Repeater {
                            model: [
                                { profile: "low-power", label: "Poupar" },
                                { profile: "balanced", label: "Equilibrado" },
                                { profile: "performance", label: "Desempenho" }
                            ]
                            MenuButton {
                                required property var modelData
                                width: (energyModeRow.width - 12) / 3; height: 42
                                label: modelData.label
                                accent: root.hardwareProfile.platform_profile === modelData.profile
                                selected: accent
                                enabled: !root.hardwareBusy && (root.hardwareProfile.platform_profiles || []).indexOf(modelData.profile) >= 0
                                onActivated: root.setPlatformProfile(modelData.profile)
                            }
                        }
                    }
                    Text {
                        visible: root.hardwareMessage.length > 0 && !root.hardwareConfirmOpen
                        text: root.hardwareMessage; color: root.platformProfileError.length ? "#ff91a4" : root.textDim; wrapMode: Text.WordWrap
                        width: parent.width; font.family: "Selawik"; font.pixelSize: 10
                    }
                    MenuButton {
                        label: root.batteryDetailsOpen ? "− Ocultar detalhes" : "+ Detalhes e gráficos"
                        height: 36
                        enabled: !root.hardwareConfirmOpen
                        onActivated: root.batteryDetailsOpen = !root.batteryDetailsOpen
                    }
                    Column {
                        width: parent.width; spacing: 12
                        visible: root.batteryDetailsOpen || root.hardwareConfirmOpen
                        Row {
                            width: parent.width; spacing: 8
                            Repeater {
                                model: [
                                    { title: "Potência", value: root.batteryWatts >= 0 ? root.batteryWatts.toFixed(1) + " W" : "—" },
                                    { title: "Saúde da bateria", value: root.batteryHealth >= 0 ? root.batteryHealth + "%" : "—" }
                                ]
                                Rectangle {
                                    required property var modelData
                                    width: (parent.width - 8) / 2; height: 48; radius: 9; color: root.controlButtonSurface
                                    Text { x: 10; y: 7; text: modelData.title; color: root.textDim; font.family: "Selawik"; font.pixelSize: 9 }
                                    Text { x: 10; y: 24; text: modelData.value; color: root.textMain; font.family: "Selawik"; font.pixelSize: 14 }
                                }
                            }
                        }
                        Rectangle { width: parent.width; height: 1; color: root.controlButtonOutline; visible: root.isHub }
                        Text {
                            visible: root.isHub
                            text: "Gráficos · " + root.gpuLabel(root.hardwareProfile.gpu_profile)
                                  + (root.hardwareProfile.reboot_required
                                     ? "  →  " + root.gpuLabel(root.hardwareProfile.requested_gpu_profile) + " (Reinício)" : "")
                            color: root.hardwareProfile.reboot_required ? "#ffd09a" : root.textDim
                            font.family: "Selawik"; font.pixelSize: 11
                            width: parent.width; wrapMode: Text.WordWrap
                        }
                        Column {
                            width: parent.width; spacing: 8
                            visible: root.isHub && !root.hardwareConfirmOpen
                            MenuButton {
                                height: 40; label: "Híbridos · NVIDIA sob pedido"
                                accent: root.hardwareProfile.requested_gpu_profile === "hybrid"
                                selected: accent
                                enabled: !root.hardwareBusy && (root.hardwareProfile.gpu_profiles || []).indexOf("hybrid") >= 0
                                onActivated: root.beginGpuProfile("hybrid")
                            }
                            MenuButton {
                                height: 40; label: "NVIDIA dedicada · maior consumo"
                                accent: root.hardwareProfile.requested_gpu_profile === "nvidia"
                                selected: accent
                                enabled: !root.hardwareBusy && (root.hardwareProfile.gpu_profiles || []).indexOf("nvidia") >= 0
                                onActivated: root.beginGpuProfile("nvidia")
                            }
                        }
                        Rectangle {
                            visible: root.isHub && root.hardwareConfirmOpen
                            width: parent.width; height: visible ? gpuConfirmationContent.implicitHeight + 24 : 0; radius: 7
                            color: root.controlButtonSurface; border.width: 1
                            border.color: root.hardwareApplied ? root.cyan : "#ffb15a"
                            Column {
                                id: gpuConfirmationContent
                                x: 12; y: 12; width: parent.width - 24; spacing: 12
                                Text {
                                    width: parent.width; text: root.hardwareMessage
                                    color: root.hardwareApplied ? root.textMain : "#ffd09a"
                                    font.family: "Selawik"; font.pixelSize: 10; font.bold: true
                                    wrapMode: Text.Wrap
                                }
                                Row {
                                    width: parent.width; spacing: 6
                                    MenuButton {
                                        width: (parent.width - 6) / 2
                                        label: root.hardwareApplied ? "Mais tarde" : "Cancelar"
                                        onActivated: root.cancelGpuProfile()
                                    }
                                    MenuButton {
                                        width: (parent.width - 6) / 2
                                        visible: root.hardwareApplied || root.hardwareToken.length > 0
                                        label: root.hardwareApplied ? "Reiniciar agora" : (root.hardwareBusy ? "A processar..." : "Confirmar")
                                        accent: true
                                        onActivated: root.hardwareApplied ? root.rebootForGpuProfile() : root.confirmGpuProfile()
                                    }
                                }
                            }
                        }
                        Text {
                            text: root.hardwareProfile.gpu_error ? "Controlos de gráficos indisponíveis. " + root.hardwareProfile.gpu_error : "A mudança de gráficos requer reinício."
                            color: root.textDim; wrapMode: Text.WordWrap; width: parent.width
                            font.family: "Selawik"; font.pixelSize: 9
                        }
                    }

                    }
                }
            }
        }
    }

}
