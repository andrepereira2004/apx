#!/usr/bin/env python3
"""Bounded APX headless runtime used only by the disposable C0-C6 VM.

This is deliberately a closed laboratory adapter: it accepts registered names,
roles and plan digests, never caller-supplied paths or commands.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import uuid

try:
    from apx_environment_features import local_packages_for, packages_for, validate_selection
    from apx_environment_desktop_defaults import install_flatpak_defaults
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    from apx_environment_features import local_packages_for, packages_for, validate_selection
    from apx_environment_desktop_defaults import install_flatpak_defaults


STATE = Path("/var/lib/apx")
RELEASES = STATE / "releases"
ENVIRONMENTS = STATE / "environments"
PLANS = STATE / "plans"
JOURNAL = STATE / "journal" / "operations.jsonl"
SNAPSHOTS = STATE / "snapshots"
ARCHIVES = STATE / "archives"
BACKUPS = STATE / "backups"
LOCAL_RECOVERY = Path("/.snapshots/local-recovery")
RECOVERY_LOCK = Path("/run/lock/apx-local-recovery.lock")
NAME_RE = re.compile(r"[a-z][a-z0-9-]{0,31}")
ROLES = {"hub", "development", "minimal", "graphical-h0", "graphical-base", "hub-graphical"}
HEADLESS_START_ROLES = {"hub", "development", "minimal"}
GRAPHICAL_ROLES = {"graphical-h0", "graphical-base", "hub-graphical"}
HUB_ROLES = {"hub", "hub-graphical"}
GRAPHICAL_CONFIG_ASSETS = {
    "alacritty/alacritty.toml": "14f9191aec4f69568e4c12bba0b96c3cf90989f0a2295eb79bf1a277b7b6a3be",
    "fastfetch/apx-logo.txt": "cd7ae1943f3b4da9c751e93a1f19f5c12594ae35a28dce0d80fcfaa8f7149077",
    "fastfetch/config.jsonc": "9c8f7b3184452b42c3e8670805cf7215fa073a7fe32f25d9251a17e08bc4c736",
    "hyprland/hyprland.conf": "1f95c439e98dd1841eab68e859b6f3e5a85cee01ef7285594993ab0a0bda248f",
    "rofi/config.rasi": "2894cd7636fcf0f03f1a7c19a1008cb8b0c162ac5fae4e9fa85dfe7484a2aa78",
    "waybar/config.json": "7a045de24f89c69be7e373cc7dc82bb06b62b0a8ee15ec41719fbce0f0de2d2f",
    "waybar/style.css": "4e649de831c068be9ff05d0c9d6ad03351e1b1a1c44ad752b44a8c353bcd90ca",
}
GRAPHICAL_CONFIG_PREVIOUS_DIGESTS = {
    "rofi/config.rasi": "82d42171e3269240979e4f4e5c4a58410ad710d9a981cd6bab49f39a3b4c5c5e",
    # Existing admitted base releases retain the earlier Super+D binding.
    "hyprland/hyprland.conf": "8d793c51f1fb5195d12636ebc504d6c80cfac836245bacbcf5f90ac769a925ac",
}
DESKTOP_CONFIG_SEED = Path("/usr/share/apx/config-seeds/desktop-essential-v1")
DESKTOP_CONFIG_ASSETS = {
    "environment-config.json": "eebaa9be26aaa5d120ec71d7d68c17c326714b51b46961fd4651f30bdb75da88",
    "hub-config.json": "eac4219dc026fab9ea2bfd34d51dc9bcb69418fa9b2a727b692112f2160c40eb",
    "style.css": "f26c8dec509c50ae56cf7f5fe2861266a2056ca4667493b94e186a801e58c80a",
}
ENVIRONMENT_SHELL_SEED = Path("/usr/share/apx/config-seeds/environment-shell-v1")
LOCAL_PACKAGE_ARTIFACTS = STATE / "package-artifacts"
LOCAL_PACKAGE_MANIFESTS = {
    "localsend-bin": "localsend-bin-v1.json",
    "gridcraft": "gridcraft-v1.json",
    "wordcraft": "wordcraft-v1.json",
    "deckcraft": "deckcraft-v1.json",
    "brave-bin": "brave-bin-v1.json",
    "nvidia-utils": "nvidia-utils-v1.json",
    "python-dlib": "python-dlib-v1.json",
    "howdy-apx": "howdy-apx-v1.json",
}
ENVIRONMENT_SHELL_ASSETS = {
    "quickshell/apx/icons/lucide/package-open.svg": "261a0676ee3db3e5c64a528ac7f81a4893ddb3dfebd0549562f4ef5033757920",
    "quickshell/apx/icons/lucide/package.svg": "69d6bc7650d26c4d24dd55eb22791607b982ce7637073944c256f1f61575509d",
    "quickshell/apx/icons/lucide/paintbrush.svg": "b0a958ba9889f89c40df6e1c168b8a7aa20f6309780e795c5bce00a4bc11bff6",
    "quickshell/apx/icons/lucide/satellite-dish.svg": "7ce3938a89d6c2cec3563a1653248c26ad1227ae139b5a2b7d7ae32778928511",
    "quickshell/apx/icons/lucide/square-stack.svg": "9f7550f0db1a934166d8c253613c43151554d69bcacaf36883f817b880f037fe",
    "quickshell/apx/icons/lucide/audio-lines.svg": "3942b8a5d6bccc927a55f857f0d44b90e2663470cd2d569000c9b60c37578dfa",
    "quickshell/apx/ControlSlider.qml": "c52c4da5377e980ce01adcda291ca4ed4daf099ef154476deddd6e0d69598ba2",
    "local/bin/apx-lock-date-v1": "79ff3f94b983a3d722450cb62f15407d5f1511e52bb815b29aaa803da33ef6fc",
    "quickshell/apx/MediaIsland.qml": "d006f4ec56d45ebb799dab586a9a963da2bad6249ddacd0636ba2c07a366d4b2",
    "quickshell/apx/MediaTimeline.qml": "586d9a06a2d68a8d77996b4880331ec40abd19905b8d5c934f53f6ef40df8698",
    "hypr/apx-lock-appearance.conf": "0a6f8e7876be85418416e495a77805b733af60ad6a3719a84e875b5b72894d52",
    "quickshell/apx/GhostLines.js": "2c492329f225bc21c9e53e40cd3eb0a308026cd3b887f7ae96c603bec617c728",
    "quickshell/apx/icons/lucide/skip-forward.svg": "f6bdc4b8d453332bafcf1366a48d5ece4bd4f15eced97c85c3676bd22c5cadf9",
    "quickshell/apx/icons/lucide/skip-back.svg": "901579624a7d28036a39b3b8bd9e6da0e8cf771a79c67836d8a52b3e2287c031",
    "quickshell/apx/icons/lucide/pause.svg": "f122ec4ea7f5693a0b1baafa9c708b53980dc87b4aacb297c6e6f71c1a4c115c",
    "quickshell/apx/icons/lucide/play.svg": "d7c34786135922a92b6896f6c2384ceeb0346afbf6041dc79982011411409833",
    "quickshell/apx/icons/lucide/bell.svg": "394889e9631fe3a9a63be9a479a95b451b708e432d895978d21d9130b5ee5dbe",
    "quickshell/apx/icons/lucide/video.svg": "d4fb6587f282c1152b953fe9494cd8ccafdf1e9f44957fbb7fe8dc7af0457597",
    "quickshell/apx/icons/lucide/music.svg": "8721b8a3594219c1313c4083049e5a5c049f49c47b1cd93fdb61d52a0803e42b",
    "rofi/apx-appearance.rasi": "e58fd6c0f51e10a0a39868ac26c13cea0a1623f6f5858e3fc8a333eb2213f13c",
    "kitty/apx-appearance.conf": "cf1b2020a68ee63e95f1ca2d96f669695c2a128d65793662f42f889454a39f7c",
    "local/bin/apx-desktop-activity-v1": "9b698ffba9d64e9aad73600c5bec37a09c62bafd23626e18295d36bb9f376da7",
    "local/bin/apx-appearance-v1": "e4c31cc192f3bf006765adf8c05a96c5e23ecfc2b357bd9b9315167f1205cfd4",
    "quickshell/apx/qmldir": "9d1abeb211de84093ac38db457560d306193b2ce8e1baa79b5651134ef18ce0e",
    "quickshell/apx/ActivityPanel.qml": "c7a3c39b738d6f1fe66b420bb1d5724d0393ffb4fb9a8673808aa3db1dfae8bb",
    "quickshell/apx/ControlDashboard.qml": "2000bb9f3260926ea35ee30aa7c5b663ffcb9b7b9c46c50423cbd5007f4f2f1d",
    "quickshell/apx/ControlTile.qml": "d175e911d764945f08fa6f4839a650d0821e3099d4e789c33a7ddbd756fb0dea",
    "quickshell/apx/DesktopActivity.qml": "08015b742c97bc9abf704c6cb5ebd62d37e13b481790baa24064bde5eec40766",
    "quickshell/apx/PersonalizationPanel.qml": "c1c030d05114fd02ed67b5f9cdf8c41f48b336161c53d07bdc270708c6461d0c",
    "quickshell/apx/Appearance.qml": "fd98999eee9e12d974f61ac1c2be0a621d6fe23c589c8794c2bc076b4483238c",
    "local/share/fonts/jetbrains-mono/OFL.txt": "a76abf002c49097d146e86740a3105a5d00450b1592e820a1109a8c5680cd697",
    "local/share/fonts/jetbrains-mono/JetBrainsMono-Regular.ttf": "e6fd0d7e91550b3ed2b735d4312474362c4716edc4fc0577a0f61ed782d5aed1",
    "local/share/fonts/jetbrains-mono/JetBrainsMono-Bold.ttf": "d22c4f3821d725eb01210d278d95dfcfcaadc34699a06658d47c8a5cc5830ada",
    "quickshell/apx/icons/lucide/check.svg": "7f33acc9a77a61659531044525fc008edebe215bf4dcf1c789c8674ad3277db0",
    "quickshell/apx/icons/lucide/x.svg": "4a9cdab38fbb96162e7dace28e33f4ca0e49d8963a6162abc3d4691b7d675117",
    "quickshell/apx/icons/lucide/plus.svg": "7f6af73bf1ff6c4bca3f18351c8d1bdec6749c0c2530c4de5da85d520c21df17",
    "quickshell/apx/icons/lucide/usb.svg": "6d3feae2abc694973d7dc8000a7016688306b82530426288c163257ac90d3e21",
    "quickshell/apx/icons/lucide/headphones.svg": "7719585dafa921805aefc21fc3262bbcc621507610a653b84e1632236650b35a",
    "quickshell/apx/icons/lucide/LICENSE.txt": "b495047bd93a9b06913511076f504daba17d5bbeb3e0650f3bb53a4220329c57",
    "quickshell/apx/icons/lucide/plane.svg": "4c775a62a524be78fe20aed8544933d4bd3802c5eca17cd6923509f87671d6d6",
    "quickshell/apx/icons/lucide/globe.svg": "82c6b8fa0b8e8d775ec9becd86f74a4e50bff7bee4c81f7362de45348504f14d",
    "quickshell/apx/icons/lucide/circle-alert.svg": "ce3e98b7a03b78c0071131df42466e4e1ff5187fccad30e739ec9ce951cf685a",
    "quickshell/apx/icons/lucide/circle-check.svg": "9711e045a5999f8a3b0782eb88e09b04e0559bc7b379dcc0a4ae645223e10345",
    "quickshell/apx/icons/lucide/mouse.svg": "e4238ad7b69d3c3d713fdc2284c8fb20c04781afe0be445539ce4f904c0a0e47",
    "quickshell/apx/icons/lucide/settings.svg": "0ae27fd0f81999229e3127ac96c5b32edfea448e291d509e76212b917551d66b",
    "quickshell/apx/icons/lucide/search.svg": "283d371c2e433817bb9c0c8310caa6c77fa4177c0f4f1168d9c83b97af7389dc",
    "quickshell/apx/icons/lucide/shield-check.svg": "8d4fcdbde5bba4abb1a2f6fe53e37ceb6343a1d5449a9d88f6f97c1971d26c4e",
    "quickshell/apx/icons/lucide/touchpad-off.svg": "101255da206d37e25764520a28ad451a29ce9535b00a2ff290aa8e0a4e799586",
    "quickshell/apx/icons/lucide/refresh-cw.svg": "2e10dd403c85a24f163d59fc6151aa21147fe9402e1305dfc8979208caee8944",
    "quickshell/apx/icons/lucide/touchpad.svg": "9d743d5ae640f51599fb006450e07469123aca45c228021610e7bfa78e494547",
    "quickshell/apx/icons/lucide/camera.svg": "ebbb3178dd80dfd942770a2237fe7bfc3515c55c7daa9d3666933a656d2790e3",
    "quickshell/apx/icons/lucide/panels-top-left.svg": "321a2a5500f2b814a2e62eb73c4b01dc65c7334fe2e6f7d77517239383e26bb1",
    "quickshell/apx/icons/lucide/calculator.svg": "a6b191250b1ffabdf9fc9536662309f1b0f65336aa681d75bae9f1708baaefd0",
    "quickshell/apx/icons/lucide/terminal.svg": "4f9b6488b237757d5cb615ccd07502fa99774826839e2a99017784bdb2596f1a",
    "quickshell/apx/icons/lucide/rotate-cw.svg": "ddcfe6d87240475946935e77411cd4d15a06f3d28a9b921bafed224ebe953668",
    "quickshell/apx/icons/lucide/folder.svg": "f0d92b94b797a8ab7d4c4ae33c3236c47f64068351b4e14bdb5014ee42898a39",
    "quickshell/apx/icons/lucide/log-out.svg": "f24b5b45c05a3acc346af8095408f6ba197ff58ea1641a4f2cb25a9702d2c0ac",
    "quickshell/apx/icons/lucide/bluetooth-connected.svg": "d39c628c736b13b022f154e9aaa8aad178ef1d090a9bc14f1f4740c24767d828",
    "quickshell/apx/icons/lucide/power.svg": "1e6b84a659aa43f826cdd8df0a63d349720004e2ccb10c33e415a990a311aa05",
    "quickshell/apx/icons/lucide/lock-keyhole.svg": "fc0b8b7590d1d9e9bb0112c5c2e15a78ade0bfeca6d6f8c79fbbe149236d74be",
    "quickshell/apx/icons/lucide/wifi-low.svg": "08629f9524f555100325f1f782105f6f84391e6ace1b41b53e99da2af5dcc733",
    "quickshell/apx/icons/lucide/wifi-high.svg": "1890bf0a7b7abe57550e817639dd530f2cbc82eb261331e72e3947c589ee2e75",
    "quickshell/apx/icons/lucide/wifi-off.svg": "318b290106e55c3505933f434d3663524206c7a44165a89508774fba4fdbaadd",
    "quickshell/apx/icons/lucide/bluetooth.svg": "f2bf3d88cf608834dc389f01b1ee41fdb7bf3656dabef69632c60d5498f3bf29",
    "quickshell/apx/icons/lucide/bluetooth-off.svg": "61d26b013859d73ddf585d7b6e460ab2a6f02ca3ec2faf4b646cf9054224c22c",
    "quickshell/apx/icons/lucide/wifi.svg": "5c4c795d014fa95d1e1038362df44a0f0f32ded9cb08c833ae72419ebadc9a91",
    "quickshell/apx/icons/lucide/hard-drive.svg": "324363c40f54e4ca843de0ad1d023b063b70a26a83bb2e0a9e9f4aad9af37378",
    "quickshell/apx/icons/lucide/keyboard.svg": "f509925ca81964ed06251ad4702e989bb81a566ffc74d15c2226b4f07ded67be",
    "quickshell/apx/icons/lucide/mic-off.svg": "bcb5a033b4ecd182ec8d0d0945810ccc5147219b1a21c017b47fd4d5ae3a8320",
    "quickshell/apx/icons/lucide/volume-x.svg": "f382e421b7aae01172989f2b749ee87e44c0c82c16970b13a9ad5a323b613be0",
    "quickshell/apx/icons/lucide/sun.svg": "a3955c8b0425fcc5c9ba12d2bdd77fe53b2cd5dd05e7742a56f342e996fb2ef8",
    "quickshell/apx/icons/lucide/mic.svg": "9b940cd735d1ffa270ba670c4e677d9a09400f3fa81d6b3f405b12a3b67a59a8",
    "quickshell/apx/icons/lucide/volume-2.svg": "fb404f9c128a0579de67b399177631e5edb3502fdc247ceb30e8b15754b46071",
    "quickshell/apx/icons/lucide/grid-2x2.svg": "dc1896d3b22e88e0ba45a77bc8e947b7a01d0c9fb5ff77d07d24a5589816bb84",
    "quickshell/apx/icons/lucide/ghost.svg": "7577ea4e1390a8a8203509dff037fa74791ecebb145cdc5e3f3349de2f009278",
    "quickshell/apx/icons/lucide/zap.svg": "4c395891eab4d1e5627c5d414a16db037317cb2f12453de0f3a1130964c6d444",
    "quickshell/apx/icons/lucide/swords.svg": "2dcf7d618baa1fbf21064bc99eb754b8b6d589f444781975a6ea0008be4e2e82",
    "quickshell/apx/icons/lucide/hexagon.svg": "d6fe215b28eaccc1d50b89b967ae0bd6368ed602a89fd90b3c02688c15f133df",
    "quickshell/apx/icons/lucide/calendar-days.svg": "9330eb8d7c4989e97b6361314abbf02953243c602874725c9e58ceca00da3bd7",
    "quickshell/apx/icons/lucide/chevron-left.svg": "83b0681aa38bf55e9d52a1e4b4cced624abe1fe7678ecafda133a574f1161d93",
    "quickshell/apx/icons/lucide/chevron-right.svg": "2758143d7b2434e4aa7307dfd34405c87909ff4052f21b5f3f40d45224b4f19b",
    "quickshell/apx/icons/lucide/pickaxe.svg": "b8a9ff74ad1cb09dcaa4b11d2155744a7b61e23d85e01bb4a930ea44aa0dcacc",
    "quickshell/apx/icons/lucide/battery-low.svg": "a158265a07d3ea60134de7ca88c023ebbe35d9af9c724c410ed251f248987a52",
    "quickshell/apx/icons/lucide/monitor.svg": "d1a443233345724859de8e4fb48968ba91e885e12ddbd710701548bd91b39428",
    "quickshell/apx/icons/lucide/battery.svg": "bd0e96da226beca6d150ee25f04bc5ca8466c1ed91e806c2179723e173af2282",
    "quickshell/apx/icons/lucide/battery-charging.svg": "6a95bf102235d7070121bb8eb21a4836fa7ea9f0dbe8327eadbdf94253acdcbd",
    "quickshell/apx/icons/lucide/battery-warning.svg": "d59e1af8b6247b59df0535197456fc25df978ae14a9e786c636815ab04c95904",
    "quickshell/apx/icons/lucide/battery-medium.svg": "f8a79b837f96c801ffc394d1d154c5a792823e3bb506bb98a4379b0647067e0a",
    "quickshell/apx/icons/lucide/battery-full.svg": "9ef66bd46e676bbcf1e8befca8e904b93be9214abccea4f8a4d20432a0c5ccf8",
    "quickshell/apx/IconLabel.qml": "37e073d44c73c7cfaa445de1df3a5749493ea8f613373290ab4cbf216bb6d43c",
    "quickshell/apx/LucideIcon.qml": "17873952b5be593d1f543c66706a7a04fc85d7e8c3c0a2b2ddc19b39f78c3b88",
    "quickshell/apx/WorkspacePager.js": "86ed3a02b0c0b317d1a3c25907ebda91057dacb6c148439ffbf3f78074f60dfe",
    "quickshell/apx/WorkspacePreview.qml": "4cdc17fa552e8870865d2f4fbfa2182e2db2ae08910ec494504edccf741075fb",
    "quickshell/apx/WorkspaceStrip.qml": "768ae2e9529c4df8e3fef43785570030faecf4b9b063a2ac18f7ce79e37c7a0b",
    "local/share/dbus-1/services/org.freedesktop.impl.portal.desktop.gtk.service": "d1f568f71a2961404fb7cea035c1d524d0a811749f5a7499a0dd12515d387446",
    "local/lib/apx/libchooser-places.so": "23adc03533f0f28db9c299ba3fef37e459f06c0a1355123892b499f59eabd927",
    "local/lib/apx/chooser-places.c": "287c6f7454111a29d14d937d3adcee326bc6d95767f012f4d352e88a8682c11f",
    "local/bin/apx-document-templates-v1": "6d300ad6f33d8119dd950a0d1dad73708a64059c2dd920b353af2530d2cd6d84",
    "local/share/icons/APX-Graphite/scalable/places/apx-folder-tagged.svg": "bca05a5e9a3691fd586fde133f2414ac82d738b4953b997e5c64859540b3aad4",
    "local/bin/apx-removable-bookmark-v1": "39828754ff29cc507bf7250a375ef705ab0f6a337b565c2e2b45aac8ce24a038",
    "environment.d/80-apx-locale.conf": "fdc040d098a158c677e344df5cb62a9be9e4f9d52f5caa0e5087f158726f5586",
    "apx/locale.env": "fdc040d098a158c677e344df5cb62a9be9e4f9d52f5caa0e5087f158726f5586",
    "local/share/thumbnailers/apx-folder-color.thumbnailer": "f8306feca643786465607ca5e38dac042b3e8557ff868350131370d08fe18e0f",
    "local/bin/apx-folder-color-v1": "abf168fbf32431e9e85c06d2427191f5f5ed815d9698d2ea89c113a0c8c9eae4",
    "local/share/icons/APX-Graphite/scalable/places/apx-file-search.svg": "21328a3e719474b54dfbd799a08bbd5d36da92c2bbc0f6e644f9ba1bc3dad1fd",
    "local/bin/apx-rofi-files-v1": "7d33e8ebf5ed594e66040a4ff3b4d2c4ad475244e84146cd113c9c458bd5befc",
    "local/share/icons/APX-Graphite/scalable/places/go-up.svg": "1a4dd9f99a622c3b7382d0365776f915fb751fa09c8138634e89f2945973da12",
    "local/share/applications/apx-browser-redirect.desktop": "b800a6301a593037dcb80d7bd9140be5cb7f30d05d94f93b23f6dc8a5b395d81",
    "local/bin/apx-browser-redirect-v1": "12848fee38e1b8dd84d4aec32fbbc17cafb297d61395a959745d1e079b8e8cdf",
    "Thunar/uca.xml": "ecc0869f622121d9a07fb21948719638a0043548939ae0ca46fc502b8655350f",
    "apx/bashrc": "c92bd4f495294992126c8145ef2990d3042ba4d42c820332881ad08669872c04",
    "apx/wallpapers/alpine-lake.png": "dd5794c56ac03f3befb28b48554222da3a44f8f695fb4f1e9f8ac8c3f14ff09d",
    "apx/wallpapers/atlantic-coast.png": "2204c16ad3f3cea13c2b0af0179800262a0a282685bcea13e2d94d1da7cf1411",
    "apx/wallpapers/rainforest-stream.png": "624a391248bee708ce4195735f9e69937083d0e2f7ba4b9f025d92f231916535",
    "brave-flags.conf": "beed8f20ca3b1de51bfd0a03b862afd62e51933141378c67bd1f34be1443280f",
    "fontconfig/fonts.conf": "ff525fe6d18ebead4e7e1a7ed92ca5d92b8d73f0544a129aa2161ebcc2bc3b24",
    "gtk-3.0/bookmarks": "04319388475f0674511ab87d2ea11e52c6407414bd975daa9cf4254ff9c207a2",
    "gtk-3.0/gtk.css": "84561eaffd8b25fecc91b650cff44363f216243ee665f6c6bce4f78a3ccaafbc",
    "gtk-3.0/settings.ini": "aedb8ee4ad26b7edda0a2aa9fdbbabd17ebfb23eabebf00182e3d1ef167609e1",
    "gtk-4.0/settings.ini": "aedb8ee4ad26b7edda0a2aa9fdbbabd17ebfb23eabebf00182e3d1ef167609e1",
    "hypr/apx-monitors.lua": "ac3a58b2504062c0faa3b3c452743a5b09f5367cfb2956a4c4d36e9fb0755585",
    "hypr/hypridle.conf": "02a0289df8cf26bb3c537ec40cdc2d3e64b08a52785d2759a6ec1cab1ba04476",
    "hypr/hyprland.lua": "78732354b8f9201cb377709f513505edf2722d194bad5527ff5cf65e2a186216",
    "hypr/hyprlock.conf": "83248958d784948fba70f244ef5c0a07939a9822e1931847fe0d5e6b50a4fb62",
    "hyprland/hyprland.conf": "43c9eead30c90654ef7280b5eedf092ec739d04c528784e251292db7e25a6f9f",
    "kitty/kitty.conf": "730e31722bc7d91f3378f64c6e3908da591d2c2510a4909b598630f88d715b94",
    "local/bin/apx-application-catalog-v1": "3f1c9975db56b72b0e463ca973f95a47eeda67d9706ffa45857fae5ad6c5f60c",
    "local/bin/apx-application-remove-v1": "6aafbba4688bcfc34757dae80da0300463523e41e9a64d3cc81f7b9525a336d7",
    "local/bin/apx-desktop-activation-v1": "2f1749c4ae9591665a9a51d8db5abb5e2f86294f3e0a7d8fad3dafb14f668f3f",
    "local/bin/apx-detached-launch": "40970a9ed235a6799913211dc135c66222ee55e15d5d38e5cfe5d2feafd785ef",
    "local/bin/apx-environment-update-v1": "7cc941774449bef66937693cf3424ee0a71564961d58c2571bdec8a67131ae96",
    "local/bin/apx-face-auth-state-v1": "82ea2de97b0990ebbd7dbdf1c664ee81343aabb84c98fc2f86501f45706da3bb",
    "local/bin/apx-host-console-open": "99c2e22329af1acbebe5c987651353acad76cd1181b946d4c2dbbed706e8c396",
    "local/bin/apx-host-console-terminal": "187025f24fda099acc85a7b82b0e0cacfd979f86feca77219911e661e7ec963e",
    "local/bin/apx-keyring-prepare-v1": "ca3f235fd1598cb8093af6bc48bd6e1d1c77f57271db243d435e8b831e1a89c1",
    "local/bin/apx-laptop-action-v1": "2517fe5fe364b5c2fe258c8c3eec63db3190333dc8daeae2f6ff4e9ba717001c",
    "local/bin/apx-mouse-sensitivity-v1": "8e6a8286f25c030c5d274f874176e7b12708daeddb0b23191a3159880d16e145",
    "local/bin/apx-legion-brightness-keys-v1.py": "510443669c26bf7ede73af8d56f37ee04faf9c4a0ca2d7afe3343742cd95b550",
    "local/bin/apx-notification-focus-v1": "835cc0302f10f01c2417077884fca7f9b9a6b95b2328ac8d32dccc4e93ca7cc0",
    "local/bin/apx-shell-v1": "55e45c39f93051fddcc95beb957172eba50c31ae6809ba082292f59c1c49955c",
    "local/bin/apx-shortcuts-v1": "c94ec111c09c46cfd58e4c74b400d224e736e593754c8e1b9896eca9ea288995",
    "local/bin/apx-sysinfo": "1daf4b37c84c855191d2190e2c44a91b95b96b0ce1a46944ea28f580349d14b5",
    "local/bin/apx-window-apps-v1": "2484dc866f612290efb2f5b5949a3eace0ca0e5562a4e8d251c5296407c5299d",
    "local/bin/apx-workspace-overview-v1": "830c8dd169b2e180bcc2671c52c14ada5037873ebc3152090af466522b76483e",
    "local/libexec/apx-rofi-secondary-v1.so": "1de32d764d0a359a3b6334097a92452155a50d38adc92ac035c213296ffea75d",
    "local/libexec/apx-system-power-client-v1.py": "c037419f59503c255a18a6144e363b146db3238c96b229e44dbfd04cb049e410",
    "local/libexec/apx_system_power_contract.py": "ced2405cbc1bd8ed7a49a2061be48ee3ff8f2d5f263e8cea93d219ce7a3622a8",
    "local/share/applications/apx-terminal.desktop": "10ed8d658f950a562f71e165f8e42661228088e45bc532b75b99bce74745bb44",
    "local/share/fonts/cascadia/CascadiaMono-Bold.ttf": "b22cb603ed23cac36e8444846e1841caca21719a5e852780a8d37ae7a49b0a36",
    "local/share/fonts/cascadia/CascadiaMono-BoldItalic.ttf": "ecaeab55e6334408f8ff1fde78a99ddaeb3bb7fad4fcd177df8475c88a7d240f",
    "local/share/fonts/cascadia/CascadiaMono-Italic.ttf": "8d98a33e7617c14dd1d200b4900bc6c2d5d7165abb5c09e9d2fd51c38ce9c9ff",
    "local/share/fonts/cascadia/CascadiaMono-Regular.ttf": "06520d032ec274fa5040b22c6f4a1d829081b24ba40b2da56dae89bf10c7b481",
    "local/share/fonts/cascadia/LICENSE.txt": "51882cd3cdba4e16f220f44ddb08a635c38c44ea6e0975db2574f4be6f958238",
    "local/share/fonts/selawik/LICENSE.txt": "77b7c2506d4efb22e09c8ccf10159f4956eab3ef7c007fef95de136bcf45300c",
    "local/share/fonts/selawik/selawk.ttf": "e9d98518d8ac2817782a9a382430463a2e0793ea68350b695bb727d9a830ee1c",
    "local/share/fonts/selawik/selawkb.ttf": "f0db5e174a90e0956ad7d2844bdca1d5e6da92ec65b2c04e57ba9b180668c904",
    "local/share/fonts/selawik/selawkl.ttf": "8e19d073091a1e869b5b0d48b925e605c0a4c6ece7df7b22a364fb065314c4c5",
    "local/share/fonts/selawik/selawksb.ttf": "0a9e9d0549a10f24bef9b3a29e06fe6e0b5c21e7a784c503b048a307841a7783",
    "local/share/fonts/selawik/selawksl.ttf": "8620960344f12093482cded984a1aafa5a57d24cbf7e9299da125ccf0e9d4102",
    "local/share/icons/APX-Graphite/index.theme": "6ec40f1027ef75c09e80d1143779d806ad92cbea920353689994c9beef965b50",
    "local/share/icons/APX-Graphite/scalable/places/folder-documents.svg": "0ae5d0547d11f011c2b425338d7f7df6b5a89c9209646b9a994b219ca8fe6eff",
    "local/share/icons/APX-Graphite/scalable/places/folder-download.svg": "19321af475280625ed2327c03630a85f4a6a2c81424635f4079f9ce3cde58c3b",
    "local/share/icons/APX-Graphite/scalable/places/folder-music.svg": "4e7fc7f5ec7fd8ae0b6cb3f489045c85372245000a68a09929457000782f2ce1",
    "local/share/icons/APX-Graphite/scalable/places/folder-open.svg": "62b238be55d47936d801695dfc19bb66bf6640c19c6a73de54aa27893dbf74a4",
    "local/share/icons/APX-Graphite/scalable/places/folder-pictures.svg": "477cd43895a95cd5d64d212f427b8dbc54cbbb847a147ced86da614a3ef606c3",
    "local/share/icons/APX-Graphite/scalable/places/folder-publicshare.svg": "bbcad1194e605f0d51e172a1b83c093a271ceb3a31d4418c8978dc064c244bec",
    "local/share/icons/APX-Graphite/scalable/places/folder-remote.svg": "337921ce54353749fc9496b0b59e3ab2774e2ca607833a33413f28ac32b3db50",
    "local/share/icons/APX-Graphite/scalable/places/folder-saved-search.svg": "e371d22b79521f3c4b139322bb12307df50d73e248e96531eaae1b42d47cde7d",
    "local/share/icons/APX-Graphite/scalable/places/folder-templates.svg": "f036a39e0fcd703fe6081b6ba45fc9164506906ef7f26895e39d0f4429d1ffe6",
    "local/share/icons/APX-Graphite/scalable/places/folder-videos.svg": "1ff0dbfa2d18ab03b727bd2f115da5b9790d6a5a5afb2b45171d2a24bbf428a9",
    "local/share/icons/APX-Graphite/scalable/places/folder.svg": "62b238be55d47936d801695dfc19bb66bf6640c19c6a73de54aa27893dbf74a4",
    "local/share/icons/APX-Graphite/scalable/places/user-desktop.svg": "d015e06aa73c72e3042568ad2327132acf5176c610abeb7acfa443af51606ab6",
    "mako/config": "3b12173118265250fac23f25191178c80f113ee8e1ed5cf4603ed8b5d84d0a60",
    "mimeapps.list": "3296274c3469bdf7a5bc6e244ab70b02aa4852b986b0c2f6dac67f9c2d15df3b",
    "quickshell/apx/BarButton.qml": "98d36316192480a87404944d65fb7eb834d4877ca1c3d5b6b5e96d3a051fb6cd",
    "quickshell/apx/BounceMouseArea.qml": "6d6ea8c4f2d926ca40f157ea0d7443134cc35bbe9c675dc148b4aeaa6275c938",
    "quickshell/apx/ControlIcon.qml": "a567b753b4dc09fca1ef5bcedc55c2dd2138ee69cb1cfac67819a3f2dbe24317",
    "quickshell/apx/calendar_store.py": "e23e6d4121f8b96647e2c0d8a8d1263e4d51f8f6d60dabebc9d3a6fce5379136",
    "quickshell/apx/shell.qml": "3bcf7735a1874dd5d1d08b770a08e61f89493071767023f8f31459eb0640e4c1",
    "rofi/config.rasi": "7871629dc71c763dfabb39fc5a2d4171ab6ba85a0d42b49b11058bd8605c9ddd",
    "xdg-desktop-portal/portals.conf": "eb738862539c32c2515a70db6578c94734bdbecde111968c7d8151e3ac3aefd9",
    "xfce4/xfconf/xfce-perchannel-xml/thunar.xml": "4479d56f259731715d38f9231adc4b6491398525648ff99c8f6179083226ea9d",
    "local/bin/apx-settings": "4ba183b406890e0e3dbbe13afef979f6b1f382c2415d50de28008f460ecc8e9f",
    "local/bin/apx-desktop-preferences-v1": "5dcba47a6b509d1b5e48063bcd1d4b052b3755fec97552408106d433190ed674",
    "local/bin/apx-clipboard-menu-v1": "8e3e3469bf2b92366000cc20c55f577a85e6243cb719844f089a4b6c7c4d663f",
    "local/share/applications/apx-settings.desktop": "a14f790b359027ba5f844d6c3bd262c95bd955c62647a66a23eafeb7d23e8738",
    "local/lib/rofi/apx-rofi-files-v1.so": "c848996c6325aa31541fbbd19205c4a8d957cc684c77f660b8ced9c4d7ee5917",
}
MAX_GRAPHICAL_CONFIG_BYTES = 1024 * 1024
MAX_WALLPAPER_BYTES = 4 * 1024 * 1024
RELEASE_IDS = {
    "hub": "hub-headless-v4",
    "development": "development-headless-v1",
    "minimal": "minimal-headless-v1",
    "graphical-h0": "hyprland-h0-v1",
    "graphical-base": "hyprland-base-v2",
    "hub-graphical": "hyprland-base-v2",
}
HOST_STORAGE_RESERVE_BYTES = 96 * 1024**3
STORAGE_POLICY = "bounded-environments-with-protected-host-reserve"
ENVIRONMENT_STORAGE_LIMITS = {
    "hub": ("16G", "32G"),
    "development": ("32G", "64G"),
    "minimal": ("8G", "16G"),
    "graphical-h0": ("32G", "64G"),
    "graphical-base": ("32G", "64G"),
    "hub-graphical": ("16G", "32G"),
}
ENVIRONMENT_RUNTIME_LIMITS = {
    "hub": ("600%", "10G", "12G", "4096"),
    "development": ("600%", "10G", "12G", "4096"),
    "minimal": ("200%", "3G", "4G", "1024"),
}
LOCAL_ADMIN_MARKER = "/etc/apx/local-admin-v1"
NETWORK_ADAPTER = "/usr/lib/apx/apx-environment-network-v1.py"
EFFECTS = {
    "create": ("root", "home", "configure", "publish"),
    "destroy": (
        "stop", "purge-update-rollbacks", "purge-snapshots", "purge-archives", "purge-backups", "purge-local-recovery", "remove-home",
        "remove-root", "purge-metadata", "unpublish", "purge-plans",
    ),
}


class Refusal(RuntimeError):
    pass


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def run(arguments: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        check=check,
        text=True,
        capture_output=capture,
        env={**os.environ, "LC_ALL": "C"},
    )


def require_root() -> None:
    if os.geteuid() != 0:
        raise Refusal("this laboratory effect requires the host executor identity")


def validate_name(name: str) -> str:
    if not NAME_RE.fullmatch(name):
        raise Refusal("invalid Environment name")
    if name.startswith("apx-"):
        raise Refusal("logical Environment name must not use the derived apx- prefix")
    return name


def validate_role(role: str) -> str:
    if role not in ROLES:
        raise Refusal("role is not admitted")
    return role


def validate_role_assignment(name: str, role: str) -> tuple[str, str]:
    """Reserve every Hub role for the canonical Hub logical identity."""
    validate_name(name)
    validate_role(role)
    if name == "hub" and role not in HUB_ROLES:
        raise Refusal("the Hub name requires an admitted Hub role")
    if name != "hub" and role in HUB_ROLES:
        raise Refusal("Hub roles are reserved for the canonical Hub name")
    return name, role


def copy_graphical_config_seed(seed: Path, destination: Path, uid: int = 1000, gid: int = 1000) -> None:
    """Copy exactly the admitted regular files from an immutable release seed."""
    if not seed.is_dir() or seed.is_symlink() or destination.exists():
        raise Refusal("graphical configuration seed is absent or unsafe")
    config_directories = {relative.split("/", 1)[0] for relative in GRAPHICAL_CONFIG_ASSETS}
    expected_entries = set(GRAPHICAL_CONFIG_ASSETS) | config_directories
    observed_entries: set[str] = set()
    for entry in seed.rglob("*"):
        relative = entry.relative_to(seed).as_posix()
        observed_entries.add(relative)
        metadata = entry.lstat()
        if relative in GRAPHICAL_CONFIG_ASSETS:
            if not stat.S_ISREG(metadata.st_mode):
                raise Refusal("graphical configuration asset is not a regular file")
        elif relative in config_directories:
            if not stat.S_ISDIR(metadata.st_mode) or entry.is_symlink():
                raise Refusal("graphical configuration directory is unsafe")
        else:
            raise Refusal("graphical configuration seed contains an unapproved entry")
    if observed_entries != expected_entries:
        raise Refusal("graphical configuration seed is incomplete")

    content: dict[str, bytes] = {}
    for relative, expected_digest in GRAPHICAL_CONFIG_ASSETS.items():
        path = seed / relative
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            value = os.read(descriptor, MAX_GRAPHICAL_CONFIG_BYTES + 1)
            if os.read(descriptor, 1) or len(value) > MAX_GRAPHICAL_CONFIG_BYTES:
                raise Refusal("graphical configuration asset exceeds the size limit")
        finally:
            os.close(descriptor)
        if hashlib.sha256(value).hexdigest() not in {
            expected_digest, GRAPHICAL_CONFIG_PREVIOUS_DIGESTS.get(relative)
        }:
            raise Refusal("graphical configuration asset digest differs")
        content[relative] = value

    destination.mkdir(mode=0o700)
    os.chown(destination, uid, gid)
    for directory in sorted(config_directories):
        target_directory = destination / directory
        target_directory.mkdir(mode=0o700)
        os.chown(target_directory, uid, gid)
    for relative, value in content.items():
        target = destination / relative
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(value)
                stream.flush()
                os.fsync(stream.fileno())
        except BaseException:
            target.unlink(missing_ok=True)
            raise
        os.chown(target, uid, gid)


def copy_desktop_config_seed(
    seed: Path, destination: Path, role: str, uid: int = 1000, gid: int = 1000,
) -> None:
    """Overlay the exact reviewed Waybar profile into a newly copied config."""
    if role not in {"graphical-base", "hub-graphical"}:
        raise Refusal("desktop configuration role is unsupported")
    if not seed.is_dir() or seed.is_symlink():
        raise Refusal("desktop configuration seed is absent or unsafe")
    if {item.name for item in seed.iterdir()} != set(DESKTOP_CONFIG_ASSETS):
        raise Refusal("desktop configuration seed entries differ")
    content: dict[str, bytes] = {}
    for name, expected_digest in DESKTOP_CONFIG_ASSETS.items():
        source = seed / name
        descriptor = os.open(source, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            value = os.read(descriptor, MAX_GRAPHICAL_CONFIG_BYTES + 1)
            if os.read(descriptor, 1) or len(value) > MAX_GRAPHICAL_CONFIG_BYTES:
                raise Refusal("desktop configuration asset exceeds the size limit")
        finally:
            os.close(descriptor)
        if hashlib.sha256(value).hexdigest() != expected_digest:
            raise Refusal("desktop configuration asset digest differs")
        content[name] = value
    waybar = destination / "waybar"
    if not waybar.is_dir() or waybar.is_symlink():
        raise Refusal("Waybar destination is absent or unsafe")
    selected = "hub-config.json" if role == "hub-graphical" else "environment-config.json"
    for source_name, destination_name in ((selected, "config.json"), ("style.css", "style.css")):
        target = waybar / destination_name
        metadata = target.lstat()
        if not stat.S_ISREG(metadata.st_mode) or target.is_symlink():
            raise Refusal("Waybar destination asset is unsafe")
        temporary = target.with_name(f".{target.name}.desktop-essential-{os.getpid()}.tmp")
        descriptor = os.open(
            temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o600,
        )
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content[source_name])
                stream.flush()
                os.fsync(stream.fileno())
            os.chown(temporary, uid, gid)
            os.replace(temporary, target)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise


def copy_environment_shell_seed(
    seed: Path, user_home: Path, uid: int = 1000, gid: int = 1000,
) -> None:
    """Overlay the reviewed QuickShell desktop shared by Hub and environments."""
    if not seed.is_dir() or seed.is_symlink():
        raise Refusal("environment shell seed is absent or unsafe")

    expected_directories: set[str] = set()
    for relative in ENVIRONMENT_SHELL_ASSETS:
        parent = Path(relative).parent
        while parent != Path("."):
            expected_directories.add(parent.as_posix())
            parent = parent.parent
    expected_entries = set(ENVIRONMENT_SHELL_ASSETS) | expected_directories
    observed_entries: set[str] = set()
    for entry in seed.rglob("*"):
        relative = entry.relative_to(seed).as_posix()
        observed_entries.add(relative)
        metadata = entry.lstat()
        if relative in ENVIRONMENT_SHELL_ASSETS:
            if not stat.S_ISREG(metadata.st_mode):
                raise Refusal("environment shell asset is not a regular file")
        elif relative in expected_directories:
            if not stat.S_ISDIR(metadata.st_mode) or entry.is_symlink():
                raise Refusal("environment shell directory is unsafe")
        else:
            raise Refusal("environment shell seed contains an unapproved entry")
    if observed_entries != expected_entries:
        raise Refusal("environment shell seed is incomplete")

    content: dict[str, bytes] = {}
    for relative, expected_digest in ENVIRONMENT_SHELL_ASSETS.items():
        source = seed / relative
        size_limit = (
            MAX_WALLPAPER_BYTES
            if relative.startswith("apx/wallpapers/")
            else MAX_GRAPHICAL_CONFIG_BYTES
        )
        descriptor = os.open(source, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            value = os.read(descriptor, size_limit + 1)
            if os.read(descriptor, 1) or len(value) > size_limit:
                raise Refusal("environment shell asset exceeds the size limit")
        finally:
            os.close(descriptor)
        if hashlib.sha256(value).hexdigest() != expected_digest:
            raise Refusal("environment shell asset digest differs")
        content[relative] = value

    if not user_home.is_dir() or user_home.is_symlink():
        raise Refusal("environment home is absent or unsafe")
    targets: dict[str, Path] = {}
    for relative in ENVIRONMENT_SHELL_ASSETS:
        parts = Path(relative).parts
        if parts[0] == "local":
            targets[relative] = user_home / ".local" / Path(*parts[1:])
        else:
            targets[relative] = user_home / ".config" / relative

    # mkdir(parents=True) creates missing ancestors with the runner's root
    # ownership.  Include every directory below user_home explicitly so a
    # fresh Home does not leave ~/.local root-owned and prevent the desktop
    # user from creating ~/.local/state when QuickShell starts.
    directories: set[Path] = set()
    for target in targets.values():
        directory = target.parent
        while directory != user_home:
            directories.add(directory)
            directory = directory.parent
    for directory in sorted(directories, key=lambda item: len(item.parts)):
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        metadata = directory.lstat()
        if not stat.S_ISDIR(metadata.st_mode) or directory.is_symlink():
            raise Refusal("environment shell destination directory is unsafe")
        os.chmod(directory, 0o700)
        os.chown(directory, uid, gid)

    for relative, value in content.items():
        target = targets[relative]
        if target.exists() or target.is_symlink():
            metadata = target.lstat()
            if not stat.S_ISREG(metadata.st_mode) or target.is_symlink():
                raise Refusal("environment shell destination asset is unsafe")
        temporary = target.with_name(f".{target.name}.environment-shell-{os.getpid()}.tmp")
        mode = 0o755 if relative.startswith(("local/bin/", "local/libexec/")) else 0o600
        descriptor = os.open(
            temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, mode,
        )
        try:
            os.fchmod(descriptor, mode)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(value)
                stream.flush()
                os.fsync(stream.fileno())
            os.chown(temporary, uid, gid)
            os.replace(temporary, target)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise


def environment_dir(name: str) -> Path:
    return ENVIRONMENTS / validate_name(name)


def registration_path(name: str) -> Path:
    return environment_dir(name) / "registration.json"


def read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise Refusal(f"cannot read authoritative state: {error}") from error
    if not isinstance(value, dict):
        raise Refusal("authoritative state is not an object")
    return value


def atomic_json(path: Path, value: object, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(canonical(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


def append_event(operation: str, action: str, effect: str, status: str, **extra: object) -> None:
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    previous = "0" * 64
    if JOURNAL.exists():
        lines = JOURNAL.read_text().splitlines()
        if lines:
            previous_record = json.loads(lines[-1])
            previous = digest(previous_record)
    event = {
        "schema": 1,
        "operation": operation,
        "action": action,
        "effect": effect,
        "status": status,
        "at": now(),
        "previous": previous,
        **extra,
    }
    with JOURNAL.open("ab") as stream:
        stream.write(canonical(event))
        stream.flush()
        os.fsync(stream.fileno())


def admitted_release(role: str) -> Path:
    release = RELEASES / RELEASE_IDS[validate_role(role)] / "root"
    if not release.is_dir():
        raise Refusal(f"admitted {role} release is absent")
    result = run(["btrfs", "property", "get", "-ts", str(release), "ro"], capture=True)
    if "ro=true" not in result.stdout:
        raise Refusal("release root is not immutable")
    return release


def make_plan(action: str, name: str, role: str | None = None,
              update_policy: str = "follow-host", description: str = "",
              preset: str = "intermediate", modules: tuple[str, ...] | list[str] = ()) -> dict[str, object]:
    validate_name(name)
    generation = str(uuid.uuid4())
    if action == "create":
        validate_role_assignment(name, role or "")
        if update_policy not in {"follow-host", "excluded"}:
            raise Refusal("unsupported update policy")
        if len(description) > 120 or description != description.strip() \
                or any(ord(character) < 32 for character in description):
            raise Refusal("invalid Environment description")
        if environment_dir(name).exists():
            raise Refusal("Environment already exists")
        admitted_release(role or "")
        if role == "graphical-base":
            if not modules:
                from apx_environment_features import PRESETS
                modules = PRESETS["intermediate"]
            try:
                preset, modules = validate_selection(preset, modules)
            except ValueError as error:
                raise Refusal(str(error)) from error
    elif action == "destroy":
        generation = str(registration(name)["generation"])
    else:
        raise Refusal("unsupported plan family")
    plan: dict[str, object] = {
        "schema": 1,
        "action": action,
        "name": name,
        "generation": generation,
        "effects": list(EFFECTS[action]),
    }
    if role is not None:
        plan["role"] = role
        plan["update_policy"] = update_policy
        plan["description"] = description
        if role == "graphical-base":
            plan["desktop_preset"] = preset
            plan["desktop_modules"] = list(modules)
    identity = digest(plan)
    plan["digest"] = identity
    atomic_json(PLANS / f"{identity}.json", plan)
    return plan


def load_plan(identity: str, action: str) -> dict[str, object]:
    if not re.fullmatch(r"[0-9a-f]{64}", identity):
        raise Refusal("invalid plan digest")
    plan = read_json(PLANS / f"{identity}.json")
    claimed = plan.pop("digest", None)
    actual = digest(plan)
    plan["digest"] = claimed
    if claimed != identity or actual != identity or plan.get("action") != action:
        raise Refusal("plan identity or family mismatch")
    return plan


def registration(name: str) -> dict[str, object]:
    record = read_json(registration_path(name))
    if record.get("name") != name or record.get("state") not in {"stopped", "running"}:
        raise Refusal("invalid registration")
    validate_role_assignment(name, str(record.get("role", "")))
    return record


def machine(name: str) -> str:
    return f"apx-{validate_name(name)}"


def machine_running(name: str) -> bool:
    result = run(["machinectl", "show", machine(name), "--property=State", "--value"], check=False, capture=True)
    return result.returncode == 0 and result.stdout.strip() in {"running", "degraded"}


def create(plan_identity: str, approval: str) -> None:
    require_root()
    plan = load_plan(plan_identity, "create")
    name = str(plan["name"])
    role = str(plan["role"])
    validate_role_assignment(name, role)
    if approval != f"CREATE {name} AS {role}":
        raise Refusal("exact creation approval is absent")
    target = environment_dir(name)
    if target.exists():
        raise Refusal("Environment path already exists")
    verify_shared_storage_reserve()
    operation = str(uuid.uuid4())
    append_event(operation, "create", "operation", "started", name=name, plan=plan_identity)
    target.mkdir(mode=0o700)
    try:
        root = target / "root"
        append_event(operation, "create", "root", "started", name=name)
        run(["btrfs", "subvolume", "snapshot", str(admitted_release(role)), str(root)])
        apply_subvolume_storage_limit(root, ENVIRONMENT_STORAGE_LIMITS[role][0])
        append_event(operation, "create", "root", "complete", name=name)
        fault("root")

        home = target / "home"
        append_event(operation, "create", "home", "started", name=name)
        run(["btrfs", "subvolume", "create", str(home)])
        home.chmod(0o755)
        apply_subvolume_storage_limit(home, ENVIRONMENT_STORAGE_LIMITS[role][1])
        verify_shared_storage_reserve()
        user_home = home / "apx"
        user_home.mkdir(mode=0o700)
        os.chown(user_home, 1000, 1000)
        home_alias = home / "Home"
        home_alias.symlink_to("apx")
        skeleton = root / "etc/skel"
        if skeleton.is_dir() and not skeleton.is_symlink():
            for source in sorted(skeleton.iterdir()):
                metadata = source.lstat()
                if not stat.S_ISREG(metadata.st_mode) or source.is_symlink():
                    raise Refusal("release skeleton contains a non-regular entry")
                destination = user_home / source.name
                shutil.copy2(source, destination, follow_symlinks=False)
                os.chown(destination, 1000, 1000)
        append_event(operation, "create", "home", "complete", name=name)
        fault("home")

        append_event(operation, "create", "configure", "started", name=name)
        (root / "etc" / "hostname").write_text(machine(name) + "\n")
        (root / "etc" / "machine-id").write_text("")
        if role in {"graphical-base", "hub-graphical"}:
            seed = root / "usr/share/apx/config-seeds/hyprland-minimal-v2"
            destination = home / "apx/.config"
            copy_graphical_config_seed(seed, destination)
            copy_desktop_config_seed(DESKTOP_CONFIG_SEED, destination, role)
            copy_environment_shell_seed(ENVIRONMENT_SHELL_SEED, user_home)
            # Hide the internal USB bridge; the conditional bookmark exposes a real pen.
            fstab = root / "etc/fstab"
            if fstab.is_symlink():
                raise Refusal("Environment fstab is linked")
            bridge = "none /media/apx-usb none noauto,x-gvfs-hide 0 0"
            original_fstab = fstab.read_text() if fstab.exists() else ""
            if not any(line.split()[1:2] == ["/media/apx-usb"]
                       for line in original_fstab.splitlines() if not line.lstrip().startswith("#")):
                fstab.write_text(original_fstab.rstrip() + "\n" + bridge + "\n")
        if role in GRAPHICAL_ROLES | {"hub"}:
            install_flatpak_defaults(root)
        if role == "graphical-base":
            configure_environment_features(root, plan)
        if role == "hub":
            (root / "run" / "apx").mkdir(parents=True, exist_ok=True)
        append_event(operation, "create", "configure", "complete", name=name)
        fault("configure")

        record = {
            "schema": 1,
            "name": name,
            "role": role,
            "generation": plan["generation"],
            "release": RELEASE_IDS[role],
            "state": "stopped",
            "created_at": now(),
            "update_policy": plan.get("update_policy", "follow-host"),
        }
        if role == "graphical-base":
            record["desktop_preset"] = plan["desktop_preset"]
            record["desktop_modules"] = plan["desktop_modules"]
        if plan.get("description"):
            record["description"] = plan["description"]
        append_event(operation, "create", "publish", "started", name=name)
        atomic_json(registration_path(name), record)
        append_event(operation, "create", "publish", "complete", name=name)
        append_event(operation, "create", "operation", "complete", name=name)
    except BaseException:
        append_event(operation, "create", "operation", "uncertain", name=name)
        raise


def configure_environment_features(root: Path, plan: dict[str, object]) -> None:
    """Apply packages, APX password and explicitly opted-in face identity."""
    preset, modules = validate_selection(plan.get("desktop_preset"), plan.get("desktop_modules"))
    from apx_face_auth import load_identity, install_identity
    face_identity = load_identity(ENVIRONMENTS.parent / "face-auth-v1") if "desktop-integration" in modules else None
    feature_dir = root / "etc/apx"
    feature_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    atomic_json(feature_dir / "environment-features.json", {
        "schema": 1, "preset": preset, "modules": list(modules),
    }, 0o644)

    hub_shadow = ENVIRONMENTS / "hub/root/etc/shadow"
    target_shadow = root / "etc/shadow"
    source_lines = read_trusted_shadow(ENVIRONMENTS / "hub/root").splitlines()
    target_lines = read_trusted_shadow(root).splitlines()
    source = next((line.split(":", 2)[1] for line in source_lines if line.startswith("apx:")), None)
    if not source or source.startswith(("!", "*")):
        raise Refusal("Hub apx password is not enrolled")
    replaced = False
    for index, line in enumerate(target_lines):
        if line.startswith("apx:"):
            fields = line.split(":"); fields[1] = source
            target_lines[index] = ":".join(fields); replaced = True; break
    if not replaced:
        raise Refusal("Environment apx account is absent")
    write_trusted_shadow(root, "\n".join(target_lines) + "\n")

    # Every graphical-base role can expose a connector wired to the Host's
    # NVIDIA card, including the minimal desktop preset.
    packages = tuple(sorted(set(packages_for(modules)) | {
        "egl-gbm", "egl-wayland", "egl-wayland2", "egl-x11",
    } | ({"python-opencv", "cblas", "lapack"} if face_identity else set())))
    if packages:
        if any(package.startswith("lib32-") for package in packages):
            pacman_config = root / "etc/pacman.conf"
            metadata = pacman_config.lstat()
            content = pacman_config.read_text()
            disabled = "#[multilib]\n#Include = /etc/pacman.d/mirrorlist\n"
            enabled = "[multilib]\nInclude = /etc/pacman.d/mirrorlist\n"
            if pacman_config.is_symlink() or not pacman_config.is_file() \
                    or metadata.st_uid != 0 or metadata.st_gid != 0 or metadata.st_mode & 0o022 \
                    or (disabled not in content and enabled not in content):
                raise Refusal("Environment multilib configuration differs")
            if disabled in content:
                content = content.replace(disabled, enabled, 1)
                descriptor = os.open(pacman_config, os.O_WRONLY | os.O_TRUNC | os.O_NOFOLLOW)
                try:
                    os.write(descriptor, content.encode())
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
        run(["pacman", "--root", str(root), "--dbpath", str(root / "var/lib/pacman"),
             "--cachedir", "/var/cache/pacman/pkg", "--config", str(root / "etc/pacman.conf"),
             "--disable-sandbox", "--ignore", "nvidia-utils,lib32-nvidia-utils",
             "-Syu", "--needed", "--noconfirm", *packages])
    local_packages = set(local_packages_for(modules)) | {"nvidia-utils"}
    if face_identity:
        local_packages.update({"python-dlib", "howdy-apx"})
    # Howdy depends on the private CPU-only dlib artifact.
    for package in sorted(local_packages, key=lambda name: (name == "howdy-apx", name)):
        artifact = validated_local_package_artifact(package)
        if package == "nvidia-utils":
            module_version = host_nvidia_version()
            if not module_version or not artifact.name.startswith(f"nvidia-utils-{module_version}-"):
                raise Refusal("NVIDIA Environment artifact does not match the Host module")
        run(["pacman", "--root", str(root), "--dbpath", str(root / "var/lib/pacman"),
             "--cachedir", "/var/cache/pacman/pkg", "--config", str(root / "etc/pacman.conf"),
            "--disable-sandbox", "-U", "--needed", "--noconfirm", str(artifact)])
    if face_identity:
        install_identity(root, face_identity)


def host_nvidia_version() -> str:
    return Path("/sys/module/nvidia/version").read_text().strip()


def validated_local_package_artifact(package: str) -> Path:
    """Resolve one Host-owned, digest-pinned non-repository package."""
    manifest_name = LOCAL_PACKAGE_MANIFESTS.get(package)
    if manifest_name is None:
        raise Refusal("Environment local package is unsupported")
    directory = LOCAL_PACKAGE_ARTIFACTS
    manifest = directory / manifest_name
    for path, expected_directory in ((directory, True), (manifest, False)):
        try:
            metadata = path.lstat()
        except OSError as error:
            raise Refusal("Environment local package metadata is absent") from error
        if path.is_symlink() or (expected_directory and not stat.S_ISDIR(metadata.st_mode)) \
                or (not expected_directory and not stat.S_ISREG(metadata.st_mode)) \
                or (metadata.st_uid, metadata.st_gid) != (0, 0) or metadata.st_mode & 0o022:
            raise Refusal("Environment local package metadata is not Host-owned")
    try:
        record = json.loads(manifest.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise Refusal("Environment local package manifest is invalid") from error
    if type(record) is not dict or record.get("schema") != 1 \
            or record.get("package") != package:
        raise Refusal("Environment local package manifest is unsupported")
    filename = record.get("filename")
    digest = record.get("sha256")
    if type(filename) is not str or Path(filename).name != filename \
            or not filename.startswith(package + "-") or not filename.endswith(".pkg.tar.zst") \
            or type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise Refusal("Environment local package manifest fields are invalid")
    artifact = directory / filename
    try:
        metadata = artifact.lstat()
    except OSError as error:
        raise Refusal("Environment local package artifact is absent") from error
    if artifact.is_symlink() or not stat.S_ISREG(metadata.st_mode) \
            or (metadata.st_uid, metadata.st_gid) != (0, 0) or metadata.st_mode & 0o022 \
            or metadata.st_size <= 0 or metadata.st_size > 512 * 1024**2:
        raise Refusal("Environment local package artifact is not admitted")
    computed = hashlib.sha256()
    with artifact.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            computed.update(chunk)
    if computed.hexdigest() != digest:
        raise Refusal("Environment local package digest does not match")
    return artifact


def trusted_root_owner(root: Path) -> tuple[int, int]:
    """Resolve root ownership across stopped and private-user active roots."""
    container = root.parent
    container_metadata = container.lstat()
    root_metadata = root.lstat()
    etc_metadata = (root / "etc").lstat()
    if any(path.is_symlink() for path in (container, root, root / "etc")) \
            or not all(stat.S_ISDIR(value.st_mode) for value in (
                container_metadata, root_metadata, etc_metadata,
            )) \
            or (container_metadata.st_uid, container_metadata.st_gid) != (0, 0) \
            or container_metadata.st_mode & 0o022 \
            or (etc_metadata.st_uid, etc_metadata.st_gid) != (
                root_metadata.st_uid, root_metadata.st_gid,
            ) \
            or etc_metadata.st_mode & 0o022:
        raise Refusal("trusted password source is unavailable")
    return root_metadata.st_uid, root_metadata.st_gid


def open_trusted_shadow(root: Path, flags: int) -> int:
    owner = trusted_root_owner(root)
    path = root / "etc/shadow"
    try:
        descriptor = os.open(path, flags | os.O_NOFOLLOW | os.O_CLOEXEC)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) \
                or (metadata.st_uid, metadata.st_gid) != owner \
                or stat.S_IMODE(metadata.st_mode) != 0o600 \
                or metadata.st_size > 65536:
            raise Refusal("trusted password source is unavailable")
        return descriptor
    except BaseException:
        if "descriptor" in locals():
            os.close(descriptor)
        raise


def read_trusted_shadow(root: Path) -> str:
    descriptor = open_trusted_shadow(root, os.O_RDONLY)
    try:
        value = bytearray()
        while len(value) <= 65536:
            chunk = os.read(descriptor, min(8192, 65537 - len(value)))
            if not chunk:
                break
            value.extend(chunk)
        if len(value) > 65536:
            raise Refusal("trusted password source is unavailable")
        return value.decode()
    except (UnicodeDecodeError, OSError) as error:
        raise Refusal("trusted password source is unavailable") from error
    finally:
        os.close(descriptor)


def write_trusted_shadow(root: Path, value: str) -> None:
    encoded = value.encode()
    if len(encoded) > 65536:
        raise Refusal("trusted password target is unavailable")
    descriptor = open_trusted_shadow(root, os.O_WRONLY)
    try:
        os.ftruncate(descriptor, 0)
        view = memoryview(encoded)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short shadow write")
            view = view[written:]
        os.fsync(descriptor)
    except OSError as error:
        raise Refusal("trusted password target is unavailable") from error
    finally:
        os.close(descriptor)


def fault(effect: str) -> None:
    if os.environ.get("APX_LAB_FAULT_AFTER") == effect:
        os._exit(86)


def verify_shared_storage_reserve() -> None:
    """Refuse new growth when the Host recovery reserve would be crossed."""
    stats = os.statvfs(STATE)
    available = stats.f_bavail * stats.f_frsize
    if available < HOST_STORAGE_RESERVE_BYTES:
        raise Refusal("shared Environment pool reached the protected Host reserve")


def apply_subvolume_storage_limit(path: Path, limit: str) -> None:
    """Bound both total referenced and exclusive growth for one Environment volume."""
    if not re.fullmatch(r"[1-9][0-9]*G", limit):
        raise Refusal("Environment storage limit is malformed")
    run(["btrfs", "qgroup", "limit", limit, str(path)])
    run(["btrfs", "qgroup", "limit", "-e", limit, str(path)])


def start(name: str) -> None:
    require_root()
    record = registration(name)
    if record.get("role") not in HEADLESS_START_ROLES:
        raise Refusal("graphical Environment activation requires the separate H0 device and recovery adapter")
    if machine_running(name):
        print(f"{name}: already running")
        return
    target = environment_dir(name)
    unit = f"apx-environment-{name}.service"
    cpu_quota, memory_high, memory_max, tasks_max = ENVIRONMENT_RUNTIME_LIMITS[str(record["role"])]
    command = [
        "systemd-run", "--unit", unit, "--collect", "--property=Delegate=yes",
        "--property=KillMode=mixed", "--",
        "systemd-nspawn", "--quiet", "--keep-unit", "--boot",
        f"--machine={machine(name)}", f"--directory={target / 'root'}",
        "--private-users=pick", "--private-users-ownership=chown",
        "--private-network", "--network-veth", "--link-journal=no", "--settings=no",
        f"--bind={target / 'home'}:/home:idmap",
    ]
    command[6:6] = [
        f"--property=CPUQuota={cpu_quota}", "--property=CPUWeight=200",
        "--property=IOWeight=200", f"--property=MemoryHigh={memory_high}",
        f"--property=MemoryMax={memory_max}", f"--property=TasksMax={tasks_max}",
    ]
    if record["role"] == "hub":
        executor_socket = Path("/run/apx/executor.sock")
        if not executor_socket.is_socket():
            raise Refusal("Hub executor endpoint is unavailable")
        command.append("--bind-ro=/run/apx/executor.sock:/run/apx/executor.sock")
        run([NETWORK_ADAPTER, "apply", "--environment", "hub"])
    operation = str(uuid.uuid4())
    append_event(operation, "activate", "runtime", "started", name=name)
    try:
        run(command, capture=True)
    except BaseException:
        if record["role"] == "hub":
            run([NETWORK_ADAPTER, "remove", "--environment", "hub"], check=False)
        raise
    for _ in range(100):
        if machine_running(name):
            break
        import time
        time.sleep(0.1)
    if not machine_running(name):
        append_event(operation, "activate", "runtime", "uncertain", name=name)
        if record["role"] == "hub":
            run([NETWORK_ADAPTER, "remove", "--environment", "hub"], check=False)
        raise Refusal("Environment did not register as running")
    for _ in range(300):
        readiness = run(
            ["systemctl", "-M", machine(name), "is-system-running"],
            check=False,
            capture=True,
        )
        if readiness.stdout.strip() in {"running", "degraded"}:
            break
        import time
        time.sleep(0.1)
    else:
        append_event(operation, "activate", "runtime", "uncertain", name=name)
        run(["systemctl", "stop", unit], check=False, capture=True)
        if record["role"] == "hub":
            run([NETWORK_ADAPTER, "remove", "--environment", "hub"], check=False)
        raise Refusal("Environment registered but did not reach a usable system state")
    record["state"] = "running"
    atomic_json(registration_path(name), record)
    append_event(operation, "activate", "runtime", "complete", name=name)


def stop(name: str) -> None:
    require_root()
    record = registration(name)
    operation = str(uuid.uuid4())
    append_event(operation, "stop", "runtime", "started", name=name)
    if machine_running(name):
        run(["machinectl", "poweroff", machine(name)], check=False, capture=True)
        for _ in range(200):
            if not machine_running(name):
                break
            import time
            time.sleep(0.1)
    if machine_running(name):
        append_event(operation, "stop", "runtime", "uncertain", name=name)
        raise Refusal("runtime residue remains")
    run(
        ["systemctl", "reset-failed", f"apx-environment-{name}.service"],
        check=False, capture=True,
    )
    if record.get("role") == "hub":
        run([NETWORK_ADAPTER, "remove", "--environment", "hub"], check=False)
    record["state"] = "stopped"
    atomic_json(registration_path(name), record)
    append_event(operation, "stop", "runtime", "complete", name=name)


def shell(name: str, *, recovery_root: bool = False) -> None:
    require_root()
    registration(name)
    if not machine_running(name):
        start(name)
    user = "root" if recovery_root else "apx"
    border = "=" * 72
    print(f"\n{border}")
    print(f"APX >>> ESTÁS A ENTRAR NO ENVIRONMENT '{name}' COMO '{user}'")
    print("APX >>> O PRÓXIMO PROMPT NÃO É O HOST. Alterações ficam neste Environment.")
    if recovery_root:
        print("APX >>> MODO ROOT DE RECUPERAÇÃO: usa apenas para reparar este Environment.")
    print(f"{border}\n", flush=True)
    result: subprocess.CompletedProcess[str] | None = None
    try:
        result = run(["machinectl", "shell", f"{user}@{machine(name)}"], check=False)
    finally:
        print(f"\n{border}")
        print(f"APX <<< SAÍSTE DO ENVIRONMENT '{name}'")
        print("APX <<< ESTÁS DE VOLTA AO HOST 'apx-host' COMO ROOT.")
        print("APX <<< Confirma o prompt antes de executar o próximo comando.")
        print(f"{border}\n", flush=True)
    if result is None or result.returncode:
        raise Refusal("Environment terminal session ended with an error")


def local_admin_state(target: str) -> tuple[str, str, str, str, str]:
    """Observe fixed enrollment facts without trusting machinectl's exit status."""
    observe = (
        "set -eu; "
        "marker=absent; test -e /etc/apx/local-admin-v1 && marker=present; "
        "sudo=absent; test -x /usr/bin/sudo && sudo=present; "
        "set -- $(/usr/bin/passwd -S apx); password=$2; "
        "wheel=absent; "
        "/usr/bin/id -nG apx | /usr/bin/tr ' ' '\\n' "
        "| /usr/bin/grep -Fxq wheel && wheel=present; "
        "policy=absent; "
        "if test -e /etc/sudoers.d/10-apx-local-admin; then "
        " policy=invalid; "
        " if test \"$(/usr/bin/stat -c '%a:%u:%g' "
        "/etc/sudoers.d/10-apx-local-admin)\" = '440:0:0' "
        " && /usr/bin/grep -Fxq '%wheel ALL=(ALL:ALL) ALL' "
        "/etc/sudoers.d/10-apx-local-admin "
        " && /usr/bin/grep -Fxq 'apx ALL=(ALL:ALL) ALL' "
        "/etc/sudoers.d/10-apx-local-admin; then policy=ready; fi; "
        "fi; "
        "/usr/bin/printf 'APX_LOCAL_ADMIN_V1:%s:%s:%s:%s:%s\\n' "
        "\"$marker\" \"$sudo\" \"$password\" \"$wheel\" \"$policy\""
    )
    result = run(
        ["machinectl", "shell", f"root@{target}", "/usr/bin/bash", "-lc", observe],
        check=False, capture=True,
    )
    prefix = "APX_LOCAL_ADMIN_V1:"
    lines = [line for line in result.stdout.splitlines() if line.startswith(prefix)]
    if len(lines) != 1:
        raise Refusal("Environment local administrator state is absent or ambiguous")
    fields = tuple(lines[0][len(prefix):].split(":"))
    if len(fields) != 5:
        raise Refusal("Environment local administrator state is malformed")
    marker, sudo, password, wheel, policy = fields
    if marker not in {"absent", "present"} \
            or sudo not in {"absent", "present"} \
            or password not in {"L", "P", "NP"} \
            or wheel not in {"absent", "present"} \
            or policy not in {"absent", "invalid", "ready"}:
        raise Refusal("Environment local administrator state contains an unknown value")
    return marker, sudo, password, wheel, policy


