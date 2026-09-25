# Multiple native Windows instances — repository candidate

## First activation preflight and recovery (2026-09-23)

The real generation-bound preparation for `windows-testes` reached `prepared`
and retained the verified original backup, 120 GiB copy, installer and two
signed maintenance images. Activation stopped before BootNext because the
pilot's `efibootmgr` output formats the EFI loader as `/\\EFI\\...` and uses a
tab after the label. The newly created maintenance entry and EFI image were
retired after checking their exact identities, and authorization was revoked.
The four original partitions and Linux-first boot order remain; no offline
migration ran. The parser now accepts this observed format as well as
`File(...)`, with a focused regression test. The 1287-test suite passes with
11 skips. The prepared job remains available for a guarded retry.

## Host staging and remaining recovery gate (2026-09-23)

The owner authorized the exact 120+80 GiB physical migration. The candidate
Host modules and Hub integration were staged with backups, and all 15
release-bound installed files match the repository. The release marker has
not been published and the finalizer service remains disabled. This preserves
the original four-partition layout while recovery is reviewed.

An interrupted copy may leave the original p3 Windows extent changed while
the original GPT still exists. A partial GPT write may leave the layout
unreadable even after the new Windows extent has been verified. The current
inspector identifies these cases, but the regular-file repair experiment is
not a physical repair procedure. A tested path to boot recovery and restore
the exact approved state is still required before activation.

## Named review plan (2026-09-23)

The 80 GiB `windows-testes` review plan is in
`audit/2026-09-23-native-v3-windows-testes-review/`. It was recalculated from
the stored four-partition inventory and measurements of the earlier
`windows-2` preview. Its generation and partition identities are bound to
`windows-testes`; it is non-executable and becomes stale if the live layout or
measurements differ. Refresh those inputs before physical preparation.

The repository's 55 native v3 tests pass, including the selected deletion,
interrupted clear and free-slot transitions. This does not validate a complete
physical create, boot, return, delete and replacement cycle. Full preparation,
power-loss recovery and independent Windows boots remain acceptance gates.
The v3 release is disabled; partition or boot changes require a separate,
specific owner instruction.

## Review before physical execution (2026-09-23)

The named review artifact passed its digest and GPT-layout checks, including
preservation of the planned p1 and p4 records. The native v3 suite passed 55
tests and the Environment-switch suite passed 28 tests. Python compilation of
the v3 modules also passed. These checks use repository fixtures and mocks;
they do not exercise the physical SSD or firmware.

The next physical sequence is: refresh read-only disk identity, GPT, Windows
NTFS minimum, APX use, LUKS header and firmware state; regenerate the
`windows-testes` plan with those inputs; prepare and verify the original
Windows backup and recovery/install images; measure the complete preparation
against the APX capacity gate; review the exact recovery and partition changes;
then obtain a specific owner instruction before any partition, EFI or firmware
write. Acceptance must subsequently observe both Windows installations booting
and returning independently, deletion from the Hub, interrupted-delete
recovery, and creation in the reserved slot.

## Current pilot full-preparation probe (2026-09-23)

A fresh read-only preview for `windows-testes` retained the original four-partition
GPT and produced the non-executable plan in
`audit/2026-09-23-native-v3-windows-testes-current/`. In an isolated private
job, the actual p3 Windows source was cloned and verified, its 120 GiB prepared
copy was created, the installer WIM was updated, and both relocation and
rollback maintenance UKIs were built and signed. The job reached `prepared`.
After all artifacts, APX used 197,217,206,272 bytes against a
268,872,712,192-byte ceiling that includes the required 16 GiB headroom:
71,655,505,920 bytes (66.74 GiB) remained below that ceiling. The exact
result is `audit/2026-09-23-native-v3-windows-testes-current/full-preparation-probe.json`.

The private job, preview token and temporary build hook were removed. APX
returned to about 198 GiB free; the real v3 pending and release markers remain
absent. The SSD still has four partitions and the firmware order remains
Linux-first. This proves preparation and measured capacity for the observed
state. It does not prove offline relocation, power-loss recovery, Windows boots,
Hub deletion or replacement on the physical layout. Any later execution must
recreate and retain verified artifacts and recheck the live state.

## Replaceable second-Windows slot (owner requirement, 2026-09-23)

The owner accepted a disposable 80 GiB Windows named `windows-testes` only if
the Hub can later delete it and create another Windows from the menu. The first
physical migration must therefore not be enabled until both actions have a
reviewed and tested lifecycle. The proposed v3 slot behavior is:

1. The first migration retains the original Windows on p3/p1 and creates one
   independent 80 GiB p5 Windows slot with p6 EFI and p7 MSR. The Hub lists the
   new instance by its chosen name and generation.
2. The Hub may delete only a selected v3 instance on p5/p6. It must require a
   second explicit confirmation, reject any pending operation or BootNext,
   validate the exact GPT/firmware identities, and leave p1/p2/p3/p4 untouched.
   If deletion is interrupted, the instance remains unavailable and the Host
   resumes or requests recovery; it never claims the slot is free early.
3. After deletion, p5/p6/p7 remain a reserved Windows slot. The Hub should
   display that the 80 GiB is available for another Windows, not returned to
   APX. A new generation can reuse that slot only after the old Windows data,
   EFI and firmware entry have been retired and the Host has validated a
   root-owned free-slot record against the exact seven-partition GPT.
4. Replacement installation formats only p5 and p6, uses a new generation
   contract/status path on p4, and creates one exact new firmware entry. The
   existing Windows p3/p1 and APX p2 are never selected. The old instance
   record remains historical only outside the active catalogue.

Repository implementation now clears and verifies all logical bytes of p5/p6,
retires the exact p6 firmware entry first, and publishes the free-slot marker
only after both wipes complete. An interrupted clear keeps the selected record
unavailable and permits the same operation to resume. The Hub states that the
space remains reserved and deletion is not secure erasure. The replacement
installer copies display drivers from the original Windows read-only source
into its private WinPE image. Unit tests cover these state transitions; boot,
recovery, and deletion on the changed physical layout remain unvalidated.
No physical delete or replacement is authorized by this design section.

## Physical installer and maintenance build tests (2026-09-23, latest)

With the current pilot kernel, both migration and rollback maintenance UKIs
built and carried a Host Secure Boot signature in a private disposable job.
They used placeholder image hashes, were never copied to EFI and were removed.
Separately, read-only p3/p4 access found two graphics-driver directories and
copied the real setup `boot.wim` into a private job. The v3 WinPE script and
generation contract were inserted, wimlib verified the modified WIM, and both
embedded files were extracted with exact matching hashes. The test WIM was
removed. Summaries are under `audit/2026-09-23-native-v3-uki-build/` and
`audit/2026-09-23-native-v3-winpe-build/`. These tests validate the build
tools, not boot or recovery on changed physical partitions.

## Physical backup measurement (2026-09-23, latest)

The owner connected external power. On the identity-matched pilot, the original
Windows p3 was unmounted and read only while the tested backup module created
an original sparse image and a 120 GiB reflinked preparation image in a private
APX test directory. It verified the source fingerprint on both sides of the
clone, NTFS consistency, the image hashes and the plan-bound manifest. Real
filesystem usage increased by 67.6 GiB. With the backup present, APX used
183.5 GiB against the planned 250.4 GiB used-space ceiling, leaving 66.9 GiB
for additional preparation artifacts and variation. The exact byte counts are
in `audit/2026-09-23-native-v3-backup-measure/summary.json`. The disposable
images were removed and free space returned to 198.0 GiB. This verifies only
backup allocation; full preparation, offline migration/recovery and independent
physical Windows boots are still open. No partition, EFI, firmware or Windows
source change was made.

## Preparation ordering and interrupted-copy review (2026-09-23, latest)

Disposable lifecycle validation confirms the capacity proof is recorded after
the verified backup, installer and both maintenance images. A regular-file
experiment simulates a partial Windows copy and restores the exact original
extent from its intact backup without changing neighboring bytes. The read-only
inspector now reports `manual-original-restore-review` only when the original
GPT is present, a plan-bound migration status exists, the original Windows
extent differs and the complete original backup hash matches. It reads the
exact-size regular backup to verify it, so the physical inspection may take
time. It never
restores a physical partition. Power-loss recovery and independent physical
boots remain open. Focused tests: 47 native v3 and 28 switch tests passing.

## Measured backup capacity gate (2026-09-23, latest)

On the physical pilot, a read-only 80 GiB second-Windows preview retains
120 GiB for the original Windows and 266.4 GiB for APX. APX currently uses
115.9 GiB. A full 151 GiB source-partition backup plus 16 GiB headroom would
need 282.9 GiB, so that conservative bound does not fit. The current NTFS
minimum is 67.4 GiB, leaving a possible allocation range, but it does not
predict actual backup usage.

