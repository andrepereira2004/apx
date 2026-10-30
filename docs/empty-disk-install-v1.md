# Experimental installation from an empty disk

Owner request, 2026-10-18: a new x86_64 PC must not require an existing Arch,
Btrfs setup, drivers, or Codex. Start the official Arch installation USB with
network access, obtain the reviewed graphical source bundle, and run its disk
installer. This is a new experimental installation path, not physical-pilot
reinstallation authorization. Tests may format only disposable virtual disks.

The live installer accepts one explicitly selected, writable, unused **empty**
whole disk (160 GiB minimum), shows its identity and a confirmation phrase,
and refuses signatures, partitions, mounts, swap and stacked devices. It never
automatically picks or erases a disk. Existing Windows and dual boot are outside
this path. Use a backup and explicitly empty the intended disk separately if
it previously contained data. This implementation does not configure encryption
or Secure Boot; firmware must permit the unsigned Arch bootloader.

One Arch/kernel: GPT, 1 GiB EFI partition on UEFI, or a BIOS boot partition on
legacy BIOS; Btrfs root subvolume; UUID fstab; GRUB; DHCP Ethernet/Wi-Fi through
NetworkManager; public firmware and detected CPU microcode. Graphics packages
are selected from PCI hardware, not DMI/model allowlists. Intel/AMD/virtual GPUs
use kernel/Mesa drivers. NVIDIA is admitted only if the exact PCI ID is in the
selected official NVIDIA driver's supported-products list; old/unknown GPUs
stop before disk changes instead of installing an incompatible driver.

The repository sources are copied, never the live Hub/home/credentials. The first
installed-system boot runs the existing graphical APX installer on tty1 and asks
for a fresh APX password there. No password is persisted for unattended replay.
A separate recovery root password is enrolled during the live installation.
VT3 remains a recovery login. Failure disables automatic retries so partial APX
installation is inspected rather than overwritten. The installed-system
installer cannot run inside a chroot, so this second boot is required.

Console and graphical password entry both use the APX default Portuguese keyboard.
After disk confirmation the live console explicitly switches to `pt-latin1`
before recovery-password enrollment; the installed console keeps that layout.
This prevents punctuation/accented passwords changing between console and GUI.
Pacstrap keeps its public package cache on the target disk, avoiding the live
USB's small writable overlay. Package signatures remain mandatory.

Commands from the unpacked bundle, as root on the live USB:

```sh
python scripts/portable/install_apx_disk.py --list-disks
python scripts/portable/install_apx_disk.py --disk /dev/SELECTED_DISK
python scripts/portable/install_apx_disk.py --disk /dev/SELECTED_DISK --apply
```

Default is read-only planning. `--apply` requests the exact displayed phrase and
recovery password before writing. Internet is required for official packages.
The script prints when to shut down/remove the USB and boot the installed disk.
If Wi-Fi is needed after reboot, configure it on VT3 using `nmtui`, then return
to VT1; no live Wi-Fi credentials are copied. Wired DHCP is automatic.

Current implementation/test evidence and remaining hardware limits must be
recorded separately; planning is not a successful blank-disk installation.

Portable sessions launch through upstream `start-hyprland`, forwarding the
configuration and watchdog handshake. A small compositor exec wrapper refuses
generic safe-mode restarts: APX owns recovery to Hub/console and must not expose
an unmanaged fallback desktop. The supervisor pins the admitted compositor PID.
Private desktop roots have a bounded 120-second registration allowance, including
the first ownership translation; exited units fail immediately. Ten seconds was
insufficient for the fresh intermediate workload in the UEFI rehearsal.

References for maintainers: [Arch installation guide](https://wiki.archlinux.org/title/Installation_guide),
[Hyprland launch tutorial](https://wiki.hypr.land/Getting-Started/Master-Tutorial/),
[Arch NVIDIA transition](https://archlinux.org/news/nvidia-590-driver-drops-pascal-support-main-packages-switch-to-open-kernel-modules/).
Driver selection uses the resolved package version's NVIDIA supported-products
page, not a frozen GPU list or the installation machine's model.