def enroll_local_admin(name: str) -> None:
    """Enroll one Environment-local password without copying a Host secret."""
    require_root()
    record = registration(name)
    if not machine_running(name):
        if record.get("role") in HEADLESS_START_ROLES:
            start(name)
        else:
            raise Refusal("start the graphical Environment before enrolling its local administrator")
    target = machine(name)
    marker, sudo, password, wheel, policy = local_admin_state(target)
    if sudo != "present":
        raise Refusal("Environment release does not contain sudo")
    if (marker, password, wheel, policy) == ("present", "P", "present", "ready"):
        raise Refusal("Environment local administrator is already enrolled")
    if marker == "present":
        raise Refusal("Environment local administrator marker exists but enrollment is incomplete")
    fixed_prepare = (
        "set -eu; "
        "/usr/bin/usermod -aG wheel apx; "
        "/usr/bin/install -d -m 0755 /etc/apx /etc/sudoers.d; "
        "/usr/bin/printf '%s\\n' '%wheel ALL=(ALL:ALL) ALL' "
        "'apx ALL=(ALL:ALL) ALL' "
        "| /usr/bin/install -m 0440 /dev/stdin /etc/sudoers.d/10-apx-local-admin"
    )
    run(["machinectl", "shell", f"root@{target}", "/usr/bin/bash", "-lc", fixed_prepare])
    print(f"Define agora uma palavra-passe exclusiva do Environment {name} para o utilizador apx.")
    run(["machinectl", "shell", f"root@{target}", "/usr/bin/passwd", "apx"])
    marker, sudo, password, wheel, policy = local_admin_state(target)
    if (marker, sudo, password, wheel, policy) != (
        "absent", "present", "P", "present", "ready"
    ):
        raise Refusal("password enrollment did not complete; no enrollment marker was written")
    run(["machinectl", "shell", f"root@{target}", "/usr/bin/touch", LOCAL_ADMIN_MARKER])
    marker, sudo, password, wheel, policy = local_admin_state(target)
    if (marker, sudo, password, wheel, policy) != (
        "present", "present", "P", "present", "ready"
    ):
        raise Refusal("Environment local administrator final state differs")
    print(f"Environment {name} local administrator enrolled; the Host password was not requested or copied.")


