# Portable native lifecycle v4 — development boundary

Owner authorized continuing portable parity and isolated installation testing on
2026-11-21. Physical disk layout/boot changes are not part of that instruction.
The existing native v3 pilot remains enabled and unchanged.

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
this profile. Source code is not enabled for physical writes until its actual
storage and recovery tests succeed.

## Bounded clean-VM rehearsal

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
