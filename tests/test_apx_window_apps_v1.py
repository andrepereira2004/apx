import importlib.util
from importlib.machinery import SourceFileLoader
import json
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout


SCRIPT = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-window-apps-v1'


def load_module():
    spec = importlib.util.spec_from_loader('apx_window_apps_v1', SourceFileLoader('apx_window_apps_v1', str(SCRIPT)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WindowApplicationsTests(unittest.TestCase):
    def test_catalog_marks_special_workspace_and_matches_startup_class(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'example.desktop'
            path.write_text('[Desktop Entry]\nType=Application\nName=Exemplo\nStartupWMClass=ExampleApp\nIcon=example-icon\nExec=example\n')
            windows = [{'class': 'ExampleApp', 'address': '0xabc', 'pid': 123,
                        'title': 'Documento', 'workspace': {'name': 'special:magic'}}]
            with patch.object(module, 'SOURCES', (Path(directory),)), \
                 patch.object(module.subprocess, 'check_output', return_value=json.dumps(windows).encode()):
                apps = module.catalog()
        self.assertEqual(len(apps), 1)
        self.assertTrue(apps[0]['windows'][0]['minimized'])
        self.assertEqual(apps[0]['windows'][0]['pid'], 123)
        self.assertEqual(apps[0]['icon'], 'example-icon')

    def test_unmatched_running_window_is_still_visible(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            windows = [{'class': 'local-tool', 'address': '0xdef', 'pid': 234,
                        'title': 'Local Tool', 'workspace': {'name': '2'}}]
            with patch.object(module, 'SOURCES', (Path(directory),)), \
                 patch.object(module.subprocess, 'check_output', return_value=json.dumps(windows).encode()):
                apps = module.catalog()
        self.assertEqual(apps[0]['name'], 'local-tool')
        self.assertFalse(apps[0]['windows'][0]['minimized'])

    def test_host_console_uses_terminal_name_and_icon(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / 'apx-terminal.desktop').write_text(
                '[Desktop Entry]\nType=Application\nName=APX Terminal\n'
                'Exec=/home/apx/.local/bin/apx-host-console-open\n'
                'Icon=/usr/share/icons/Papirus/48x48/apps/utilities-terminal.svg\n'
                'StartupWMClass=apx-host-console-v1\n')
            windows = [{'class': 'apx-host-console-v1', 'address': '0xabc',
                        'pid': 123, 'workspace': {'name': '1'}}]
            with patch.object(module, 'SOURCES', (Path(directory),)), \
                 patch.object(module.subprocess, 'check_output', return_value=json.dumps(windows).encode()), \
                 patch.object(module, 'resolve_icons'):
                apps = module.catalog()
        self.assertEqual(apps[0]['name'], 'APX Terminal')
        self.assertEqual(apps[0]['icon'], '/usr/share/icons/Papirus/48x48/apps/utilities-terminal.svg')
        self.assertEqual(apps[0]['id'], 'apx-terminal')
        self.assertEqual(apps[0]['windows'][0]['address'], '0xabc')

    def test_running_apps_precede_frequent_closed_apps(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            for name in ('alpha', 'beta'):
                (source / (name + '.desktop')).write_text(
                    '[Desktop Entry]\nType=Application\nName=' + name + '\nExec=' + name + '\n')
            usage = source / 'usage.json'
            usage.write_text('{"beta":100}')
            windows = [{'class': 'alpha', 'address': '0xabc', 'pid': 123,
                        'workspace': {'name': '1'}}]
            with patch.object(module, 'SOURCES', (source,)), \
                 patch.object(module, 'USAGE', usage), \
                 patch.object(module, 'ROFI_USAGE', source / 'missing-cache'), \
                 patch.object(module.subprocess, 'check_output', return_value=json.dumps(windows).encode()):
                self.assertEqual([a['id'] for a in module.catalog()], ['alpha', 'beta'])

    def test_existing_rofi_history_is_reused_without_double_counting(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / 'rofi3.druncache').write_text('30 brave-browser.desktop\n28 hytale.desktop\n')
            (source / 'usage.json').write_text('{"hytale":3}')
            with patch.object(module, 'ROFI_USAGE', source / 'rofi3.druncache'), \
                 patch.object(module, 'USAGE', source / 'usage.json'):
                self.assertEqual(module.usage_counts()['hytale'], 31)
                module.record_use('hytale')
                self.assertEqual(json.loads((source / 'usage.json').read_text())['hytale'], 4)

    def test_resolved_icon_cache_keeps_desktop_icons_without_gtk_lookup(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            icon = root / 'sample.svg'
            icon.write_text('<svg/>')
            cache = root / 'icons.json'
            cache.write_text(json.dumps({'sample-icon': str(icon)}))
            app = {'icon': 'sample-icon'}
            with patch.object(module, 'ICON_CACHE', cache):
                module.resolve_icons([app])
            self.assertEqual(app['iconPath'], str(icon))

    def test_terminate_requires_current_window_address(self):
        module = load_module()
        with patch.object(module, 'catalog', return_value=[{'windows': [{'address': '0xabc', 'pid': 123}]}]), \
             patch.object(module.os, 'kill') as kill, \
             patch.object(module.sys, 'argv', ['apx-window-apps-v1', 'terminate', '0xabc']):
            module.main()
            kill.assert_called_once_with(123, module.signal.SIGTERM)
        with patch.object(module, 'catalog', return_value=[]), \
             patch.object(module.os, 'kill') as kill, \
             patch.object(module.sys, 'argv', ['apx-window-apps-v1', 'terminate', '0xabc']):
            with self.assertRaises(SystemExit):
                module.main()
            kill.assert_not_called()

    def test_rofi_secondary_click_opens_actions_without_running_them(self):
        module = load_module()
        app = {'id': 'sample', 'name': 'Sample', 'iconPath': '/tmp/icon.svg',
               'windows': [{'address': '0xabc', 'minimized': False}]}
        output = io.StringIO()
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.dict(module.os.environ, {'ROFI_RETV': '10', 'ROFI_INFO': 'sample'}, clear=True), \
             patch.object(module, 'perform') as perform, redirect_stdout(output):
            module.rofi_rows()
        self.assertIn('Abrir segunda instância\0display\x1f<span foreground="#77c99a"><b>+</b></span>  Abrir segunda instância\x1finfo\x1faction:open:sample', output.getvalue())
        self.assertIn('Terminar tarefa\0display\x1f<span foreground="#e4b75c"><b>×</b></span>  Terminar tarefa\x1finfo\x1faction:terminate:0xabc', output.getvalue())
        self.assertIn('Desinstalar aplicação\0display\x1f<span foreground="#d98989"><b>−</b></span>  Desinstalar aplicação\x1finfo\x1faction:uninstall:sample', output.getvalue())
        self.assertIn('Sample\0display', output.getvalue())
        perform.assert_not_called()

    def test_repeated_right_click_does_not_activate_minimized_window(self):
        module = load_module()
        app = {'id': 'sample', 'name': 'Sample', 'iconPath': '/tmp/icon.svg',
               'windows': [{'address': '0xabc', 'minimized': True}]}
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.dict(module.os.environ, {'ROFI_RETV': '10', 'ROFI_INFO': 'sample',
                                            'ROFI_DATA': 'selected:sample'}, clear=True), \
             patch.object(module, 'perform') as perform:
            module.rofi_rows()
        perform.assert_not_called()

    def test_left_click_opens_application_or_executes_selected_action(self):
        module = load_module()
        app = {'id': 'sample', 'name': 'Sample', 'iconPath': '/tmp/icon.svg', 'windows': []}
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.dict(module.os.environ, {'ROFI_RETV': '1', 'ROFI_INFO': 'sample'}, clear=True), \
             patch.object(module, 'perform') as perform:
            module.rofi_rows()
        perform.assert_called_once_with('open', 'sample')
        running = dict(app, windows=[{'address': '0xabc', 'minimized': True}])
        with patch.object(module, 'catalog', return_value=[running]), \
             patch.dict(module.os.environ, {'ROFI_RETV': '1', 'ROFI_INFO': 'sample'}, clear=True), \
             patch.object(module, 'perform') as perform:
            module.rofi_rows()
        perform.assert_called_once_with('focus', '0xabc')
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.dict(module.os.environ, {'ROFI_RETV': '1', 'ROFI_INFO': 'action:nvidia:sample',
                                            'ROFI_DATA': 'selected:sample'}, clear=True), \
             patch.object(module, 'perform') as perform:
            module.rofi_rows()
        perform.assert_called_once_with('nvidia', 'sample')

    def test_executed_action_closes_only_its_rofi_parent(self):
        module = load_module()
        with patch.object(module, 'perform') as perform, \
             patch.object(module.os, 'getppid', return_value=123), \
             patch.object(module.os, 'readlink', return_value='/usr/bin/rofi'), \
             patch.object(module.os, 'kill') as kill:
            module.execute_and_close('open', 'sample')
        perform.assert_called_once_with('open', 'sample')
        kill.assert_called_once_with(123, module.signal.SIGTERM)
        with patch.object(module, 'perform'), \
             patch.object(module.os, 'getppid', return_value=123), \
             patch.object(module.os, 'readlink', return_value='/usr/bin/quickshell'), \
             patch.object(module.os, 'kill') as kill:
            module.execute_and_close('open', 'sample')
        kill.assert_not_called()

    def test_right_click_on_action_only_keeps_options_open(self):
        module = load_module()
        app = {'id': 'sample', 'name': 'Sample', 'iconPath': '/tmp/icon.svg', 'windows': []}
        output = io.StringIO()
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.dict(module.os.environ, {'ROFI_RETV': '10', 'ROFI_INFO': 'action:uninstall:sample',
                                            'ROFI_DATA': 'selected:sample'}, clear=True), \
             patch.object(module, 'perform') as perform, redirect_stdout(output):
            module.rofi_rows()
        self.assertIn('Desinstalar aplicação', output.getvalue())
        self.assertNotIn('Confirmar desinstalação', output.getvalue())
        perform.assert_not_called()

    def test_closed_app_has_only_uninstall_action(self):
        module = load_module()
        app = {'id': 'sample', 'name': 'Sample', 'iconPath': '/tmp/icon.svg', 'windows': []}
        output = io.StringIO()
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.dict(module.os.environ, {'ROFI_RETV': '10', 'ROFI_INFO': 'sample'}, clear=True), \
             redirect_stdout(output):
            module.rofi_rows()
        self.assertIn('Desinstalar aplicação', output.getvalue())
        self.assertNotIn('Abrir segunda instância', output.getvalue())
        self.assertNotIn('Terminar tarefa', output.getvalue())

    def test_hybrid_mode_offers_nvidia_launch_on_selected_application(self):
        module = load_module()
        app = {'id': 'sample', 'name': 'Sample', 'iconPath': '/tmp/icon.svg', 'windows': []}
        output = io.StringIO()
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.object(module, 'nvidia_on_demand', return_value=True), \
             patch.dict(module.os.environ, {'ROFI_RETV': '10', 'ROFI_INFO': 'sample'}, clear=True), \
             redirect_stdout(output):
            module.rofi_rows()
        self.assertIn('Abrir na NVIDIA\0display\x1f<span foreground="#77c99a"><b>◆</b></span>  Abrir na NVIDIA\x1finfo\x1faction:nvidia:sample', output.getvalue())

    def test_nvidia_action_is_limited_to_game_environments_in_hybrid_mode(self):
        module = load_module()
        with patch.object(module.Path, 'is_char_device', return_value=True), \
             patch.dict(module.os.environ, {'APX_GPU_POLICY': 'hybrid'}, clear=True):
            for name in ('apx-hytale', 'apx-minecraft'):
                with patch.object(module.Path, 'read_text', return_value=name):
                    self.assertTrue(module.nvidia_on_demand())
            for name in ('apx-steam', 'apx-faculdade', 'apx-hub'):
                with patch.object(module.Path, 'read_text', return_value=name):
                    self.assertFalse(module.nvidia_on_demand())
        with patch.object(module.Path, 'read_text', return_value='apx-hytale'), \
             patch.object(module.Path, 'is_char_device', return_value=True), \
             patch.dict(module.os.environ, {'APX_GPU_POLICY': 'nvidia'}, clear=True):
            self.assertFalse(module.nvidia_on_demand())

    def test_hybrid_nvidia_launch_passes_gpu_choice_into_flatpak(self):
        module = load_module()
        app = {'id': 'com.example.Game', 'name': 'Game',
               'path': '/home/apx/.local/share/flatpak/exports/share/applications/com.example.Game.desktop',
               'windows': []}
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.object(module, 'nvidia_on_demand', return_value=True), \
             patch.object(module.subprocess, 'Popen') as popen, \
             patch.object(module, 'record_use'):
            module.perform('nvidia', app['id'])
        command = popen.call_args.args[0]
        self.assertEqual(command[:3], ['/usr/bin/flatpak', 'run', '--user'])
        self.assertIn('--env=__NV_PRIME_RENDER_OFFLOAD=1', command)
        self.assertIn('--env=__GLX_VENDOR_LIBRARY_NAME=nvidia', command)
        self.assertIn('--env=__VK_LAYER_NV_optimus=NVIDIA_only', command)
        self.assertEqual(command[-1], app['id'])

    def test_hybrid_nvidia_launch_passes_gpu_choice_into_native_app(self):
        module = load_module()
        app = {'id': 'sample', 'name': 'Sample', 'path': '/usr/share/applications/sample.desktop', 'windows': []}
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.object(module, 'nvidia_on_demand', return_value=True), \
             patch.object(module.subprocess, 'Popen') as popen, \
             patch.object(module, 'record_use'):
            module.perform('nvidia', app['id'])
        self.assertEqual(popen.call_args.args[0], ['/usr/bin/gtk-launch', 'sample'])
        self.assertEqual(popen.call_args.kwargs['env']['__NV_PRIME_RENDER_OFFLOAD'], '1')

    def test_uninstall_requires_inline_confirmation_and_keeps_terminal_open(self):
        module = load_module()
        app = {'id': 'sample', 'name': 'Sample', 'path': '/usr/share/applications/sample.desktop',
               'iconPath': '/tmp/icon.svg', 'windows': []}
        output = io.StringIO()
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.dict(module.os.environ, {'ROFI_RETV': '1', 'ROFI_INFO': 'action:uninstall:sample',
                                            'ROFI_DATA': 'selected:sample'}, clear=True), \
             patch.object(module, 'perform') as perform, redirect_stdout(output):
            module.rofi_rows()
        self.assertIn('Confirmar desinstalação', output.getvalue())
        perform.assert_not_called()
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.object(module.subprocess, 'Popen') as popen:
            module.perform('uninstall', 'sample')
        self.assertIn('--hold', popen.call_args.args[0])
        self.assertIs(popen.call_args.kwargs['stdout'], module.subprocess.DEVNULL)
        self.assertIs(popen.call_args.kwargs['stderr'], module.subprocess.DEVNULL)

    def test_rofi_passes_selected_row_as_argument(self):
        module = load_module()
        app = {'id': 'sample', 'name': 'Sample', 'iconPath': '/tmp/icon.svg',
               'windows': [{'address': '0xabc', 'minimized': False}]}
        output = io.StringIO()
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.dict(module.os.environ, {'ROFI_RETV': '10', 'ROFI_INFO': 'sample'}, clear=True), \
             patch.object(module.sys, 'argv', ['apx-window-apps-v1', 'Sample']), \
             redirect_stdout(output):
            module.main()
        self.assertIn('Abrir segunda instância', output.getvalue())

    def test_focus_restores_minimized_window_to_active_workspace(self):
        module = load_module()
        app = {'id': 'sample', 'windows': [{'address': '0xabc', 'pid': 123, 'minimized': True}]}
        with patch.object(module, 'catalog', return_value=[app]), \
             patch.object(module.subprocess, 'check_output', return_value=b'{"id":2}'), \
             patch.object(module, 'hyprland_eval') as evaluate, \
             patch.object(module, 'record_use'):
            module.perform('focus', '0xabc')
        self.assertIn('workspace=2', evaluate.call_args_list[0].args[0])
        self.assertIn('silent=true', evaluate.call_args_list[0].args[0])
        self.assertIn('hl.dsp.focus', evaluate.call_args_list[1].args[0])
        self.assertIn('address:0xabc', evaluate.call_args_list[1].args[0])

    def test_hyprland_error_does_not_become_rofi_row(self):
        module = load_module()
        result = module.subprocess.CompletedProcess([], 0,
            'error: [string "return hl.dispatch(...)" ...', '')
        output = io.StringIO()
        with patch.object(module.subprocess, 'run', return_value=result), \
             redirect_stdout(output):
            with self.assertRaisesRegex(RuntimeError, 'Não foi possível ativar'):
                module.hyprland_eval('hl.dispatch(hl.dsp.focus({window="address:0xabc"}))')
        self.assertEqual(output.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