The planner can now issue a provisional, non-executable plan with a
`measured-backup-capacity` gate. Preparation builds the verified backup,
installer and recovery images before recording actual APX filesystem usage
in a plan-bound proof. Activation remeasures and requires that usage plus
16 GiB fit the planned APX partition. If it fails, partial preparation remains
for review; the SSD layout is unchanged. The Hub preview still reports
`can_create: false`. This is repository-only code: physical migration,
independent dual boot and power-loss recovery remain unverified. Focused tests:
43 native v3 and 28 switch tests passing. A disposable activation test confirms
that a changed capacity proof or current overuse stops before EFI publication.

## Explicit new-installation retry (2026-09-23, later)

The v3 repository candidate now has a bounded retry path for a new Windows
whose WinPE installer wrote an exact `failed` status. The Host checks the
selected generation, plan digest, migrated GPT and p4 setup firmware entry,
then rearms that entry only after a two-click Hub confirmation. The installer
formats the new incomplete target on retry; the original Windows and APX
partitions are not selected. A missing or ambiguous status, a failure after
the `boot-prepared` status, or two exhausted retries requires assisted
recovery. Forty focused native v3 tests pass, including mocked executor and
Hub-control checks; the switch contract test also accepts the selected retry
operation. No physical retry or disk write was performed.

## Independent boot and return contract (2026-09-23, later)

The v3 runner checks the selected record's EFI partition and entry, requires
that entry in BootOrder with Linux first, and arms only BootNext. Repository
tests exercise the old p1 and new p6 EFI entries independently. The shared
Windows ReturnToHub helper contains no fixed Windows partition or firmware
entry and passes the existing file-hash and driver checks in a disposable
Windows-root fixture. These tests do not prove physical firmware or Windows
startup behavior; no native v3 release was enabled.

## GPT repair laboratory (2026-09-23, later)

`src/apx_native_gpt_repair_v3.py` is deliberately limited to regular disk
files. Its disposable test wrote the original GPT, corrupted the primary
header, rewrote the planned destination GPT, and confirmed the exact table.
The read-only recovery assessment can label an unreadable or changed GPT for
manual repair review only when the copy marker and destination digest match.
These pieces do not form a physical repair procedure: the laboratory
assessment is supplied by the caller, and LUKS/Btrfs, firmware boot and
power-loss behavior still need end-to-end validation. The physical SSD was
not touched. Focused native v3 tests: 36 passing.

## Installer handoff correction (2026-09-23, later)

The generated WinPE script now writes `install-status-v3.ini` under
`APX/Native/<name>/<generation>/` on setup media and includes the exact plan
digest in success and failure records. It reads its setup contract from the
same directory. The Host finalizer checks the status
profile, generation, plan hash, Windows and dedicated EFI partition identities,
and byte equality with the EFI copy. An interrupted finalizer can reuse only
one exactly matching firmware entry; aliases and duplicates are rejected.
The Hub does not offer old-layout rollback after WinPE has started and instead
shows assisted recovery. The 35 focused native v3 tests pass. This remains
uninstalled. A data-preserving installation retry/discard design, interrupted
GPT repair, and physical independent boots are still required.

## Interrupted migration evidence (2026-09-23, later)

The offline candidate now retains a separate generation-specific
`copy-verified` marker after raw destination verification. A detected failure
from APX shrink, Windows copy or GPT write holds the initrd maintenance
session; it does not automatically reboot into a potentially inconsistent
partition layout. Backup manifests carry the exact plan hash, and the
renderer and lifecycle reject a mismatched manifest.

`scripts/physical-pilot/inspect-native-recovery-v3.py` is a read-only
candidate for the identity-matched pilot. Given the job plan and image
manifest, it reads the observed GPT and recovery markers and hashes the exact
destination extent. Its output is evidence for a reviewed recovery decision,
never permission to rewrite GPT. A disposable 64 MiB GPT file round-trip and
32 focused native v3 tests pass. Physical power-loss recovery and independent
Windows boots remain open; no pilot disk or firmware change occurred.

## Offline guard update (2026-09-23)

