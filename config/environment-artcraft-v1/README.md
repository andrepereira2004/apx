# Native ArtCraft packages on the Faculdade pilot

The creation office module resolves GridCraft, WordCraft and DeckCraft through
Host-owned digest-pinned manifests under `/var/lib/apx/package-artifacts`; packages
are installed only into the selected Environment. No suite is installed on Host.
WordCraft and DeckCraft desktop entries select native Wayland to avoid Xwayland
upscaling blur at fractional display scale.

## GridCraft asynchronous Open (installed 0.6.1-2)

Upstream GridCraft 0.6.1 calls the blocking native Open picker on its UI thread.
On Wayland the window cannot acknowledge compositor pings while selecting a file,
so Hyprland displays its not-responding dialog. The APX patch queues a parented
`rfd::AsyncFileDialog`, waits on a worker, wakes egui, and applies the selected
path on a later UI frame. Cancel retains the current workbook; repeated Open
requests do not create overlapping pickers; worker failure is reported. Input
into the sheet is paused while its modal picker is outstanding. Desktop response
and JSON inspection remain live. Saved paths, recent files and password/error
handling still use the normal `open_path` route. The web picker is unchanged.

Only **Open** is changed; native Save/Export/picture pickers are outside this fix.
No compositor not-responding checks are disabled.

Patch: `patches/gridcraft-0.6.1-async-open.patch` (MIT OR Apache-2.0 upstream).
Source tag archive: `https://github.com/storytold/gridcraft/archive/refs/tags/v0.6.1.tar.gz`.
SHA256: `8c3997854e19d385aa00082e3f8de091ed4f65127be0b195cb826b3cb3083380`.
Build source and compiler state belong only in Faculdade's owner cache, not Host.
Apply with `patch -p1` in the clean tag tree. Build with `cargo build --locked
--release -p gridcraft -j 3`, using `CARGO_PROFILE_RELEASE_LTO=false`,
`CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16`, `CARGO_PROFILE_RELEASE_OPT_LEVEL=2` and an
Environment-local `CARGO_TARGET_DIR`. Run `cargo test --locked --release --lib -p
gridcraft-ui-egui async_open_tests -j 3` with the same profile before packaging.
Replace only `/usr/bin/gridcraft` in the original package payload, increment its
package release, preserve licensing/icons/CLI, and update its package manifest
SHA256 plus the patch/source/binary hashes. The suite installer preserves an
`apx_patch=async-open-v1` manifest rather than reinstalling the blocking binary.

Three regression tests pass. The native Wayland GUI passed a 20-second selector
hold with 20 responsive UI requests, cancel, actual XLSX selection and save.
The installed binary is identical to that candidate; the creation resolver admits
the updated artifact. Adoption evidence: audit/2026-10-12-gridcraft-async-open.json.
Future upstream builds require revalidation; this is an APX patch, not an upstream
published release.
