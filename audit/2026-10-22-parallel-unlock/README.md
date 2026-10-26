# Parallel face/password unlock — 2026-10-22

Owner asked to type the unlock code while scanning the face. Applied in Hub,
Faculdade, Hytale, Minecraft and Steam. Howdy now opens the password conversation
while comparison runs; submitting input stops comparison and leaves PAM_AUTHTOK
for pam_unix. A recognized face cancels the pending conversation and completes
through the existing faillock authsucc path. Failed/disabled camera preserves
password input. A wrong password still reaches authfail. Password, face model,
camera settings and account/session/password include paths are unchanged.

The installed upstream native workaround cancels a PAM prompt thread. Upstream
labels this mode potentially unstable; isolated tests below pass for the installed
binary and Hyprlock-style condition-variable callback, but actual owner unlock
remains to be observed. This is a bounded experimental pilot configuration.
No input emulation, additional uinput grant, new package or biometric copy.

Howdy's workaround setting is per Environment, not per PAM consumer. Consequently
other already configured Howdy consumers (such as sudo in Hub) also offer the
concurrent prompt. Their PAM files and authorization rules were not changed.
The protected opt-in identity config/PAM and digests were updated for future
workload creation; no face model was opened or copied by this deployment.

Source lock comments/status instructions, independent seed/five homes and runtime/
recovery digest pins updated. Authentication deployment recheck: 0 files pending.
UI/seed deployment recheck: 0 files pending. No session restart or owner lock.

Validation:
- 21 existing face identity/status tests pass.
- 7 desktop seed tests pass.
- Native installed pam_howdy tested inside a private mount namespace using the
  candidate production PAM ordering, a synthetic comparison script, synthetic
  password verifier/faillock, and a Hyprlock-style blocking conversation.
  Face success, password during scan, timeout, camera failure, rejected password,
  and disabled Howdy pass. Children reaped. See validation.log.
- Fixture modules never become live authentication policy. Model contents,
  camera and real passwords are not used. These tests validate coordination and
  PAM control flow, not real password checking, face accuracy or faillock storage.
- Work-default suite has an unrelated existing bar-layout assertion failure;
  its lock assertion was updated for concurrent behavior.

Reproduce fixture (g++/PAM development headers already present):

```sh
g++ -O2 -pthread pam-conversation.cpp -lpam -o pam-conversation
g++ -shared -fPIC pam-fixture-password.cpp -lpam -o pam-fixture-password.so
g++ -shared -fPIC pam-fixture-faillock.cpp -lpam -o pam-fixture-faillock.so
python validate.py
```

Fixture uses the fixed Faculdade root only as read-only test substrate with
namespace-local file overrides; it does not boot or alter that Environment.
The global mount propagation is made private before any bind mount.

Backups:
- /var/lib/apx/backups/20261022T072852Z-parallel-unlock (private config and PAM).
- /var/lib/apx/backups/20261022T072907Z-controls-followup (UI/seed/digest pins).

Authentication rollback: run deploy-parallel-unlock-20261022.py --rollback with
its backup. UI rollback uses deploy-parallel-unlock-ui-20261022.py --rollback
with the controls-followup backup. Roll back both before reinstating old digests.
No commit or push.

Primary implementation references (retrieved 2026-10-22):
- https://github.com/boltgolt/howdy/blob/d3ab99382f88f043d15f15c1450ab69433892a1c/howdy/src/pam/main.cc
- https://github.com/hyprwm/hyprlock/blob/main/src/auth/Pam.cpp
- https://github.com/linux-pam/linux-pam/blob/master/modules/pam_unix/pam_unix_auth.c

Retrieved upstream files in this directory are reference evidence; the Howdy
source is pinned, while the Hyprlock main file is not an exact installed version.