The repository-only offline layout validator now checks the starting GPT
layout and exact resulting GPT for the requested action: original to migrated
for relocation, migrated to original for rollback. The generated script writes
a generation-specific status record and
the finalizer reads that exact record. Hub and lifecycle expose rollback only
after an offline migration failure, before launching second-Windows setup;
rollback requires the migrated layout. The original partition is fully hashed
before and after cloning and rechecked before activating migration. Focused
native v3 tests pass (24). The
script has not been installed or run on the physical SSD. A failed Windows
setup needs a separate, data-preserving recovery path. The fingerprint guard
has repository tests but no physical validation. Interrupted GPT-write
recovery and independent EFI/BCD boot are unverified.

After GPT writing, the candidate re-reads and compares every approved extent
and partition identity before marking completion. On a detected write or
result-check failure, the initrd service stays in maintenance instead of
automatically rebooting. A power loss can still leave a partial GPT and needs
a separate, reviewed recovery procedure before physical activation.

## Morning implementation update

The live Hub now has independent-name Windows capacity review, implemented by
`native.plan` with authoritative Hub checks and a read-only sandboxed worker.
The button says “Verificar espaço”; `can_create` remains false. This is a
preview, not completed multi-instance creation.

The latest capacity plan reserves a dedicated 512 MiB EFI system partition
and 16 MiB MSR for the new Windows. Existing p1 EFI and p4 media stay unchanged;
p5 is the new Windows, p6 its EFI, p7 its MSR. New APX capacity is approximately
266.4 GiB. Registry validation now requires different EFI partition identities,
using the standard Microsoft boot path on each. Older custom per-generation
EFI directory proposals and the earlier 266.9 GiB budget are superseded.

Microsoft documents that BCDBoot `/s` targets the explicit system partition,
and `/f UEFI` places the boot files under `EFI/Microsoft/Boot`:
[BCDBoot documentation](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/bcdboot-command-line-options-techref-di?view=windows-11).
Dedicated partitions are our design choice based on that behavior, not proof
of two independent physical boots; firmware/BCD end-to-end validation remains.

`src/apx_native_backup_v3.py` prepares only private image files. Real test:
128 MiB NTFS source, payload inserted, original backup/reflink prepared copy,
copy shrunk to 96 MiB; original source hash and payload in both images match.
Failure keeps partial files and stage record. No physical backup or migration
was run. Full tests: 1236 passing, 11 skips. The offline executor and rollback
remain the next implementation gate, followed by native boot tests and the
explicit physical disk review required by AGENTS.md.

## Requested outcome

The owner wants two or more independent Windows Environments that boot natively
on the physical machine. Each must own its installation/data and appear in the
Hub catalogue. Switching is still a reboot, with one native OS active at a time.
Hyprland/QuickShell continue to serve the APX/Linux Environments.

This is an accepted product objective, not an installed capability. The current
native Windows pipeline still supports one installation. No limit was merely
removed from the UI or contract, because the underlying operations would still
address the original installation.

## Read-only evidence on this pilot

The internal disk has approximately 476.9 GiB and no unallocated GPT extent:

- p1: 1 GiB Linux/Windows EFI system partition;
- p2: approximately 315.9 GiB encrypted APX/Linux;
- p3: approximately 151 GiB existing Windows NTFS;
- p4: 9 GiB installation media.

`ntfsresize --info --no-action /dev/nvme0n1p3` reports 96,898,674,688 bytes
minimum from current allocation, roughly 90.24 GiB. The existing Windows cannot
be reduced to an 80 GiB partition while retaining its current files. The
observed APX Btrfs usage is about 83.7 GiB. These are observations, not resize
approval or proof that an offline migration will succeed.

Exact GPT and NTFS diagnostic output are preserved in
`audit/2026-09-21-input-monitors/disk-layout-before.json` and
`windows-space-readonly.txt`.

The native policy contains max_instances=1 and minimum_apx_size_gib=256.
Names, metadata paths, generation checks, partition IDs, UEFI selection,
maintenance status and destructive tail assumptions are all single-instance:

- `src/apx_environment_switch_contract.py`;
- `scripts/physical-pilot/apx-environment-switch-v1.py`;
- `scripts/physical-pilot/apx-native-boot-runner-v1.py`;
- `scripts/physical-pilot/apx-native-windows-lifecycle-v1.py` and finalizer;
- `scripts/physical-pilot/apx-native-windows-recovery-v1.py`;
- lifecycle initrd/build scripts and Windows installation media scripts;
- QuickShell creation, deletion and recovery actions.

In particular, the v1 offline executor expects a whole contiguous tail and
assumes that no other native Windows partition exists. Reusing it for a second
instance could affect the existing Windows. It must remain gated until replaced
by a plan that targets exact independent extents and generations.

