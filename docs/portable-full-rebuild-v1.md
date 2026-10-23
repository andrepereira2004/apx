# Experimental graphical APX rebuild on generic Arch PCs — VM results, 2026-10-18

For a PC with no OS, use the newer [Portuguese USB installation guide](install-apx-from-usb-pt.md)
and [empty-disk rehearsal](empty-disk-validation-2026-10-18.md). The entry point
`install_apx_disk.py` now installs Arch/Btrfs/bootloader/drivers before continuing
with this document's installed-Arch graphical installer. The earlier results
below remain historical evidence; they are not the latest final-source replay.

Status: **fresh Arch graphical installation and the enhanced automated core
checks passed in a disposable VM**. This is still an experimental local-source
candidate, not complete physical-pilot feature parity or a published GitHub
reinstallation path. The public entry point remains the older headless installer.

## Measured result and completed cleanup

- Fresh Arch x86_64, kernel 7.2.11-arch1-1, QEMU q35: installer completed and the
  current Hub/QuickShell booted. Workload lifecycle, isolation, snapshot and
  archive/restore passed. The final panel command lacked a display in the test
  fixture; the fixture was corrected without changing the installed product.
- Cold boot on QEMU pc/i440FX: all **15 enhanced checks passed**, including the
  same graphical/isolation lifecycle, explicit refusal of workload socket/CLI
  management, forced compositor failure returning to Hub, update preview and
  opening Control Centre through real QuickShell IPC. This establishes two
  virtual hardware profiles, not compatibility with every real PC.
- All **528 product source files** match the exact local source input used by
  the fresh VM; all **185 shell assets** matched their installed pins.
- Bar/background and [Control Centre](../audit/2026-10-18-portable-rebuild/vm/pc-controls.png)
  were visually inspected. Human initial login, personalization interaction,
  real GPU, wireless/audio, suspend and full update execution remain acceptance
  gates. Automated VM authentication fixtures were never shipped by the installer.
- Teste, its VM disk, installed private QEMU, maintenance/budget units and KVM
  proxy were **deleted**. RAM build roots/keyrings and the temporary bundle are
  absent. About 1.15 GiB of package archives explicitly downloaded by Host-side
  test steps was removed; installed packages were not uninstalled on the Host.
  Other Environment registrations were unchanged during cleanup, partitions
  match the original baseline, APX is healthy and no Host service failed.
  Free space at cleanup: **106.76 GiB**.

Evidence: [PC acceptance](../audit/2026-10-18-portable-rebuild/vm/pc-result.json),
[complete installation log](../audit/2026-10-18-portable-rebuild/vm/fresh-full-install.log),
[source comparison](../audit/2026-10-18-portable-rebuild/vm/final-source-comparison.json),
[cleanup](../audit/2026-10-18-portable-rebuild/vm/cleanup.json), and
[64 focused source tests and bundle checks](../audit/2026-10-18-portable-rebuild/source-verification.json).

The 97 GiB guard interrupted repetitions while preserving the existing 96 GiB
Host reserve. Only the test's unpublished workload was recovered after that
interruption. Source, installation logs and failure evidence remain; no live
roots, credentials or VM disks are retained. No new commit/push was performed.

## Current candidate and test ownership

`scripts/portable/install-apx-full.sh` defaults to read-only `--check`; `--apply`
requires a fresh already-installed Arch x86_64 Host, Btrfs, an admitted graphical
seat and new APX identity enrollment. It does not partition disks, migrate
Windows, configure a bootloader or copy live Hub data. The normal Arch package
upgrade may update the Host kernel; no physical disk formatting is performed. This new command is
not yet a published GitHub entry point.

The candidate reuses the current lifecycle and signed Arch bootstrap, then builds
one fresh graphical release and an independent immutable Hub release. Installed
source modules and the complete pinned shell seed come from an explicit source
manifest. The graphical supervisor discovers paired DRM/render nodes, connected
outputs and seat0 inputs. It creates generation-scoped character-device proxies,
retains private user/network namespaces, and exposes only the selected nodes and
typed service sockets. Workloads never receive the management socket.

Existing status/calendar/appearance/audio and management contracts are reused
with active-peer/cgroup/generation checks. Hub authority uses the root-published
current Hub identity, not the pilot generation or a hardcoded unit. The generic
profile admits authenticated Hub CLI management in addition to QuickShell;
power mutations retain the existing shell-bound confirmation mechanism.
Switching retires one private graphical session before activating another;
workloads may return to Hub but cannot directly switch/manage other workloads.

This is a fresh platform profile without personal/third-party applications or
biometric credentials. It does **not** enable the pilot's native Windows disk
planner, Legion GPU-firmware switch, external model-store setup or privileged
Host-console exception. These are explicit remaining portability boundaries,
not features proved by copying their source into an installation. Hardware
controls are capability-based; absent backlights/radios/audio do not block boot.
Current generic updates and other pilot-specific management integrations still
need end-to-end admission before full feature parity may be claimed.

