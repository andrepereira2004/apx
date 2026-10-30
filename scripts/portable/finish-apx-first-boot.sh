#!/usr/bin/bash
# Runs only in the newly installed system; no stored owner password or agent.
set -euo pipefail
[[ $EUID == 0 && -f /etc/apx-empty-disk-install.json ]]
finish() {
    result=$?
    trap - EXIT
    systemctl disable apx-first-boot.service
    systemctl unmask getty@tty1.service
    systemctl start --no-block getty@tty3.service
    if ((result)); then
        echo 'APX installation failed. Automatic retries are disabled. Inspect on VT3 before retrying.'
        echo "Exit status: $result"
    fi
    exit "$result"
}
trap finish EXIT
if [[ -e /var/lib/apx/portable-install.json || -e /var/lib/apx-first-boot-complete ]]; then
    echo 'Existing installation checkpoint: refusing automatic overwrite.'
    exit 2
fi
echo 'APX first boot. Internet is required. For Wi-Fi use root + nmtui on Ctrl+Alt+F3, then return with Ctrl+Alt+F1.'
until curl --fail --silent --head --max-time 10 https://archlinux.org/ >/dev/null; do
    echo 'Waiting for internet...'; sleep 5
done
bash /opt/apx-installer/scripts/portable/install-apx-full.sh --apply
touch /var/lib/apx-first-boot-complete
systemctl start --no-block apx-portable-graphical.service
