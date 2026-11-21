"""Closed desktop-feature catalogue for APX Environment creation."""

from __future__ import annotations

MODULES = (
    "system", "cli-aur", "graphical", "desktop-integration", "locale-input",
    "network", "bluetooth", "audio", "graphics", "power", "devices-storage",
    "files", "web-documents", "multimedia", "office", "communication",
    "printing-scanning", "development", "shortcuts", "iphone-integration",
    "minecraft", "steam", "hytale", "mail", "gaming-chat", "study-tools", "messaging", "minecraft-backups", "chatgpt",
)

DEPENDENCIES = {
    "system": (), "cli-aur": ("system",), "graphical": ("system",),
    "desktop-integration": ("graphical",), "locale-input": ("system",),
    "network": ("system",), "bluetooth": ("system",), "audio": ("system",),
    "graphics": ("graphical",), "power": ("graphical",),
    "devices-storage": ("system",),
    "files": ("desktop-integration", "devices-storage"),
    "web-documents": ("desktop-integration", "network"),
    "multimedia": ("desktop-integration", "audio", "graphics"),
    "office": ("desktop-integration", "locale-input"),
    "communication": ("desktop-integration", "network", "audio", "graphics"),
    "printing-scanning": ("desktop-integration", "network", "devices-storage"),
    "development": ("cli-aur",), "shortcuts": ("graphical",),
    "iphone-integration": ("desktop-integration", "network"),
    "minecraft": ("desktop-integration", "network", "audio", "graphics"),
    "steam": ("desktop-integration", "network", "audio", "graphics"),
    "hytale": ("desktop-integration", "network", "audio", "graphics"),
    "mail": ("desktop-integration", "network"),
    "gaming-chat": ("communication",),
    "study-tools": ("desktop-integration", "network"),
    "messaging": ("communication",),
    "minecraft-backups": ("desktop-integration",),
    "chatgpt": ("web-documents",),
}

OPTIONAL_MODULES = frozenset(("iphone-integration", "minecraft", "steam", "hytale", "mail",
                              "gaming-chat", "study-tools", "messaging", "minecraft-backups", "chatgpt"))

PRESETS = {
    "basic": ("system", "cli-aur"),
    "intermediate": tuple(module for module in MODULES if module not in OPTIONAL_MODULES | {"office", "development"}),
    "complete": tuple(module for module in MODULES if module not in OPTIONAL_MODULES),
}

# The admitted graphical release owns the open-source base. Its NVIDIA
# userspace must match the Host module and is supplied as a pinned local
# artifact during creation, even for a minimal graphical Environment.
PACKAGES = {
    "system": ("xfce4-taskmanager",),
    "graphics": ("egl-gbm", "egl-wayland", "egl-wayland2", "egl-x11"),
    "audio": ("pipewire-alsa", "pavucontrol"),
    "locale-input": ("noto-fonts-emoji", "ttf-liberation", "enchant", "otf-font-awesome"),
    "desktop-integration": ("cliphist", "man-pages", "qt5-wayland"),
    "files": (
        "7zip", "catfish", "ffmpegthumbnailer", "papirus-icon-theme",
        "poppler-glib", "rsync", "thunar-archive-plugin", "unrar", "unzip", "xarchiver", "zip",
    ),
    "web-documents": ("evince",),
    "multimedia": ("ffmpeg", "gst-libav", "gst-plugins-good", "gst-plugins-ugly", "mpv"),
    # ArtCraft binaries are admitted through pinned local artifacts.
    "office": (),
    "communication": ("v4l-utils",),
    "minecraft": ("alsa-lib", "gtk3", "libsecret", "libnotify", "nss", "qt6-wayland"),
    "steam": ("flatpak",),
    "hytale": ("flatpak",),
    "mail": ("thunderbird",),
    "gaming-chat": ("discord",),
    "study-tools": ("flatpak", "gtk3", "jupyterlab", "libsecret", "nss", "texlive-langportuguese",
                    "texlive-latexextra", "texlive-latexrecommended"),
    "messaging": ("flatpak",),
    "chatgpt": ("alsa-lib", "at-spi2-core", "cairo", "dbus", "expat", "gdk-pixbuf2",
                "glib2", "glibc", "gtk3", "libcups", "libgcc", "libglvnd", "libnotify",
                "libsecret", "libstdc++", "libusb", "libx11", "libxcb", "libxcomposite",
                "libxdamage", "libxext", "libxfixes", "libxkbcommon", "libxrandr", "libxss",
                "mesa", "nspr", "nss", "openssl", "pango", "systemd-libs", "tar",
                "tpm2-tss", "vulkan-swrast", "xdg-utils", "xz"),
    "minecraft-backups": ("gtk3", "libnotify", "python-gobject", "python-numpy"),
    "printing-scanning": ("cups", "sane", "sane-airscan", "simple-scan", "system-config-printer"),
    "development": ("cmake", "ninja", "nodejs", "npm", "podman", "python-pip", "rust"),
    "iphone-integration": ("libayatana-appindicator", "libayatana-indicator", "ayatana-ido"),
}

