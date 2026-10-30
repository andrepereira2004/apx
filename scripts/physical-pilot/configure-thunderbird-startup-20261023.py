#!/usr/bin/env python3
"""Disable the welcome page/donation notices in one explicitly selected profile.

Last-selected-message restoration is provided separately by the official
Last selected message 2.1 MailExtension; this file does not claim to replace it.
"""
from pathlib import Path
import argparse
import datetime
import os
import shutil

BEGIN = '// APX mail startup begin'
END = '// APX mail startup end'
PREFERENCES = {
    'mailnews.start_page.enabled': False,
    'mail.inappnotifications.donation_enabled': False,
    'mailnews.scroll_to_new_message': False,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile', type=Path)
    args = parser.parse_args()
    profile = args.profile.resolve(strict=True)
    assert profile.is_dir()
    path = profile / 'user.js'
    assert not path.is_symlink()
    text = path.read_text() if path.exists() else ''
    old = text
    if BEGIN in text:
        assert text.count(BEGIN) == text.count(END) == 1
        a = text.index(BEGIN)
        b = text.index(END, a) + len(END)
        if text[b:b + 1] == '\n':
            b += 1
        text = text[:a] + text[b:]
    block = BEGIN + '\n' + ''.join(
        f'user_pref("{key}", {str(value).lower()});\n'
        for key, value in PREFERENCES.items()
    ) + END + '\n'
    data = text + ('' if not text or text.endswith('\n') else '\n') + block
    if data == old:
        print('Startup preferences already match.')
        return
    info = path.stat() if path.exists() else profile.stat()
    if path.exists():
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup = profile / ('user.js.before-apx-startup-' + stamp)
        shutil.copy2(path, backup)
        os.chown(backup, info.st_uid, info.st_gid)
        print('Preference backup:', backup)
    temp = path.with_name('user.js.apx-startup-tmp')
    assert not temp.exists() and not temp.is_symlink()
    temp.write_text(data)
    os.chmod(temp, info.st_mode & 0o777 if path.exists() else 0o600)
    os.chown(temp, info.st_uid, info.st_gid)
    os.replace(temp, path)
    print('Startup preferences configured; restart Thunderbird.')


if __name__ == '__main__':
    main()
