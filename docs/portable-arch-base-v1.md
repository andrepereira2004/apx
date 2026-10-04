# Portable Arch base v1 (experimental)

The owner requested installation on a different generic PC on 2026-10-04.
This first adapter reuses the current APX headless lifecycle and typed Hub
executor. It is independent of Lenovo identity, disk names, EFI and native
Windows partitions. It does not yet reproduce the current graphical pilot.
The graphical pilot still requires a hardware-independent device lease,
seat/recovery adapter and installation of its authenticated service contracts.
Do not run the physical-pilot scripts on another PC or remove their guards.

## Architecture and effects

Run on an already booted, fresh Arch Linux x86_64 installation with systemd,
Internet access, and Btrfs at `/var/lib/apx` (a Btrfs `/` also works). The current
96 GiB host reserve remains enforced; allow at least 110 GiB free. The installer
never partitions, formats, alters the bootloader or copies the live Hub.
It refuses existing APX installations and containers. Inspection is the default;
`--apply` installs packages, enables healthy Btrfs quotas, builds fresh signed
Arch releases, installs the current runtime/client/executor and enables the
executor and headless Hub at boot. Fresh pacman keyrings are initialized separately, populated from the official
Arch public keyring and preserved by `pacstrap -K`; Host secret keys are not copied.
No login credentials, personal files, native Windows
images, firmware identities or development authentication are bundled.

Each Environment has its own writable root/home, package database and user
namespace. Releases are immutable. A Host firewall and a networkd configuration
apply only to APX virtual interfaces. Only the active Hub user namespace can
submit typed lifecycle requests. Host root remains the recovery authority.
A normal workload never receives the management socket. Containers are not VMs.

## Recovery and acceptance

An incomplete install leaves `/var/lib/apx/portable-install.json` with its last
completed phase and refuses reinstallation. This deliberately avoids silently
accepting incomplete releases or overwriting another installation. Inspect the
record and journal from the Host console; preserve evidence before resetting a
fresh disposable target. The existing Host console/boot path remains available.
Stopping `apx-portable-hub.service` stops only Hub; stop individual workloads with
`apx environment stop NAME`. Do not erase `/var/lib/apx` on an established system.

Required acceptance: boot a new VM with no physical disks, install from source,
verify executor and Hub after reboot, create/start/stop/delete a workload through
the authenticated Hub, verify its package/data isolation, and refuse installation
over existing state. Repository tests are not equivalent to this evidence.

## Usage

A transfer archive can be built without copying machine state:

```sh
python scripts/portable/build-bundle.py /tmp/apx-portable.tar.gz
```

Extract it on the new PC and run `sha256sum -c SHA256SUMS` from its directory.
Alternatively, copy a clean checkout of this repository. Then:

```sh
bash scripts/portable/install-apx-arch.sh --check
bash scripts/portable/install-apx-arch.sh --apply
apx environment shell hub
```

Inside Hub:

```sh
apx environment create-plan work --role minimal
# Use the digest printed by the plan:
apx environment create --plan DIGEST --approve 'CREATE work AS minimal'
apx environment start work
```

On the Host, `apx environment shell work` opens its unprivileged account.
`apx environment enroll-local-admin work` interactively sets an Environment-local
administrator password. All application installation then belongs in that
Environment. This release admits only headless hub/development/minimal roles;
GUI and native Windows are explicitly unavailable on the portable base.

References: [systemd-nspawn](https://www.freedesktop.org/software/systemd/man/latest/systemd-nspawn.html)
and [Arch systemd-nspawn](https://wiki.archlinux.org/title/Systemd-nspawn).


## Repeatable VM test

On an Arch laboratory Host with root, KVM, `qemu-system-x86`, `pacstrap`,
`arch-chroot` and `mkfs.btrfs` available:

```sh
python scripts/portable/test-in-vm.py /path/to/new-teste-de-vm
```

The path must not exist. The harness builds a new Arch filesystem and a sparse
160 GiB virtual disk (allow 12 GiB real free space), boots QEMU with no physical
block devices, shared folders or forwarded ports, and repeats the lifecycle
checks after a second boot. It keeps the disk and logs for inspection. Its
only disk-format operation targets the freshly created regular file. It does
not create a registered Environment on the current APX Host or change its reserve.
The guest uses locked accounts; the smoke runner is a temporary root service
inside the disposable VM. This runner is not included in the installation bundle.


## Observed result — 2026-10-04

Fresh installation passed in QEMU/KVM “Teste de VM” using guest kernel
7.2.8-arch1-2, 4 GiB RAM and a new sparse 160 GiB disk. Two subsequent boots
also passed authenticated Hub creation/start/stop/deletion of `vmtest`, a private
filesystem write, absence of the management socket in the workload, installation
of signed Arch package `ed` only in that workload, and refusal to overwrite the
existing APX installation. Only Hub remains registered inside the guest after
testing. The physical APX catalogue was not changed.

The read-only post-test inspection matched every installed source hash to the
repository and confirmed the installer completed. All 1,347 repository tests
pass (11 expected skips). Python compilation, shell syntax, whitespace checks
and bundle checksums pass. The initial stale test expectations were corrected;
the runtime status lookup now supports a plain directory on Btrfs, and its
repository recovery digest was updated without deploying it on the pilot.

The VM exposed and led to fixes for runtime symlink resolution, missing pinned
Hub defaults, package keyring trust initialization, restrictive inherited umask,
networkd configuration reload before first container creation, and test readiness
(DHCP and waiting for both services). Package signature checks remained enabled.
These results validate the headless base only. They do not establish graphical,
GPU, suspend, physical-device or native-Windows portability.

Evidence: [`audit/2026-10-04-portable/result.json`](../audit/2026-10-04-portable/result.json).
The stopped VM and raw logs are in `/root/apx-teste-de-vm`; successful logs are
`boot-v5-1.log`, `boot-v6-1.log`, `boot-v6-2.log`, and the retained disk is
`disk-v5.raw`. Failed trial disks were removed; diagnostic logs were retained.
The VM is not a registered Environment in the current physical APX because its
69 GiB initial free space was below the unchanged 96 GiB creation reserve.