## Storage choice confirmed

The owner explicitly requires only the current internal SSD. No additional disk
is an acceptable solution.

On the current SSD, one feasible capacity *budget* is:

- approximately 266.9 GiB for APX/Linux (above the existing 256 GiB minimum);
- 120 GiB for the existing Windows;
- 80 GiB for a second Windows;
- 9 GiB shared installation media plus the existing 1 GiB EFI partition.

This requires moving/restoring the existing Windows to a different start
position, not just shrinking Linux. Freeing about 49 GiB before p3 and shrinking
p3 does not by itself produce a contiguous 80 GiB new partition. A verified
backup/restore and exact offline relocation plan are prerequisites. The size
numbers above describe OS partitions explicitly; the current v1 menu counts
installation media inside its advertised reservation and must not silently
reuse those semantics.

Three 80 GiB Windows partitions plus installation media and the current
256 GiB APX minimum exceed this SSD's capacity. Supporting more instances
therefore means a capacity-based limit. Under the current 256 GiB APX reserve,
this SSD can budget two instances at 120+80 GiB, not unlimited installations.

## Required implementation before migration

1. A versioned per-instance registry binds name, generation, disk identity,
   partition identity/extent, dedicated Windows boot entry/BCD store and
   installation/recovery status. Preserve the legacy Windows record during
   migration; do not overwrite it to represent the second instance.
2. Catalogue, create, boot, metadata, delete and retry/discard operations all
   resolve the same selected instance. Authoritative Hub and generation checks
   remain enforced by the Host executor.
3. A capacity planner validates non-overlap, alignment, APX reserve, installer
   space and the complete observed precondition table. Creation/deletion acts
   only on the approved instance's extents. Reclaim to APX is allowed only when
   contiguous and validated; deleting one instance never expands across another.
4. Offline preparation and Windows setup carry the instance identity end to end.
   Per-instance status/attempt counters and EFI assets must not collide. Keep
   Linux first in boot order; BootNext selects the exact chosen native instance.
5. Validate first-install failure, adding a second installation, booting each,
   return to Hub, retry/discard for each, and deleting either instance while
   preserving the other. Repository contract tests are not physical boot proof.
6. Before any physical migration, prepare the exact executable plan, recovery
   artifacts and backups, then obtain the owner's explicit disk/boot approval
   required by AGENTS.md. Do not lower the APX reserve or destroy the current
   Windows to make this request appear completed.

No Windows filesystem, partition table, EFI entry, bootloader or native policy
was changed in this session. This work remains outstanding after the external
input and monitor improvements.

## Owner clarification

The owner explicitly selected only the current internal SSD on 2026-09-21.
No additional disk is an acceptable solution. Preserve the existing Windows
and implement the per-instance migration before requesting disk-write approval.

## Repository candidate now implemented

`src/apx_native_instances_v3.py` validates GPT non-overlap/alignment, per-instance
name/generation/disk/partition extent, unique EFI paths and boot entries, exact
selection and lifecycle state transitions. It rejects stale generations,
collisions, changed disks and booting a non-ready instance. These are pure
functions; they do not trust live metadata, authorize callers or write firmware.
Host ownership checks and caller authority still belong in the future executor.

`scripts/physical-pilot/plan-native-instances-v3.py` generates a review artifact
from explicit read-only inventory and measurements. The current result is
`audit/2026-09-21-input-monitors/native-migration-candidate.json`. It preserves
p1 ESP and p4 installer byte-for-byte in place. It shrinks the APX end, relocates
existing p3 Windows to 120 GiB with its PARTUUID/generation retained, and adds
p5 Windows at 80 GiB immediately before the existing installer. It includes
16 MiB LUKS metadata, the APX 256 GiB minimum and a conservative full-size
existing-Windows backup budget plus 16 GiB headroom inside the remaining APX.
`windows-games` is a placeholder identity, not a user-approved installation name.

This avoids moving/rebuilding the installer; it does not avoid relocating the
existing Windows. The artifact carries the original table hash, target extents
and a plan hash, and explicitly says executable=false. The old executor must
never consume it. Per-instance EFI paths are a proposed contract, not proof
that separate BCD stores boot correctly. Nine tests cover capacity, data and
backup budget, disk/extent drift, collisions, stale selection and isolated state
changes. Installed native actions remain v1 until the complete v3 offline
executor, rollback and physical boot verification exist. No migration approval
was requested because that executable work is not yet reviewable.
