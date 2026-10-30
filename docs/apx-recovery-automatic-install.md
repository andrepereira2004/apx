# APX Recovery in new empty-disk installations

The portable empty-disk installer (`scripts/portable/install_apx_disk.py`) now
requires UEFI and creates three partitions: a 1 GiB EFI system partition, a
2 GiB ext4 `APX_RECOVERY` partition, and the APX Btrfs system partition. It
refuses a populated disk. This changes future installations only; it does not
repartition an existing APX computer.

Before formatting, the installer downloads the pinned official Codex CLI
`rust-v0.166.0` Linux x86_64 release and verifies its SHA-256 digest. The
recovery partition receives a separate minimal Arch Linux, its own kernel,
initramfs, NetworkManager, filesystem repair tools, and `codex`. It boots to
a text console with root login and no graphical desktop. The user connects to
the network, runs `codex login --device-auth` once, then starts `codex`.

The installer creates an `APX Recovery` UEFI firmware entry that loads a
separate unified kernel image. Its boot order keeps APX first and Recovery
last. Normal power-on proceeds without a selection screen; the firmware setup
or boot menu can select Recovery. The key used to open that menu depends on
the computer's firmware and is not guaranteed to be F2 on another PC.

Recovery uses the shared EFI system partition for its UEFI image but never
needs the APX root filesystem to start. If the shared EFI partition or disk
itself fails, external installation media is still required. The recovery
root is unencrypted and allows physical console access; do not put account
tokens or other private APX data in its installation image.

The installer source and a verified release download have been tested here.
A fresh empty-disk installation, firmware menu selection, and cold boot on a
second computer remain acceptance checks before calling the path proven.