# Reviewed native packages that are not available from the official Arch
# repositories. The runtime resolves these names through the Host-owned,
# digest-pinned artifact manifest before invoking pacman -U.
LOCAL_PACKAGES = {"system": ("brave-bin",), "graphics": ("nvidia-utils",), "office": ("gridcraft", "wordcraft", "deckcraft"), "iphone-integration": ("localsend-bin",),
                  "minecraft-backups": ("salvador-de-mundos-apx",), "chatgpt": ("chatgpt-bin",)}

ESTIMATED_MIB = {
    "system": 420, "cli-aur": 260, "graphical": 520,
    "desktop-integration": 170, "locale-input": 190, "network": 70,
    "bluetooth": 35, "audio": 125, "graphics": 390, "power": 30,
    "devices-storage": 120, "files": 115, "web-documents": 360,
    "multimedia": 240, "office": 220, "communication": 55,
    "printing-scanning": 145, "development": 1150, "shortcuts": 8,
    "iphone-integration": 90,
    "minecraft": 200, "steam": 4500, "hytale": 3000, "mail": 260,
    "gaming-chat": 300, "study-tools": 3000, "messaging": 800,
    "minecraft-backups": 24, "chatgpt": 1850,
}


def normalize_modules(values: object) -> tuple[str, ...]:
    if type(values) not in {list, tuple} or not values:
        raise ValueError("Environment modules must be a non-empty list")
    if any(type(value) is not str or value not in MODULES for value in values):
        raise ValueError("Environment module is unsupported")
    selected = set(values)
    changed = True
    while changed:
        changed = False
        for module in tuple(selected):
            for dependency in DEPENDENCIES[module]:
                if dependency not in selected:
                    selected.add(dependency); changed = True
    return tuple(module for module in MODULES if module in selected)


def validate_selection(preset: object, values: object) -> tuple[str, tuple[str, ...]]:
    if type(preset) is not str or preset not in PRESETS:
        raise ValueError("Environment preset is unsupported")
    modules = normalize_modules(values)
    return preset, modules


def packages_for(values: object) -> tuple[str, ...]:
    modules = normalize_modules(values)
    return tuple(sorted({package for module in modules for package in PACKAGES.get(module, ())}))


def local_packages_for(values: object) -> tuple[str, ...]:
    modules = normalize_modules(values)
    return tuple(sorted({package for module in modules for package in LOCAL_PACKAGES.get(module, ())}))


def estimated_mib(values: object) -> int:
    return sum(ESTIMATED_MIB[module] for module in normalize_modules(values))


# These scripts run only as apx in the new Environment. The public request
# selects module keys, never downloads, executable paths, or shell fragments.
APPLICATION_MODULES = ("minecraft", "steam", "hytale", "study-tools", "messaging")

