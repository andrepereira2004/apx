# Empty-PC installer rehearsal, 2026-10-18

Experimental owner-authorized work. No physical disk layout, kernel, bootloader
or driver installation on the physical pilot. Owner's existing Teste/manual VM
is retained separately. Evidence: `audit/2026-10-18-empty-disk/`.

The new installer starts from the official Arch 2026.10.01 installation ISO,
SHA256 `684ded26c63240ff4a41e8c25ee84ea6da233f557364821f13d12c2b0a9059a5`,
and a new empty 180 GiB sparse virtual disk. QEMU runs unprivileged inside a
private maintenance container cloned from disposable Teste's stopped root;
it receives only its own RAM-backed files and a KVM character-device proxy.
There is no physical block device, live Hub/home, Host management socket,
filesystem share or Host credential in the guest. Root command fixtures use a
private virtual serial port and are excluded from the product bundle.

The live installer was exercised through its actual terminal prompts using a
new synthetic recovery password. In UEFI/q35 it formatted the virtual disk,
installed Arch/firmware/Mesa/microcode/NetworkManager, generated UUID fstab and
GRUB, then powered off. A disk-only boot with no external kernel/initramfs/ISO
started the first-boot APX service, which requested a different new password.
The actual password prompts and graphical login were driven by virtual keyboard
and mouse. No authentication-bypass fixture was enabled for this installation
or normal login. The installed product sources matched the then-current checkout.

The initial functional suite exposed a real registration timeout: fresh nspawn
ownership translation exceeded ten seconds. Preserved the failure and journal;
the supervisor now allows 120 seconds, bounded by unit liveness. Added regression
tests for delayed registration, timeout and immediate failure. Patched only that
controller in the UEFI guest, recreated the failed test workload through APX,
and all 15 functional checks passed: shell/source integrity, Hub identity,
independent intermediate workload, switching/return, workload management refusal,
real package/file isolation, compositor-failure recovery to Hub, snapshot,
archive/restore, destruction, update preview, overwrite refusal and real shell
IPC opening Control Centre. This is a patched runtime replay, not a fresh replay
of the final complete installer source; the separate BIOS replay covers that.

The UEFI guest then passed a normal reboot/password login and 125 seconds of
continuous Hub stability, with both VT2 getty instances masked and no failed
guest units. Real pointer movement and the upstream watchdog handshake were
verified after reboot. See `uefi-cold-boot-stability.json`.

A separate BIOS/pc replay installed from the final 534 product sources on an
empty virtual disk, starting with a restrictive 0077 live-root umask. The target
root retained Arch's readable/traversable 0555 mode. Disk-only BIOS/GRUB boot,
first-boot APX installation, normal graphical login and all 15 functional checks
passed **without runtime patches**. Both the installation source manifest and
installed compositor/session/controller hashes match the current checkout.

The last follow-up aligned console/graphical keyboards to Portuguese before
password enrollment. Real virtual-keyboard input with Unicode and punctuation
passed console enrollment and graphical PAM login; it was not just an ASCII
password test. No bypass fixture was enabled. Earlier BIOS stage-one success
was superseded and its target fully discarded before this final replay. A
test-only cache-copy shortcut hit the ISO's small writable-overlay limit and
was abandoned/cleaned; final pacstrap uses its normal target-local package cache.
See `bios-final-replay-reset.json`, `bios-final-install-plan.json`,
`bios-final-functional.json`, `bios-unicode-login.json` and the compressed install log.
Normal BIOS reboot then passed the same Unicode/punctuation password login;
first-boot setup remained disabled and no guest units failed. See
`bios-cold-boot.json`. No subsequent runtime/source patch was needed.

Read-only discovery on the actual AMD/NVIDIA pilot selected AMD microcode,
Mesa/Radeon and the official supported NVIDIA open driver. No physical package
installation or database synchronization occurred. This validates selection,
not a fresh real-GPU boot. Intel, AMD, virtual and NVIDIA admission/rejection also
have unit coverage. Sixty focused tests pass after the registration fix.

Tests do not establish universal PC support, full physical-pilot feature parity,
native Windows/dual-boot installation, Secure Boot, encryption, biometrics,
firmware-specific GPU controls, real radio/audio/suspend, or full update execution.
New installation creates a fresh APX; personal applications/documents, biometric
enrollment and the old machine's mutable Environment payloads are not restored.

Cleanup removed the extra RAM-backed ISO/disks/synthetic secret, maintenance
container, temporary Btrfs root, KVM proxy, HTTP source server and its budget
guard. Owner's existing Teste/manual VM remains. Physical partition-table hash
and measured normal Environment registration hashes are unchanged; no failed
Host units. Host free space after cleanup: 99.04 GiB. Btrfs I/O counters remain
zero and its pre-existing corruption counter remains 79. See `cleanup.json`.
Source, technical evidence and the small source-only delivery package are kept;
none of these changes have been committed/pushed in this stage.