def destroy(plan_identity: str, approval: str) -> None:
    require_root()
    with local_recovery_lock():
        _destroy_locked(plan_identity, approval)


def _destroy_locked(plan_identity: str, approval: str) -> None:
    plan = load_plan(plan_identity, "destroy")
    name = str(plan["name"])
    if approval != f"DESTROY {name}":
        raise Refusal("exact destruction approval is absent")
    record = registration(name)
    if plan.get("generation") != record.get("generation"):
        raise Refusal("destruction plan generation is stale")
    if plan.get("effects") != list(EFFECTS["destroy"]):
        raise Refusal("destruction plan effects differ from complete purge policy")
    target = environment_dir(name)
    metadata = target.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode) \
            or metadata.st_uid != 0 or metadata.st_gid != 0 \
            or stat.S_IMODE(metadata.st_mode) != 0o700:
        raise Refusal("Environment container is not a trusted root-owned directory")
    operation = str(uuid.uuid4())
    rollbacks = environment_update_rollbacks(name)
    local_copies = local_recovery_snapshots(name)
    append_event(operation, "destroy", "operation", "started", name=name, plan=plan_identity)
    stop(name)
    for path in rollbacks:
        delete_subvolume_tree(path)
    append_event(operation, "destroy", "purge-update-rollbacks", "complete", name=name, removed=len(rollbacks))
    for effect, count in purge_environment_copies(name):
        append_event(operation, "destroy", effect, "complete", name=name, removed=count)
    removed_backups = purge_environment_backups(name)
    append_event(
        operation, "destroy", "purge-backups", "complete", name=name,
        removed=removed_backups,
    )
    purge_local_recovery(name, local_copies)
    append_event(operation, "destroy", "purge-local-recovery", "complete", name=name, removed=len(local_copies))
    for label in ("home", "root"):
        path = target / label
        append_event(operation, "destroy", f"remove-{label}", "started", name=name)
        delete_subvolume_tree(path)
        append_event(operation, "destroy", f"remove-{label}", "complete", name=name)
    record_path = registration_path(name)
    append_event(operation, "destroy", "unpublish", "started", name=name)
    record_path.unlink()
    append_event(operation, "destroy", "unpublish", "complete", name=name)
    append_event(operation, "destroy", "purge-metadata", "started", name=name)
    shutil.rmtree(target)
    append_event(operation, "destroy", "purge-metadata", "complete", name=name)
    removed_plans = purge_environment_plans(name)
    append_event(
        operation, "destroy", "purge-plans", "complete", name=name,
        removed=removed_plans,
    )
    append_event(operation, "destroy", "operation", "complete", name=name)


