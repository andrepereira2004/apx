# Fresh application installation — experimental physical pilot

Owner request: new Environments must install current stable application releases.
Repository packages already use an Environment-targeted full pacman -Syu. GPU
userspace must keep matching the running Host kernel driver, not blindly latest.
Flatpak installation resolves the current stable remote branch.

Add an upstream freshness check before resolving each external local artifact.
Brave is refreshed from its official GitHub stable release, verifying the asset
SHA-256 and retaining APX desktop integration. Publish a new root-owned package
and atomic digest manifest; retain old artifacts for rollback. Do not update Host
packages. Network failure must refuse creation instead of silently installing
an old browser. LocalSend is rebuilt from the verified supplier archive when needed. ArtCraft
uses current verified official Arch payloads with the APX package identity;
DeckCraft retains its scale wrapper and an updated managed-version pin. Old
binary patches are not blindly applied to different supplier binaries. ChatGPT
is resolved from its signed official index and its package signature is checked
against the previously reviewed public release key. Supplier format changes
fail explicitly instead of silently falling back to older cached artifacts.
Local APX applications remain at the current APX build; NVIDIA remains Host-bound.

Resolve VS Code and Bedrock launcher at installation from stable supplier metadata,
and use the current Minecraft launcher URL. No mutable metadata endpoint may
execute downloaded shell or PKGBUILD code on the Host. Downloads remain bounded,
HTTPS-only, with stable channel validation and checksums where supplied.

Installation freshness is a point-in-time guarantee, not continuous background
updates of existing Environments. Existing package update controls remain local.
Testing uses fixtures and isolated package inspection; no boot or broad upgrade
is needed. Recovery restores prior manifests/runtime/helper and uses existing
Environment snapshots when an installed application was changed.