The authorized test uses `teste`, generation
`6d3bf7be-dcf6-4040-a13e-9fda4c7c8100`, with intermediate preset and QEMU installed
in its private root. Only a KVM proxy under `/dev/apx-portable-rehearsal-teste`
enters its maintenance container. Root command/authentication fixtures exist only
inside the disposable guest, are guarded by VM detection and a test marker, and
are never installed by the APX installer. They demonstrate automated lifecycle
behavior, not human login acceptance. There are no guest Host-directory shares,
forwarded TCP ports or physical disks. Final cleanup removed Teste, VM,
maintenance/budget units, device proxy and temporary rootfs/keyrings, retaining
source and non-secret technical evidence only.

## Reproducing the experimental candidate

Use an already installed and booted Arch x86_64 system with Btrfs and a working
Host graphics driver. This command is not a disk installer and is not a promise
of compatibility with every PC. The read-only check refuses unsupported or
already populated targets:

```sh
bash scripts/portable/install-apx-full.sh --check
```

On a fresh disposable target, run the same entry point with `--apply` as root.
It requests a **new** password interactively and performs the normal Arch package
upgrade before building APX. Start the installed graphical service with
`systemctl start apx-portable-graphical.service`. A failed graphical start leaves
the Host console available; inspect `journalctl -u apx-portable-graphical` there.
Do not run this on the current populated pilot.

A source-only distribution can be created from this checkout:

```sh
python scripts/portable/build-bundle.py --profile graphical /path/to/apx-graphical.tar.gz
```

Extract it on the fresh target, enter `apx-portable`, and validate
`sha256sum -c SHA256SUMS` before running the check. The archive excludes test
agents, authentication fixtures, live roots, homes, private identity and VM
images. It preserves the exact selected source bytes; Arch package versions
remain rolling repository inputs, not a frozen package snapshot. Publication
and a test downloading that published revision remain separate acceptance.

## Owner request and observed starting point

The owner requested a new graphical Environment named **Teste**, with the
`intermediate` desktop preset, containing QEMU and a fresh Arch VM. That VM must
install the complete current APX experience from repository sources. The
installation must not be locked to this Lenovo model or the pilot's identities.
This explicitly names `teste`, superseding the temporary-mode default test-name
prefix for this experiment only. It does not authorize removing existing
Environments, data, snapshots or Windows, or changing the physical disk layout.

Read-only inspection on 2026-10-18 confirmed the expected `apx-host`/82JU pilot,
healthy Btrfs full-accounting quotas and no failed systemd units. Hytale was the
active graphical Environment. No Teste registration existed. About 25 GiB was
available on the physical Btrfs pool, below the existing **96 GiB** reserve
required before creating an Environment. No creation or provisioning was
attempted, and the active session was not switched or restarted.

The new read-only audit found all **185** shell-seed assets in the runtime's
pinned manifest identical in the repository and installed independent seed.
That checks the shell seed, not every mutable home or the complete system.
Among 176 Python/shell files directly under `/usr/lib/apx`, 159 matched a tracked
source by name and hash and 17 differed. The canonical graphical engine and
session under `/var/lib/apx/official-hub-v1` also differ from repository source.
Some library files are superseded copies. Do not overwrite repository code from
that inventory without reviewing the actual execution path and differences.

Evidence: `audit/2026-10-18-portable-rebuild/readiness.json`. Comparison is not a
backup, a transitive-dependency proof, or installation/recovery acceptance.

## Repeatable inspection

From this checkout on the current Host:

```sh
python scripts/portable/audit-rebuild-readiness.py
```

Optional `--output NEW_FILE.json` creates a new report exclusively. Exit 2 means
there are known blockers; exit 3 means inspection failed. The audit never runs
the installed adapters, installs packages, writes APX state, reads private
credentials, copies service bodies or exports Environment homes. It compares
source hashes, seed hashes and service executable paths.

The initial resource estimate allowed 32 GiB of actual additional working space **after**
the existing 96 GiB reserve, giving a starting threshold of 128 GiB available.
This is a conservative planning allowance, not a new APX policy or a guarantee
of final image size. A sparse 160 GiB guest disk does not provide real storage.
The reserve must also be checked during construction and before new growth.
The user was asked whether space would be freed or another disk provided.
An additional disk still requires an explicit storage design: putting only
the VM there would not satisfy the APX pool's Environment-creation reserve.

After the authorized cleanup recovered 82.30 GiB, the bounded rehearsal instead
stages Arch in RAM, avoids a retained second build root, and relies on normal
runtime/outer Btrfs compression. A Host budget service stops only the test if
available physical space falls below 97 GiB, preserving the existing 96 GiB
reserve. This supersedes the earlier 128 GiB starting estimate for this measured
run, not the installed lifecycle's storage policy. A first image created with
the Host mkfs rootdir zstd compressor produced guest decompression failures;
that option was removed and the failed disposable disk deleted after preserving
logs. A second fresh Arch image boots correctly with kernel 7.2.11-arch1-1.

## Required portable installation design