def delete_subvolume_tree(path: Path) -> None:
    if not path.exists():
        return
    run(["btrfs", "subvolume", "delete", "-R", str(path)])


UUID_COMPONENT = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


@contextlib.contextmanager
def local_recovery_lock():
    """Shared with apx-local-snapshots: no backup can race a deletion."""
    fd = os.open(RECOVERY_LOCK, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or info.st_mode & 0o022:
            raise Refusal("local recovery lock is not trusted")
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def trusted_recovery_directory(path: Path) -> None:
    # Check all ancestors too; resolving a symlink before checking is unsafe.
    for item in reversed((path, *path.parents)):
        info = item.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or info.st_mode & 0o022:
            # /tmp is allowed only as an ancestor of isolated test fixtures.
            if item == Path('/tmp') and stat.S_ISDIR(info.st_mode) and info.st_mode & stat.S_ISVTX:
                continue
            raise Refusal(f"local recovery directory is not trusted: {item}")


def local_recovery_snapshots(name: str) -> tuple[Path, ...]:
    """Admit the exact layout owned by apx-local-snapshots, all generations."""
    validate_name(name)
    if not LOCAL_RECOVERY.exists() and not LOCAL_RECOVERY.is_symlink():
        return ()
    trusted_recovery_directory(LOCAL_RECOVERY)
    found = []
    for label in ('root', 'home'):
        parent = LOCAL_RECOVERY / f'environment-{name}-{label}'
        if not parent.exists() and not parent.is_symlink():
            continue
        trusted_recovery_directory(parent)
        for path in sorted(parent.iterdir()):
            if not re.fullmatch(r'[0-9]{8}T[0-9]{6}Z', path.name) or path.is_symlink() or not path.is_dir():
                raise Refusal(f"unrecognized local recovery copy: {path}")
            # A plain directory must never be accepted as a Btrfs snapshot.
            run(['btrfs', 'subvolume', 'show', str(path)])
            found.append(path)
    # Btrfs snapshots are non-recursive. On the pilot /var/lib/apx is a separate
    # subvolume. If another installation has mixed APX state in system backups,
    # refuse before stopping/unpublishing instead of falsely reporting deletion.
    system = LOCAL_RECOVERY / 'system'
    if system.exists() or system.is_symlink():
        trusted_recovery_directory(system)
        for snapshot in sorted(system.iterdir()):
            trusted_recovery_directory(snapshot)
            state = snapshot / 'var/lib/apx'
            # Check intermediate components without following backup symlinks.
            for part in (snapshot / 'var', snapshot / 'var/lib', state):
                if part.is_symlink():
                    raise Refusal('mixed system backup has a symlink in its APX state path')
            if state.exists() and any(state.iterdir()):
                raise Refusal('system recovery snapshot contains mixed APX state; purge its Environment copies before deletion')
    return tuple(found)


def purge_local_recovery(name: str, copies: tuple[Path, ...]) -> None:
    for path in copies:
        delete_subvolume_tree(path)
        if path.exists() or path.is_symlink():
            raise Refusal('local recovery snapshot remained after deletion')
    for label in ('root', 'home'):
        parent = LOCAL_RECOVERY / f'environment-{name}-{label}'
        if parent.exists():
            parent.rmdir()  # Unexpected new content fails closed.
    if local_recovery_snapshots(name):
        raise Refusal('local recovery copies remain')


def environment_update_rollbacks(name: str) -> tuple[Path, ...]:
    """Admit only exact target snapshots in journalled update operation layouts."""
    validate_name(name)
    found: list[Path] = []
    operation_pattern = re.compile(r"[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}")
    for base, coordinated in ((STATE / "environment-updates-v1", False),
                              (STATE / "coordinated-updates-v1", True)):
        operations = base / "operations" if coordinated else base
        if not operations.exists():
            continue
        if base.is_symlink() or operations.is_symlink():
            raise Refusal("update operation directory is a symlink")
        for directory in sorted(operations.iterdir()):
            if not operation_pattern.fullmatch(directory.name):
                continue
            if directory.is_symlink() or not directory.is_dir():
                raise Refusal("update operation has an unexpected type")
            rollback = base / "rollbacks" / directory.name if coordinated else directory / "rollback"
            if not rollback.exists():
                continue
            if rollback.is_symlink() or rollback.parent.is_symlink():
                raise Refusal("update rollback directory is a symlink")
            candidates = [rollback / (name + "-" + part) for part in ("root", "home")]
            if not any(path.exists() or path.is_symlink() for path in candidates):
                continue
            plan_path = directory / ("approved-plan.json" if coordinated else "plan.json")
            for evidence in (plan_path, directory / "status.json"):
                info = evidence.lstat()
                if evidence.is_symlink() or not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or info.st_mode & 0o022:
                    raise Refusal("update rollback evidence is not trusted")
            plan = read_json(plan_path)
            targets = plan.get("targets", [])
            if not any(isinstance(target, dict) and target.get("name") == name
                       and (not coordinated or target.get("kind") == "environment") for target in targets):
                raise Refusal("rollback target is not identified by its update plan")
            status = read_json(directory / "status.json")
            if status.get("state") not in {"complete", "failed", "awaiting-hub"}:
                raise Refusal("update operation may still be using this rollback")
            for path in candidates:
                if path.is_symlink():
                    raise Refusal("rollback snapshot is a symlink")
                if path.exists():
                    if not path.is_dir():
                        raise Refusal("rollback snapshot is not a directory")
                    found.append(path)
    return tuple(found)


def _remove_exact_copy(path: Path, *, snapshot: bool) -> None:
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        path.unlink()
        return
    if snapshot:
        for label in ("home", "root"):
            delete_subvolume_tree(path / label)
    shutil.rmtree(path)


def purge_environment_copies(name: str) -> tuple[tuple[str, int], ...]:
    """Delete every APX snapshot/archive generation for one logical name."""
    validate_name(name)
    snapshot_name = re.compile(
        rf"{re.escape(name)}-{UUID_COMPONENT}-[0-9]{{8}}T[0-9]{{6}}Z"
    )
    archive_name = re.compile(
        rf"archive-{re.escape(name)}-{UUID_COMPONENT}-{UUID_COMPONENT}"
    )
    counts: list[tuple[str, int]] = []
    for parent, pattern, effect, is_snapshot in (
        (SNAPSHOTS, snapshot_name, "purge-snapshots", True),
        (ARCHIVES, archive_name, "purge-archives", False),
    ):
        removed = 0
        if parent.exists():
            for path in sorted(parent.iterdir()):
                if pattern.fullmatch(path.name):
                    _remove_exact_copy(path, snapshot=is_snapshot)
                    removed += 1
        counts.append((effect, removed))
    return tuple(counts)


def purge_environment_plans(name: str) -> int:
    """Remove stored operation plans that identify the deleted Environment."""
    validate_name(name)
    removed = 0
    if not PLANS.exists():
        return removed
    for path in sorted(PLANS.glob("*.json")):
        if re.fullmatch(r"[0-9a-f]{64}\.json", path.name) is None:
            continue
        try:
            value = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict) and value.get("name") == name:
            path.unlink()
            removed += 1
    return removed