APPLICATION_INSTALL_SCRIPT = r"""set -euo pipefail
export HOME=/home/apx
export XDG_DATA_HOME="$HOME/.local/share"
/usr/lib/systemd/systemd-networkd-wait-online --interface=host0:routable --ipv4 --timeout=45
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
download() {
    curl --fail --location --proto '=https' --proto-redir '=https' --connect-timeout 15 --retry 2 \
         --output "$scratch/$1" -- "$2"
    if [[ -n ${3:-} ]]; then
        printf '%s  %s\n' "$3" "$scratch/$1" | sha256sum --check --status
    fi
}
entry() {
    cat > "$XDG_DATA_HOME/applications/$1.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=$2
Exec=/home/apx/.local/bin/apx-template-launch-app $3
Icon=$4
StartupWMClass=$5
Categories=Game;
Terminal=false
DESKTOP
    if [[ -n ${6:-} ]]; then
        printf 'X-Flatpak=%s\n' "$6" >> "$XDG_DATA_HOME/applications/$1.desktop"
    fi
}
for module in "$@"; do
    case $module in
        minecraft) ;;
        *) flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo; break ;;
    esac
done

for module in "$@"; do
    case $module in
        minecraft)
            echo 'A instalar Launcher Minecraft (Java) e Launcher Minecraft (Bedrock)…'
            download Minecraft.tar.gz https://launcher.mojang.com/download/Minecraft.tar.gz
            python3 - "$scratch/bedrock-release" <<'LATEST'
import json,pathlib,re,sys,urllib.request
request=urllib.request.Request('https://api.github.com/repos/Wyze3306/BedrockOnLinux/releases/latest',headers={'User-Agent':'APX-stable-install/1'})
with urllib.request.urlopen(request,timeout=30) as response: release=json.load(response)
if release.get('draft') or release.get('prerelease'): raise RuntimeError('O launcher não tem versão estável disponível')
asset=next(a for a in release['assets'] if a['name'].endswith('-x86_64.AppImage'))
url=asset['browser_download_url'];digest=asset.get('digest') or ''
if not url.startswith('https://github.com/Wyze3306/BedrockOnLinux/releases/download/') or not re.fullmatch('sha256:[a-f0-9]{64}',digest): raise RuntimeError('O launcher não publicou checksum verificável')
pathlib.Path(sys.argv[1]).write_text(url+'\n'+digest[7:]+'\n')
LATEST
            mapfile -t bedrock_release < "$scratch/bedrock-release"
            download BedrockOnLinux.AppImage "${bedrock_release[0]}" "${bedrock_release[1]}"
            launchers=$XDG_DATA_HOME/apx-launchers
            mkdir -p -- "$launchers"
            tar -xzf "$scratch/Minecraft.tar.gz" -O minecraft-launcher/minecraft-launcher > "$launchers/minecraft-launcher"
            install -m 0755 "$scratch/BedrockOnLinux.AppImage" "$launchers/BedrockOnLinux.AppImage"
            chmod 0755 "$launchers/minecraft-launcher"
            icon=/home/apx/.config/quickshell/apx/icons/lucide/pickaxe.svg
            entry minecraft-launcher 'Launcher Minecraft (Java)' java "$icon" 'Minecraft Launcher'
            entry bedrock-on-linux 'Launcher Minecraft (Bedrock)' bedrock "$icon" minecraft.windows.exe
            ;;
        steam)
            echo 'A instalar Steam…'
            flatpak install --user --noninteractive flathub com.valvesoftware.Steam
            ;;
        hytale)
            echo 'A instalar Hytale Launcher…'
            download Hytale.flatpak https://launcher.hytale.com/builds/release/linux/amd64/hytale-launcher-latest.flatpak
            flatpak install --user --noninteractive "$scratch/Hytale.flatpak"
            flatpak info --user com.hypixel.HytaleLauncher >/dev/null
            flatpak override --user --env=GDK_BACKEND=wayland com.hypixel.HytaleLauncher
            entry com.hypixel.HytaleLauncher 'Hytale Launcher' hytale com.hypixel.HytaleLauncher HytaleLauncher com.hypixel.HytaleLauncher
            ;;
        study-tools)
            echo 'A instalar Zotero e Visual Studio Code…'
            flatpak install --user --noninteractive flathub org.zotero.Zotero
            python3 - "$scratch/vscode-release" <<'LATEST'
import json,pathlib,re,sys,urllib.request
with urllib.request.urlopen('https://update.code.visualstudio.com/api/update/linux-x64/stable/latest',timeout=30) as response: release=json.load(response)
url=release['url'];digest=release.get('sha256hash') or ''
if not url.startswith('https://vscode.download.prss.microsoft.com/') or not re.fullmatch('[a-f0-9]{64}',digest): raise RuntimeError('O VS Code não publicou checksum verificável')
pathlib.Path(sys.argv[1]).write_text(url+'\n'+digest+'\n')
LATEST
            mapfile -t vscode_release < "$scratch/vscode-release"
            download VSCode.tar.gz "${vscode_release[0]}" "${vscode_release[1]}"
            launchers=$XDG_DATA_HOME/apx-launchers
            mkdir -p -- "$launchers"
            tar -xzf "$scratch/VSCode.tar.gz" --no-same-owner -C "$launchers"
            test -x "$launchers/VSCode-linux-x64/bin/code"
            cat > "$XDG_DATA_HOME/applications/code.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=Visual Studio Code
Exec=/home/apx/.local/share/apx-launchers/VSCode-linux-x64/bin/code %F
Icon=/home/apx/.local/share/apx-launchers/VSCode-linux-x64/resources/app/resources/linux/code.png
Categories=Development;
Terminal=false
DESKTOP
            ;;
        messaging)
            echo 'A instalar ZapZap…'
            flatpak install --user --noninteractive flathub com.rtosta.zapzap
            ;;
        *) exit 2 ;;
    esac
done
"""

APPLICATION_LAUNCH_SCRIPT = r"""#!/usr/bin/bash
set -euo pipefail
app=$1
shift
if [[ ${APX_GPU_POLICY:-} == hybrid ]]; then
    export __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia __VK_LAYER_NV_optimus=NVIDIA_only
fi
case $app in
    java)
        # Match the pilot launcher setting. The game renderer is independent.
        exec "$HOME/.local/share/apx-launchers/minecraft-launcher" --disable-gpu "$@"
        ;;
    bedrock)
        export APPIMAGE_EXTRACT_AND_RUN=1
        exec "$HOME/.local/share/apx-launchers/BedrockOnLinux.AppImage" "$@"
        ;;
    hytale)
        options=()
        if [[ ${APX_GPU_POLICY:-} == hybrid ]]; then
            options+=(--env=__NV_PRIME_RENDER_OFFLOAD=1 --env=__GLX_VENDOR_LIBRARY_NAME=nvidia
                      --env=__VK_LAYER_NV_optimus=NVIDIA_only)
        fi
        exec flatpak run --user "${options[@]}" com.hypixel.HytaleLauncher "$@"
        ;;
    *) exit 2 ;;
esac
"""
