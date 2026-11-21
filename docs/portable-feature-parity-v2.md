> Atualização: instalação limpa e segundo arranque concluídos em 2026-11-21.
> Ver [evidência v3](../audit/2026-11-21-portable-v3/README.md);
> Windows nativo portátil v4 agora está [implementado nas fontes](portable-native-v4-development.md);
> sem nova instalação Windows/aceitação física neste computador.

# Portable feature integration v2 — 2026-11-21

Experimental extension of the fresh Arch graphical installer. Sources remain
repository-owned and versioned; the live Hub never becomes a release template.

New Environments obtain selected native applications from verified stable vendor
releases. Host-owned download storage contains packages and public manifests,
never credentials. Packages are installed only into an independent new root.
The common release and Hub stay minimal. Public packaging recipes bootstrap
without requiring an older package from the pilot. NVIDIA userspace is admitted
only when it matches the running Host module; other GPUs require no NVIDIA.
Selected user applications retain private nspawn installation before publication.

A root-owned shared folder is bound read-only into each graphical Environment.
The existing bounded copy/rename broker provides writes, including wallpaper
usage. Services start before the graphical supervisor. Teardown retires the
session namespace and leaves shared owner data intact; installer retries never
replace an existing APX installation. No live homes, passwords or device IDs
are exported by the bundle.

Public, reviewed packaging assets and their digests belong to the source
manifest. Locally adapted applications without a stable public source require
an explicit reviewed distribution artifact; unavailable modules fail before a
new Environment is published. Fresh-source checks distinguish inclusion from
actual runtime enablement. A new VM replay and physical acceptance remain
necessary evidence after source tests.

Native Windows, firmware GPU switching, external model storage and pilot USB
UUID allowlists are not generic capabilities. Enabling these without a per-host
storage/boot transaction and recovery design is not permitted by this change.
Their current safeguards remain in force. Source parity must never be described
as full portable functional parity while these integrations remain unported.

## Implemented source and package checks

The portable creator now provisions every catalogue module through the current
feature catalogue. Brave, LocalSend, ArtCraft and ChatGPT bootstrap from verified
stable upstream releases even with an empty package cache. Public recipe text,
icons and the ChatGPT public signing key are versioned under
`config/portable-packages-v2`. Salvador de Mundos uses the small reviewed,
digest-pinned APX distribution artifact; its Python ABI requirement is retained.
No application profiles, sessions or credentials are shipped. Apps are installed
only when selected for a workload; the Hub remains minimal.

Repository and native packages run inside a temporary private-user/private-network
nspawn machine, with the package cache mounted read-only. Failed transactions
retire the machine and firewall identity before allowing recovery. Intel/AMD
Flatpak setup no longer requires an NVIDIA module. NVIDIA userspace is kept at
the Host version. Creation checks estimated application workspace in addition
to the existing 96 GiB recovery reserve before creating new volumes.

The installer now installs/starts the transfer, filtered Bluetooth passkey,
removable USB and LocalSend services. Graphical sessions bind shared files
read-only and expose admitted USB files through the Host broker. USB admission
requires USB transport, removable media, a serial, a filesystem UUID and a
supported vfat/exfat/NTFS partition; disks with mounts outside APX are excluded.
Duplicate UUIDs and raw-device/path unmount requests are refused. The existing
root-only unmount broker rechecks device identity. Public USB catalogues drive
bookmarks, notifications and safe-removal actions. No pilot USB UUID is needed.
Capture-capable seat0 camera character nodes are discovered separately.

Environment batch updates stop and restart the portable graphical supervisor
rather than a physical-pilot launcher. The Hub resume phase reuses its existing
policy/rollback directories, preserving their link checks and backup contents.
Host package updates remain the Arch console workflow in the portable profile.

The live/source differences were reviewed. Most represent older installed
adapters, deliberate hardware/identity adaptation or personal appearance.
The current repository's newer cleanup, device, package-coherence and compositor
changes are retained. The wallpaper chooser's double-click/Enter acceptance fix
was ported. Only the four changed shell helper hashes were renewed; the source
runtime hash in the historical quota recovery script was synchronized.

## Evidence and remaining acceptance

`audit/2026-11-21-portable-parity/` records:

- 777 verified source files and a rebuilt standalone graphical bundle. The
  extracted bundle independently passes hashes and contains all new recipes,
  helpers, public key and the reviewed Salvador distribution package.
- Seven real package bootstraps: Brave 1:1.100.58-1, LocalSend 1.18.2-1,
  GridCraft 0.19.1-1, WordCraft/DeckCraft 0.18.1-1, ChatGPT
  26.1117.41037-1 and Salvador 1.0-1. ChatGPT index and package signatures were
  verified using the versioned public key. Vendor failures never publish a
  replacement manifest. A missing first-install ArtCraft template was found
  by this rehearsal, fixed, covered by a regression test and rechecked.
- 385 focused tests passed, including 39 portable tests. Six pre-existing test
  failures were independently reproduced using unchanged HEAD files and remain
  recorded, rather than counted as passes. They concern older appearance
  assertions/fixtures and a whole-file tempfile prohibition now also matching
  public LocalSend configuration writes. No unrelated appearance policy was
  changed to satisfy those older expectations.
- Both fresh-install entry points refuse this already installed APX computer.
  The installed native release remains enabled with no validation errors.

No new operating-system installation, boot, USB mount, camera capture, Bluetooth
pairing or native Windows transaction was executed on the Host. Package download,
metadata/signature verification, source tests and bundle extraction are not a
clean-VM replay. The previously documented VM storage/tooling constraints remain.

**Full parity remains incomplete.** Native Windows creation/deletion/reclaim is
still bound to the pilot's encrypted disk layout, signed UKIs and exact SSD
identity. The generic installer uses a different unencrypted Arch/GRUB layout.
A separate portable storage/boot/recovery implementation and a fresh VM replay
are required before enabling those operations on a new PC. Firmware-specific GPU
mode changes are likewise not enabled on unrecognized hardware. Do not remove
those guards or describe this source integration as complete physical parity.