def purge_environment_backups(name: str) -> int:
    """Remove legacy Host maintenance copies explicitly named for the target."""
    validate_name(name)
    if not BACKUPS.exists():
        return 0
    removed = 0
    # Deployment backups store numbered files, with identity in their manifest.
    # Delete the saved copy, never the original target named by the manifest.
    prefix = str(ENVIRONMENTS / name) + "/"
    for manifest in sorted(BACKUPS.glob("*/manifest.json")):
        if manifest.is_symlink() or manifest.parent.is_symlink():
            raise Refusal("backup manifest is a symlink")
        try:
            entries = json.loads(manifest.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(entries, list):
            continue
        owned = [entry for entry in entries if isinstance(entry, dict)
                 and isinstance(entry.get("target"), str) and entry["target"].startswith(prefix)]
        copies: list[Path] = []
        for entry in owned:
            saved = entry.get("backup")
            if saved is None:
                continue
            path = Path(saved)
            if not path.is_absolute() or path.parent != manifest.parent:
                raise Refusal("saved backup is outside its manifest directory")
            if path.exists() and not path.is_file() and not path.is_symlink():
                raise Refusal("saved configuration backup has an unexpected type")
            copies.append(path)
        for path in copies:
            if path.exists() or path.is_symlink():
                path.unlink(); removed += 1
        if owned:
            atomic_json(manifest, [entry for entry in entries if entry not in owned])
            for filename in ("records.json", "packages.json"):
                evidence = manifest.parent / filename
                if evidence.exists():
                    if evidence.is_symlink():
                        raise Refusal("backup inventory is a symlink")
                    value = json.loads(evidence.read_text())
                    if isinstance(value, dict) and name in value:
                        value.pop(name); atomic_json(evidence, value)
    exact_names = {name, f"{name}-shell.qml"}
    candidates = sorted(
        (path for path in BACKUPS.rglob("*") if path.name in exact_names),
        key=lambda path: len(path.parts), reverse=True,
    )
    for path in candidates:
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
            shutil.rmtree(path)
        else:
            path.unlink()
        removed += 1
    return removed


def snapshot(name: str) -> str:
    require_root()
    record = registration(name)
    if machine_running(name):
        raise Refusal("snapshot requires a stopped Environment")
    identity = f"{name}-{record['generation']}-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    target = SNAPSHOTS / identity
    target.mkdir(parents=True)
    run(["btrfs", "subvolume", "snapshot", "-r", str(environment_dir(name) / "root"), str(target / "root")])
    run(["btrfs", "subvolume", "snapshot", "-r", str(environment_dir(name) / "home"), str(target / "home")])
    manifest = {"schema": 1, "snapshot": identity, "name": name, "generation": record["generation"], "created_at": now()}
    atomic_json(target / "manifest.json", manifest, 0o400)
    append_event(str(uuid.uuid4()), "snapshot", "publish", "complete", name=name, snapshot=identity)
    print(identity)
    return identity


def archive(name: str) -> str:
    require_root()
    record = registration(name)
    if machine_running(name):
        raise Refusal("archive requires a stopped Environment")
    snapshot_identity = snapshot(name)
    snapshot_dir = SNAPSHOTS / snapshot_identity
    archive_identity = f"archive-{name}-{record['generation']}-{uuid.uuid4()}"
    target = ARCHIVES / archive_identity
    target.mkdir(parents=True, mode=0o700)
    operation = str(uuid.uuid4())
    append_event(operation, "archive", "streams", "started", name=name, archive=archive_identity)
    hashes: dict[str, str] = {}
    for label in ("root", "home"):
        output = target / f"{label}.btrfs.zst"
        sender = subprocess.Popen(["btrfs", "send", str(snapshot_dir / label)], stdout=subprocess.PIPE)
        assert sender.stdout is not None
        compressor = subprocess.run(["zstd", "-q", "-T0", "-o", str(output)], stdin=sender.stdout)
        sender.stdout.close()
        sender_result = sender.wait()
        if sender_result != 0 or compressor.returncode != 0:
            append_event(operation, "archive", "streams", "uncertain", name=name, archive=archive_identity)
            raise Refusal("archive stream creation failed")
        hashes[label] = hashlib.sha256(output.read_bytes()).hexdigest()
    manifest = {
        "schema": 1,
        "archive": archive_identity,
        "source_name": name,
        "source_generation": record["generation"],
        "role": record["role"],
        "release": record["release"],
        "snapshot": snapshot_identity,
        "streams": hashes,
        "created_at": now(),
    }
    atomic_json(target / "manifest.json", manifest, 0o400)
    append_event(operation, "archive", "publish", "complete", name=name, archive=archive_identity)
    print(archive_identity)
    return archive_identity


def validate_archive(identity: str) -> Path:
    if not re.fullmatch(r"archive-[a-z0-9-]{1,160}", identity):
        raise Refusal("invalid archive identity")
    path = ARCHIVES / identity
    manifest = read_json(path / "manifest.json")
    if manifest.get("archive") != identity or set(manifest.get("streams", {})) != {"root", "home"}:
        raise Refusal("archive manifest mismatch")
    for label in ("root", "home"):
        stream = path / f"{label}.btrfs.zst"
        if not stream.is_file() or hashlib.sha256(stream.read_bytes()).hexdigest() != manifest["streams"][label]:
            raise Refusal("archive stream identity mismatch")
    return path


def restore(archive_identity: str, name: str, approval: str) -> None:
    require_root()
    validate_name(name)
    if approval != f"RESTORE {archive_identity} AS {name}":
        raise Refusal("exact restore approval is absent")
    if environment_dir(name).exists():
        raise Refusal("restore destination already exists")
    archive_path = validate_archive(archive_identity)
    manifest = read_json(archive_path / "manifest.json")
    validate_role_assignment(name, str(manifest.get("role", "")))
    target = environment_dir(name)
    target.mkdir(mode=0o700)
    operation = str(uuid.uuid4())
    append_event(operation, "restore", "operation", "started", name=name, archive=archive_identity)
    try:
        for label in ("root", "home"):
            stream = subprocess.Popen(["zstd", "-q", "-d", "-c", str(archive_path / f"{label}.btrfs.zst")], stdout=subprocess.PIPE)
            assert stream.stdout is not None
            receiver = subprocess.run(["btrfs", "receive", str(target)], stdin=stream.stdout, capture_output=True, text=True)
            stream.stdout.close()
            stream_result = stream.wait()
            if stream_result != 0 or receiver.returncode != 0:
                raise Refusal(f"restore receive failed: {receiver.stderr.strip()}")
            run(["btrfs", "property", "set", "-f", "-ts", str(target / label), "ro", "false"])
        verify_shared_storage_reserve()
        root = target / "root"
        (root / "etc" / "hostname").write_text(machine(name) + "\n")
        (root / "etc" / "machine-id").write_text("")
        record = {
            "schema": 1,
            "name": name,
            "role": manifest["role"],
            "generation": str(uuid.uuid4()),
            "release": manifest["release"],
            "state": "stopped",
            "created_at": now(),
            "restored_from": archive_identity,
        }
        atomic_json(registration_path(name), record)
        append_event(operation, "restore", "operation", "complete", name=name, archive=archive_identity)
    except BaseException:
        append_event(operation, "restore", "operation", "uncertain", name=name, archive=archive_identity)
        raise


def list_environments(as_json: bool) -> None:
    values: list[dict[str, object]] = []
    if ENVIRONMENTS.exists():
        for child in sorted(ENVIRONMENTS.iterdir()):
            if not NAME_RE.fullmatch(child.name) or not (child / "registration.json").is_file():
                continue
            record = registration(child.name)
            record = {**record, "observed_running": machine_running(child.name)}
            values.append(record)
    if as_json:
        print(json.dumps(values, sort_keys=True, indent=2))
    elif not values:
        print("No APX Environments are registered.")
    else:
        for value in values:
            print(f"{value['name']}\t{value['role']}\t{value['state']}\t{value['generation']}")


def status() -> None:
    failures = run(["systemctl", "--failed", "--no-legend"], check=False, capture=True).stdout.strip()
    print("APX disposable headless runtime")
    print(f"state={STATE} filesystem={run(['findmnt', '-n', '-T', str(STATE), '-o', 'FSTYPE'], capture=True).stdout.strip()}")
    print(f"host_system={'healthy' if not failures else 'degraded'}")
    list_environments(False)


def recover() -> None:
    require_root()
    uncertain: set[str] = set()
    if JOURNAL.exists():
        operations: dict[str, str] = {}
        for line in JOURNAL.read_text().splitlines():
            event = json.loads(line)
            if event.get("effect") == "operation":
                operations[str(event["operation"])] = str(event["status"])
        uncertain = {operation for operation, state in operations.items() if state != "complete"}
    print(json.dumps({"uncertain_operations": sorted(uncertain), "policy": "preserve-and-inspect"}, indent=2))


def recover_unpublished(name: str, approval: str) -> None:
    require_root()
    with local_recovery_lock():
        _recover_unpublished_locked(name, approval)


def _recover_unpublished_locked(name: str, approval: str) -> None:
    validate_name(name)
    if approval != f"CLEAN UNPUBLISHED {name}":
        raise Refusal("exact recovery cleanup approval is absent")
    target = environment_dir(name)
    if registration_path(name).exists() or machine_running(name):
        raise Refusal("recovery target is published or running")
    operation: str | None = None
    action: str | None = None
    if JOURNAL.exists():
        for line in reversed(JOURNAL.read_text().splitlines()):
            event = json.loads(line)
            if (
                event.get("name") == name
                and event.get("action") in {"create", "restore"}
                and event.get("effect") == "operation"
                and event.get("status") in {"started", "uncertain"}
            ):
                operation = str(event["operation"])
                action = str(event["action"])
                break
    if operation is None:
        raise Refusal("no matching uncertain unpublished operation")
    copies = local_recovery_snapshots(name)
    purge_local_recovery(name, copies)
    if not target.exists():
        append_event(
            operation, action or "recovery", "operation", "complete", name=name,
            recovery="confirmed-already-absent",
        )
        return
    if not target.is_dir():
        raise Refusal("recovery target has an unexpected filesystem type")
    for label in ("home", "root"):
        delete_subvolume_tree(target / label)
    remaining = list(target.iterdir())
    if remaining:
        raise Refusal("unrecognized recovery content is preserved")
    target.rmdir()
    append_event(operation, action or "recovery", "operation", "complete", name=name, recovery="approved-clean-unpublished")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="apx")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    commands.add_parser("recovery-status")
    recovery_clean = commands.add_parser("recovery-clean-unpublished")
    recovery_clean.add_argument("name")
    recovery_clean.add_argument("--approve", required=True)
    environment = commands.add_parser("environment")
    sub = environment.add_subparsers(dest="environment_command", required=True)
    listing = sub.add_parser("list")
    listing.add_argument("--json", action="store_true")
    create_plan = sub.add_parser("create-plan")
    create_plan.add_argument("name")
    create_plan.add_argument("--role", required=True, choices=sorted(ROLES))
    create_plan.add_argument("--exclude-host-updates", action="store_true",
                             help="opt out of coordinated Host update plans")
    create_plan.add_argument("--description", default="")
    create_plan.add_argument("--desktop-preset", default="intermediate",
                             choices=("basic", "intermediate", "complete"))
    create_plan.add_argument("--desktop-modules", default="")
    create_apply = sub.add_parser("create")
    create_apply.add_argument("--plan", required=True)
    create_apply.add_argument("--approve", required=True)
    for command in ("start", "stop", "shell", "shell-root", "snapshot", "archive",
                    "enroll-local-admin"):
        item = sub.add_parser(command)
        item.add_argument("name")
    destroy_plan = sub.add_parser("destroy-plan")
    destroy_plan.add_argument("name")
    destroy_apply = sub.add_parser("destroy")
    destroy_apply.add_argument("--plan", required=True)
    destroy_apply.add_argument("--approve", required=True)
    restore_apply = sub.add_parser("restore")
    restore_apply.add_argument("--archive", required=True)
    restore_apply.add_argument("--name", required=True)
    restore_apply.add_argument("--approve", required=True)
    return root


