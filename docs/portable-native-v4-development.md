# Portable native lifecycle v4 — source implementation

The owner requested source implementation on 2026-11-21 for a future PC, with
no Windows installation, VM rehearsal or disk/boot changes on this computer.
The portable v4 executor, WinPE builder, Hub actions, return helper and exact
instance deletion/reclaim are implemented in the repository. They are staged by
the future fresh-disk installer; the existing native v3 pilot remains unchanged.
This is experimental source implementation, not a newly observed Windows install.

The generic profile has ESP + APX Recovery + a single unencrypted Btrfs root.
A new native transaction must bind disk serial/WWN, GPT GUID, sector size and
partition UUIDs/extents to a root-owned per-installation identity. Partition
numbers and Linux device spelling may differ across SATA/NVMe/virtio. Existing
ESP, Recovery, foreign partitions and native siblings must remain exact.

Creation is calculated as an offline Btrfs shrink with preserved recovery reserve
and headroom, followed by a Windows payload, independent ESP/MSR and temporary
installation media in the freed contiguous tail. Each transaction has a fresh
generation, a recomputable digest, exact approval, durable stages, rollback before
WinPE launch, bounded setup retries afterwards, and independent EFI/BCD identity.
Deleting a non-adjacent slot cannot silently claim immediate contiguous Linux
growth; it must retain a reusable slot or use a separately validated multi-device
Btrfs integration and boot dependency. No pilot LUKS/UKI constants are copied into
this profile. The future installer stages the executor; runtime writes require the exact
installation identity, matching Recovery code, registered official ISO and a
separate authenticated activation. There is no VM-acceptance switch to unlock.

## Earlier bounded clean-VM rehearsal (historical)

Use only the new `codex-test-portable-v3` disposable development Environment,
with its generation recorded before tools are installed. QEMU and its packages
belong there. KVM is a named character-device proxy, never a physical block
path. The guest is a 160 GiB sparse file, booted with a guest-only kernel/initrd,
private networking and a private virtio-serial owner test channel. No Host homes,
credentials, block devices or system sockets enter QEMU.

This rehearsal replaces the earlier unallocated 32 GiB workspace estimate with
a hard 24 GiB aggregate qgroup for this one test's root and home, plus a 97 GiB
Host free-space stop guard. The product's 96 GiB reserve is unchanged. With
approximately 124 GiB initially free, the ceiling leaves recovery headroom;
if the bound prevents completion, preserve logs and stop rather than increasing
it or touching other Environments. RAM staging is limited by available memory.
The old 32 GiB figure remains historical for its earlier unbounded test plan.

After each run, retain sanitized logs/source hashes only. Stop owned units,
prove the QEMU process and KVM lease are gone, destroy only this recorded test,
and remove its own qgroup. Preserve other registrations and the native release.

## DNS integration discovered during rehearsal

The lab uplink accepts verified HTTPS but direct DNS from its private namespace
is unreliable. Portable workload egress must remain closed to private LAN/Host
services. A bounded per-veth DNS broker may expose UDP/TCP 53 only on admitted
APX gateway addresses and forward DNS wire messages to a fixed verified HTTPS
resolver, with limited query size/concurrency and no query logging. DHCP advertises
the gateway (`DNS=_server_address`), preserving arbitrary gateway allocation.
This avoids opening LAN access or relying on a copied Host resolver file.

The temporary lab's separate DNS fixture is never included in product sources.

## Implementation contract — owner request 2026-11-21

The owner requests source implementation only, with no installation or disk/boot
changes on this PC and no further installation rehearsals. The portable fresh-disk
installer will provision the independent Recovery root with an offline worker.
Hub preparation verifies owner-registered Windows ISO SHA256/image index, builds
an instance-bound WinPE helper in a disposable compiler root, and copies verified
media and a transaction into Recovery. Activation explicitly queues a one-shot
Recovery boot. Recovery verifies the hardware/GPT checkpoint again, shrinks the
unmounted Linux root, writes the complete protected GPT, formats only new slots,
and stages a patched WinPE image. The normal APX boot remains first in BootOrder.
WinPE validates exact GPT GUIDs/extents, sector geometry and source hashes before
DISM; BCDBoot writes only the new instance's ESP. Linux finalization validates
completion and files before exposing the Windows entry. No automatic boot loops.
Retries are bounded and explicitly confirmed; interrupted offline operations are
resumed from durable checkpoints, never inferred solely from a stage name.

Deletion retires only EFI entries bound to the selected ESP, erases only that
instance's exact extents, and reclaims adjacent space into the original root.
Nonadjacent space becomes a recorded Btrfs member with early boot device scanning;
new shrink-based creation is refused while root is multi-device. Recovery remains
an independent ext4 filesystem and can resume a failed job without mounting the
normal root as its own system. Unknown layout changes stop before writes.

Windows ISO/download licensing and hardware drivers are not copied from this PC.
The future owner registers an official ISO/hash/index and optional verified driver
archive through the Host console. WinPE and the Windows return helper are built
from repository C source using Arch-signed compiler packages in a temporary tool
root; development packages do not enter Host or Environments. Windows owns its
own user/OOBE/license/update lifecycle; APX adds a visible Return to Hub action.

This is an experimental source implementation, not new physical validation.
Syntax/contract review may be performed; no installer, VM or Windows is launched
as part of this implementation task.