These are the design and acceptance boundaries; implemented behavior and measured
results are recorded above. Optional hardware integrations remain separate.

1. Start on an already installed, booted Arch Linux **x86_64** system with
   systemd and a suitable Btrfs pool. This first scope excludes other CPU
   architectures and operating systems. Refuse existing APX state instead of
   overwriting it. Do not partition, format physical disks, replace bootloaders
   or enroll Secure Boot keys as part of APX installation.
2. Install an explicit, pinned revision and an inspectable source/file manifest.
   Reconcile current live-code differences first. Build fresh releases using
   public package sources; do not copy the live Hub, its home, a Development
   checkout, password hashes, face identity, session state or credentials.
   Package artifacts unavailable from official Arch repositories need their
   own reproducible build/download recipe, version, license and checksum.
3. Preserve current private root/home/package databases, generation-bound
   lifecycle, typed management requests, immutable releases and independent
   seeds. Only the authoritative active Hub may manage other Environments.
   A workload may return to Hub but must never gain the management endpoint.
4. Add a separate portable graphical adapter. Discover DRM devices, render
   nodes and their associated connected displays; input devices and seats;
   optional audio, camera, Bluetooth, Wi-Fi and battery devices. Select/install
   drivers supported by the detected hardware. Never replace fixed pilot
   checks with blanket `/dev`, filesystem or Host-root access. Missing optional
   hardware disables only its feature; it must not prevent the Hub starting.
5. Generate installation-local identifiers and service configuration. Remove
   dependence on the pilot's fixed Hub generation, unit name, PCI addresses,
   ALSA card/index, input identity and `wlan0` from the portable path. Retain
   peer credentials, user-namespace, active-cgroup and generation checks.
   Preserve the pilot default identity guards. The portable adapter supplies its own
   root-owned installation identity; active-peer authority checks remain mandatory.
6. Install the current Hyprland/QuickShell seed and required desktop dependencies
   into fresh Environment roots. Validate compositor/configuration compatibility
   rather than assuming a rolling Arch package has the same Lua interface as
   the pilot. Enroll a new local human identity interactively. No password or
   credentials may be embedded in GitHub or the VM evidence.
7. Install supervised graphical-session, service, shutdown and recovery paths.
   A graphical failure must leave Host-console recovery usable. Native Windows,
   GPU passthrough, face enrollment and external model storage are optional
   separate integrations; fixed hardware bindings cannot be copied to a
   generic target or claimed tested by a virtual GPU.

## Teste and VM execution contract

Once the resource blocker is resolved, create only the new `teste` Environment
using the reviewed APX create-plan/create path, `graphical-base` role and
`intermediate` preset. Record its generated identity and exact effects before
applying them. Never rename/reuse an existing workload to make the test pass.
Do not silently switch away from the owner's active Environment.

QEMU and its dependencies belong in Teste's private package root. Admit only a
bounded `/dev/kvm` capability through the existing Host device-lease path. Keep
the VM disk, source staging and logs within the test budget. Use a fresh virtual
disk and network; expose no physical block devices, Host homes, Host system bus,
APX-management sockets or credentials to the VM. Installation must target the
guest's disk only. Arch can be installed from official media or bootstrapped
using the official Arch tools. Preserve full installation, boot and failure logs.

The guest must exercise the **full** installer, not simply rerun the old headless
smoke test. Pin and record the source revision and actual installed file hashes.
If testing unpublished changes with a read-only source image, label that run as
local-source acceptance; it does not establish GitHub delivery acceptance.

Acceptance gates before advertising complete portable parity (automated core
checks above passed; remaining human/physical/UI gates are still open):

- fresh Arch guest boots the graphical Hub with the current QuickShell;
- the rendered bar, Control Centre, menus and personalization are inspected;
- Hub can create an independent intermediate graphical workload, switch into
  it and return; workload management of other Environments is refused;
- a real package installation and private file in one workload remain absent
  from the guest Host, Hub, base and a second workload;
- snapshot, archive/restore, stop and deletion operate through the existing
  authority checks, preserving unrelated data;
- compositor failure recovers to the Hub or documented console path;
- a second cold boot reproduces the installed behavior;
- installer refuses an existing installation and unsafe/unsupported targets;
- no model, serial, pilot generation or fixed PCI address is required;
- a distinct virtual hardware profile is tested before expanding portability
  claims; real GPU, wireless, audio and suspend acceptance stays separate.

No new full-install command is published until it exists and passes this
rehearsal. A second successful test fetching the published revision from GitHub
is needed before advertising a one-command GitHub reinstall.

## References

- [Existing portable headless base and its older VM evidence](portable-arch-base-v1.md)
- [Arch installation from existing Linux](https://wiki.archlinux.org/title/Install_Arch_Linux_from_existing_Linux)
- [Arch QEMU documentation](https://wiki.archlinux.org/title/QEMU)
- [systemd-nspawn isolation and mapped mounts](https://www.freedesktop.org/software/systemd/man/latest/systemd-nspawn.html)