def main() -> int:
    arguments = parser().parse_args()
    if arguments.command == "status":
        status()
    elif arguments.command == "recovery-status":
        recover()
    elif arguments.command == "recovery-clean-unpublished":
        recover_unpublished(arguments.name, arguments.approve)
    elif arguments.environment_command == "list":
        list_environments(arguments.json)
    elif arguments.environment_command == "create-plan":
        policy = "excluded" if arguments.exclude_host_updates else "follow-host"
        print(json.dumps(make_plan("create", arguments.name, arguments.role, policy,
                                   arguments.description, arguments.desktop_preset,
                                   tuple(filter(None, arguments.desktop_modules.split(",")))),
                         sort_keys=True, indent=2))
    elif arguments.environment_command == "create":
        create(arguments.plan, arguments.approve)
    elif arguments.environment_command == "start":
        start(arguments.name)
    elif arguments.environment_command == "stop":
        stop(arguments.name)
    elif arguments.environment_command == "shell":
        shell(arguments.name)
    elif arguments.environment_command == "shell-root":
        shell(arguments.name, recovery_root=True)
    elif arguments.environment_command == "enroll-local-admin":
        enroll_local_admin(arguments.name)
    elif arguments.environment_command == "snapshot":
        snapshot(arguments.name)
    elif arguments.environment_command == "archive":
        archive(arguments.name)
    elif arguments.environment_command == "destroy-plan":
        print(json.dumps(make_plan("destroy", arguments.name), sort_keys=True, indent=2))
    elif arguments.environment_command == "destroy":
        destroy(arguments.plan, arguments.approve)
    elif arguments.environment_command == "restore":
        restore(arguments.archive, arguments.name, arguments.approve)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Refusal, subprocess.CalledProcessError) as error:
        print(f"APX refused: {error}", file=sys.stderr)
        raise SystemExit(2)
