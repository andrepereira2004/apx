> Atualização: proprietário rejeita popin no Rofi. Reposto slide bottom,
> mantendo entrada320ms apxFluid/saída240ms easeInOutCubic e carregamento lazy.
> Referências abaixo a popin no Rofi são históricas e foram substituídas.

# Desktop alignment, motion and startup responsiveness — 2026-10-25

Owner authorizes continuing integration work, prioritizes responsive application/
Rofi launch, boot/shutdown, horizontal alignment and matching corner geometry.
Subsequent owner feedback rejects overly short/brusque animations and uses the
QuickShell Environment/Control Centre menus as the reference for Rofi entry/exit.

## Final deployed configuration

- Shared logical outer edge20px matches Hyprland gaps_out20; QuickShell panel
  uses20px margins and capsule groups no longer add8px. Menus clamp to20px.
  Live numeric inspection confirmed calendar x20 and right controls ending1516
  on a1536logical-wide screen. Visible tiled content starts22px with2px border,
  so its outer frame starts20px. Floating windows remain independently positioned.
- Shared outer corner10px matches live Hyprland rounding10/power2 (circular).
  QuickShell popup/mask and outer ControlDashboard cards use that radius;
  Rofi launcherbox changes18px to10px. Internal controls retain their own radii.
- Bluetooth primary row action104x32/radius8 matches Wi-Fi compact action;
  paired-device Ligar keeps68px width. No pairing or radio action executed.
- Final application entrance320ms apxFluid Bezier(.2,.8;.2,1), popin97%;
  exit240ms easeInOutCubic, popin98%. Thunar keeps97% entry rather than90%.
  Intermediate220/160ms configuration was superseded after owner rejected it.
- Final Rofi layer rule popin97% replaces long slide-bottom; entry320ms apxFluid,
  exit240ms easeInOutCubic. Intermediate180/140ms and300ms settings superseded.
  These layer durations also affect other compositor-animated layers. QuickShell
  retains its own internal320/240ms animations. No internal Rofi motion added.
  Similar timing/curves do not establish identical geometry or perceived smoothness.

## Rofi startup work

Apps/system native mode init used to synchronously fetch both pages on every
Rofi start. Opt-in APX_ROFI_TIMING tracing in the native source confirmed apps
load76.4ms + hidden system load75.6ms in one short sample. Initialization now
allocates each mode but requests its initial page only when Rofi asks for its
entries/message. Each invocation still reads current data; no new cache or folder
prefetch. In one comparable trace, first app icon callback moved from209.5ms to
132.3ms relative to apps init; hidden system did not load. Direct system opening
loads system only. This is NOT a GPU-presentation or first-interactive-frame
measurement. Timing diagnostics emit only mode/stage/monotonic timestamps when
APX_ROFI_TIMING is explicitly enabled; otherwise silent.

Native apps/system compiled in Faculdade with-Wall/-Wextra/-Werror. Actual
isolated Rofi opens for both modes stayed alive and closed normally. Existing
40application action tests,2Bluetooth tests and7seed tests pass. Optional build
cache removed after reviewed binaries were copied to source and deployed.

## Thunar responsiveness

Evidence/probes in ../2026-10-25-desktop-integration/. Direct empty-directory
window map median455.8ms without resident process (five samples, not guaranteed
cold cache). With existing Thunar --daemon, five-sample median120.5ms; first
window still427.3ms, subsequent windows119.8–121.3ms. Resident RSS52176KiB.
Window mapping is not proof of interactive readiness or animation completion.
Integrated existing Environment-local Thunar daemon into background desktop
startup when /usr/bin/thunar exists, without waiting for it. Started it in active
Faculdade; no user Thunar window closed and no process-wide quit used. It belongs
to that Environment session and does not share state across Environments. First
window optimization remains open. No folder scan/preload added by APX.

## Boot/shutdown and LocalSend observations

Recorded boot32.282s: firmware10.270, loader2.476, kernel.985, initrd12.295,
userspace6.255. graphical.target is not an interactive desktop-ready timestamp.
No bootloader, firmware, TPM, encryption or initrd setting changed; no restart or
shutdown performed. Previous journal has only partial shutdown tail and no
reliable end-to-end shutdown duration. Controlled future validation still needed.
LocalSend old package archive itself contains mode0600 desktop entry, confirming
reinstall recurrence risk. Only the previously recorded Faculdade mode fix exists;
package rebuild and validation remain open.

## Deployment and recovery

Bounded wrapper scripts/physical-pilot/deploy-desktop-alignment-20261025.py
reuses identity-checked existing deployment, syncs source/independent seed/five
homes/runtime hashes/recovery pins and backs up exact changes. Last backup path
is in deployment output; latest motion backup recorded in CURRENT_HANDOFF.md.
--check reports0pending. Compositor live eval accepted; configerrors empty.
QuickShell reload readiness issue encountered during intermediate stages; only
supervised QuickShell process restarted, without restarting session/compositor.
Owner visual acceptance remains pending. No package install, commit or push.
