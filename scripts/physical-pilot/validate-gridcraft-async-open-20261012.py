#!/usr/bin/env python3
"""Run inside Faculdade as apx: validate a disposable GridCraft Open picker."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import time

import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi


def rpc(method, params=None, timeout=2):
    with socket.create_connection(('127.0.0.1', 17984), timeout) as stream:
        stream.settimeout(timeout)
        stream.sendall((json.dumps({'id': 1, 'method': method, 'params': params or {}}) + '\n').encode())
        data = b''
        while True:
            chunk = stream.recv(65536)
            if not chunk:
                raise RuntimeError('GridCraft closed the control connection')
            data += chunk
            try:
                return json.loads(data)
            except ValueError:
                continue


def chooser_nodes():
    nodes = []
    def walk(node, depth=0):
        if depth > 18:
            return
        nodes.append(node)
        for index in range(node.get_child_count()):
            walk(node.get_child_at_index(index), depth + 1)
    desktop = Atspi.get_desktop(0)
    for index in range(desktop.get_child_count()):
        app = desktop.get_child_at_index(index)
        if app.get_name() == 'xdg-desktop-portal-gtk':
            for child in range(app.get_child_count()):
                window = app.get_child_at_index(child)
                if window.get_role_name() == 'file chooser' and window.get_state_set().contains(Atspi.StateType.SHOWING):
                    walk(window)
    return nodes


def wait_picker():
    for _ in range(100):
        nodes = chooser_nodes()
        if nodes:
            return nodes
        time.sleep(0.1)
    raise RuntimeError('No native file selector appeared')


def press_button(names):
    for node in chooser_nodes():
        if node.get_name() in names:
            action = node.get_action_iface()
            if action and action.get_n_actions() and action.do_action(0):
                return
    raise RuntimeError('Selector action was not available: ' + '/'.join(names))


def choose_file(path):
    nodes = wait_picker()
    for node in nodes:
        action = node.get_action_iface()
        if node.get_role_name() == 'file chooser' and action and action.get_n_actions():
            if not action.do_action(0):
                raise RuntimeError('Could not show the location field')
            break
    time.sleep(0.2)
    for node in chooser_nodes():
        if node.get_role_name() == 'text' and node.get_state_set().contains(Atspi.StateType.SHOWING):
            if not node.get_editable_text_iface().set_text_contents(str(path)):
                raise RuntimeError('Could not enter the test path')
            node.get_action_iface().do_action(0)
            break
    else:
        raise RuntimeError('No visible location field')
    time.sleep(0.3)
    press_button({'Selecionar', 'Select', 'Abrir', 'Open'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary', required=True)
    args = parser.parse_args()
    work = Path.home() / '.cache/apx-gridcraft-validation/async-open'
    work.mkdir(parents=True, exist_ok=True)
    work.chmod(0o700)
    test = work / 'picker-input.xlsx'
    output = work / 'picker-output.xlsx'
    if chooser_nodes():
        raise RuntimeError('An existing file selector is open; do not interfere with it')
    subprocess.run(['gridcraft-cli', 'run', '--cmd', 'cell.set={"cell":"A1","input":"12"}',
                    '--cmd', 'cell.set={"cell":"A2","input":"30"}',
                    '--cmd', 'cell.set={"cell":"A3","input":"=SUM(A1:A2)"}', '--out', str(test)],
                   check=True, stdout=subprocess.DEVNULL)
    env = dict(os.environ, XDG_CONFIG_HOME=str(work / 'config'), GRIDCRAFT_NO_PREFS='1')
    log = (work / 'gui.log').open('ab')
    proc = subprocess.Popen([args.binary, '--control', '17984'], env=env,
                            stdin=subprocess.DEVNULL, stdout=log, stderr=log)
    report = {}
    try:
        for _ in range(100):
            try:
                initial = rpc('document.inspect')['result']
                break
            except (OSError, RuntimeError):
                if proc.poll() is not None:
                    raise RuntimeError('Candidate quit at startup')
                time.sleep(0.2)
        else:
            raise RuntimeError('Candidate did not respond at startup')
        assert rpc('ui.key', {'key': 'O', 'cmd': True, 'ctrl': True})['ok']
        wait_picker()
        latencies = []
        for _ in range(20):
            start = time.monotonic()
            assert rpc('ui.inspect')['ok']
            latencies.append(time.monotonic() - start)
            time.sleep(1)
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j']))
        ours = [c for c in clients if c['pid'] == proc.pid]
        assert ours and not ours[0]['xwayland']
        assert not any('not responding' in c['title'].lower() for c in clients)
        report.update(held_picker_seconds=20, responsive_queries=20,
                      maximum_response_ms=round(max(latencies) * 1000, 2), native_wayland=True,
                      no_not_responding_dialog=True)
        press_button({'Cancelar', 'Cancel'})
        time.sleep(0.3)
        canceled = rpc('document.inspect')['result']
        assert canceled['sheets'] == initial['sheets'] and canceled['dirty'] == initial['dirty']
        report['cancel_preserves_workbook'] = True
        assert rpc('ui.key', {'key': 'O', 'cmd': True, 'ctrl': True})['ok']
        choose_file(test)
        for _ in range(30):
            opened = rpc('document.inspect')['result']
            if opened.get('path') == str(test):
                break
            time.sleep(0.2)
        else:
            raise RuntimeError('Selected file was not loaded')
        values = rpc('sheet.read', {'range': 'A1:A3'})['result']['values']
        assert values == [[12.0], [30.0], [42.0]]
        assert rpc('app.save', {'path': str(output)})['ok'] and output.is_file()
        report.update(open_from_native_selector=True, values=values, saved=True)
        (work / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report), flush=True)
        rpc('app.quit')
        proc.wait(timeout=5)
    finally:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=5)
        log.close()


if __name__ == '__main__':
    main()