## Using it on the future PC

Install the graphical portable APX profile from the normal USB flow first.
The fresh-disk installer stages the independent Recovery worker and records that
PC's own disk/GPT/filesystem identities. An arbitrary existing Arch installation
without that Recovery/identity is not silently repartitioned or enrolled.

On that future PC's Host console, obtain the official Windows x64 ISO, compare
its SHA256 with the publisher, and inspect its edition indexes with
`wimlib-imagex info /path/to/windows.iso`. Register the chosen index:

```sh
apx-native-windows register-source --iso /path/to/windows.iso \
  --sha256 OFFICIAL_SHA256 --image-index CHOSEN_INDEX
```

The command imports only verified public installation media into a private store;
it does not install Windows or queue a reboot. Optional `--drivers drivers.tar`
and `--drivers-sha256 SHA256` accept an owner-verified archive of signed x64
INF/SYS/CAT driver packages for that PC. Relative files/directories only; links,
special files and traversal are refused. Drivers are loaded into WinPE and added
to the selected Windows image. No Lenovo/pilot driver, activation, account or
personal credential is imported.

In the Hub, select Windows, choose the name/capacity and check the space. Prepare
it first; preparation builds verified per-instance media with an Arch-signed
cross-compiler in a disposable tools root. No development package is installed
on the Host. A separate confirmation then installs and restarts through Recovery
and WinPE. WinPE returns to the Hub; opening the new Windows completes its own
OOBE/account setup. Windows-requested restarts return to APX by default; open the
same Windows again when its first-boot setup needs another pass. No unattended
boot loop or APX password import is added.

A visible APX tray action in Windows offers Return to Hub; it elevates only the
small helper, verifies the exact APX GPT ESP and EFI path in firmware, sets APX
first/next with readback, and restarts. The helper does not depend on localized
BCD output, fixed boot numbers, VBScript or PowerShell inside WinPE.

The Hub exposes explicit cancellation before native installation, at most two
retries of that instance, and removal/reclaim after installation or a failed
installation. `apx-native-windows status` provides the same durable state at the
Host console. Root console instance commands use `--target NAME --generation
UUID`; they are operator recovery tools, not workload permissions.

## Storage and recovery details

Heavy media stays in the normal root until copied into the newly allocated
10 GiB setup slot. Recovery's 2 GiB ext4 root stores only its worker, journal and
plans. The planner accounts for a 24 GiB transient media/build allowance in
addition to allocated Linux extents, the 96 GiB reserve and 16 GiB headroom.
The full before/after GPT and instance plan remain in Recovery even on failure.
A shrink changes only the unmounted root; the kernel partition map is updated
only for changed, unmounted partitions while Recovery stays mounted.

Every stage is fsynced. Repeated pre-WinPE stages admit only the exact before or
after checkpoint; there is no inference from a log line alone. Formatting cannot
run from an unexpected layout or without the generation-bound media manifest.
Once WinPE is launched, restoring the old table is prohibited; explicit retry or
exact-slot deletion is required. Unknown/torn GPT changes stop for operator
recovery using the saved complete tables rather than guessing partition ranges.
If the offline unit fails, the independent Recovery console remains available;
the firmware default still points to APX. No automatic retry is armed.

Adjacent deletion grows the original Btrfs device. A nonadjacent deleted slot
becomes an exact recorded Btrfs member; its initramfs dependency is generated for
both systemd and BusyBox initramfs, and rebuilt before adding the member. Other
Windows slots remain exact. New shrink-based creation is deliberately refused
while root is multi-device. UEFI x64, the fresh portable GPT/Btrfs layout and a
stable disk serial/WWN are required; this does not convert legacy BIOS, encrypted
or foreign layouts. It does not automate BitLocker recovery or Windows licensing.

## Implementation map and verification scope

- `src/apx_portable_native.py`: recomputed geometry and immutable identities.
- `src/apx_portable_native_io.py`: trusted records, device/firmware checks.
- `src/apx_portable_native_media.py`: official ISO, split WIM, private compiler.
- `src/apx_portable_native_worker.py`: Host/Recovery lifecycle and finalization.
- `src/apx_portable_native_hub.py`: authorized Hub catalogue, status and dispatch.
- `scripts/portable/apx-portable-native.py`: future worker/console entry point.
- `scripts/portable/install_native_v4.py`: future Host and Recovery provisioning.
- `config/portable-native-v4/`: Windows helper, tray, provisioning and boot hooks.

Source contracts use mocked commands and synthetic geometry only; they do not
open block devices, firmware, ISO or Windows. No new VM, installation, physical
repartitioning, service deployment or Windows execution was performed for this
change. The new C helper has not been compiled/executed here. Earlier Linux VM
results remain historical and do not certify these new native sources.

The BCDBoot `/s` behavior follows [Microsoft's command reference](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/bcdboot-command-line-options-techref-di?view=windows-11):
boot files go to the selected ESP without creating a global firmware entry.
WinPE startup follows [Winpeshl.ini](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpeshlini-reference-launching-an-app-when-winpe-starts?view=windows-11).
WIM metadata and boot-index selection follow [wimlib](https://www.wimlib.net/man1/wiminfo.html).

The private builder uses the official [Arch mingw-w64-gcc package](https://archlinux.org/packages/extra/x86_64/mingw-w64-gcc/); it is not added to the Host package list.
