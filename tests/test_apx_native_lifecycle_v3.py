import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import contextmanager
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from apx_native_instances_v3 import plan_second_windows
from test_apx_native_instances_v3 import fixture

PATH = Path(__file__).resolve().parents[1] / 'scripts/physical-pilot/apx-native-lifecycle-v3.py'
SPEC = importlib.util.spec_from_file_location('native_lifecycle_v3', PATH)
LIFECYCLE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LIFECYCLE)


class NativeLifecycleTests(unittest.TestCase):
    def test_real_efibootmgr_loader_format_matches_exact_entry(self):
        partuuid = '9625F250-9ACC-453A-AE63-0C863ADE440F'
        label = 'APX native relocate 2770478b'
        loader = '\\EFI\\APX\\native-v3-2770478b-relocate.efi'
        firmware = ('Boot0000* ' + label + '\tHD(1,GPT,' + partuuid.lower()
                    + ',0x800,0x200000)/' + loader + '\n')
        self.assertEqual(LIFECYCLE.find_matching_entry(firmware, 1, partuuid,
                         label, loader), '0000')
        with self.assertRaisesRegex(ValueError, 'aliases'):
            LIFECYCLE.find_matching_entry(firmware.replace(label, 'Other label'),
                                          1, partuuid, label, loader)

    def test_delete_only_new_slot_and_resume_after_interrupted_wipe(self):
        table, legacy, args = fixture()
        plan = plan_second_windows(table, legacy, **args)
        generation = plan['new']['generation']
        after = plan['after']['partitions']
        def record(name, gen, windows, esp, entry):
            return {'schema': 3, 'profile': 'apx-native-instance-v3', 'name': name,
                    'generation': gen, 'state': 'ready', 'system_kind': 'windows-native',
                    'disk_id': plan['disk_id'], 'disk_serial': plan['disk_serial'],
                    'windows_partuuid': windows['uuid'], 'start_sector': windows['start'],
                    'size_sectors': windows['size'], 'esp_partuuid': esp['uuid'],
                    'linux_boot_entry': '0005', 'windows_boot_entry': entry,
                    'efi_path': '/EFI/Microsoft/Boot/bootmgfw.efi'}
        original = record('windows', legacy['generation'], after[2], after[0], '0006')
        selected = record(plan['new']['name'], generation, after[4], after[5], '0007')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            instances = root / 'instances-v3'; instances.mkdir()
            LIFECYCLE.write(instances / 'windows.json', original)
            LIFECYCLE.write(instances / (selected['name']+'.json'), selected)
            job = root / 'job'; job.mkdir()
            LIFECYCLE.write(job / 'plan.json', plan)
            lock = root / 'lock'; lock.write_text('owned-token\n')
            pending = root / 'pending-v3.json'
            firmware = {'entry': True}
            def command(*args, **kwargs):
                if args == ('efibootmgr', '-v'):
                    line = (f"Boot0007* APX {selected['name']} HD(6,GPT,{after[5]['uuid']},0,1)"
                            '/File(\\EFI\\Microsoft\\Boot\\bootmgfw.efi)\n') if firmware['entry'] else ''
                    return 'BootCurrent: 0005\nBootOrder: 0005,0006,0007\n' + line
                if args == ('efibootmgr', '-b', '0007', '-B'):
                    firmware['entry'] = False; return ''
                raise AssertionError(args)
            calls = []
            def interrupted(path, size, partuuid, number):
                calls.append(number)
                if number == 6 and calls.count(6) == 1:
                    raise OSError('simulated wipe interruption')
            with mock.patch.object(LIFECYCLE, 'target'), \
                 mock.patch.object(LIFECYCLE, 'ROOT', root), \
                 mock.patch.object(LIFECYCLE, 'PENDING', pending), \
                 mock.patch.object(LIFECYCLE, 'LOCK', lock), \
                 mock.patch.object(LIFECYCLE, 'job_path', return_value=job), \
                 mock.patch.object(LIFECYCLE, 'layout', return_value=plan['after']), \
                 mock.patch.object(LIFECYCLE, 'command', side_effect=command), \
                 mock.patch.object(LIFECYCLE, 'wipe_block_partition', side_effect=interrupted), \
                 mock.patch.object(LIFECYCLE, 'state'):
                with self.assertRaisesRegex(OSError, 'simulated'):
                    LIFECYCLE.delete_instance(generation, 'owned-token')
                self.assertTrue(pending.exists())
                self.assertEqual(json.loads((instances/(selected['name']+'.json')).read_text())['state'], 'deleting')
                self.assertFalse((root/'free-slot-v3.json').exists())
                LIFECYCLE.delete_instance(generation, 'owned-token')
            self.assertEqual(calls, [5, 6, 5, 6])
            self.assertFalse(pending.exists())
            self.assertFalse((instances/(selected['name']+'.json')).exists())
            self.assertTrue((root/'retired-v3'/(selected['name']+'-'+generation+'.json')).exists())
            self.assertEqual(json.loads((root/'free-slot-v3.json').read_text())['state'], 'free')
            self.assertEqual(json.loads((instances/'windows.json').read_text()), original)

    def test_measured_capacity_uses_allocated_filesystem_space(self):
        table, legacy, args = fixture()
        plan = plan_second_windows(table, legacy, **args)
        block = 4096
        allowed = plan['apx_payload_bytes'] - 16 * 1024**3
        usage = mock.Mock(f_blocks=300 * 1024**3 // block,
                          f_bfree=(300 * 1024**3 - allowed) // block,
                          f_frsize=block)
        with mock.patch.object(LIFECYCLE.os, 'statvfs', return_value=usage):
            proof = LIFECYCLE.measured_capacity(plan, Path('/unused'))
        self.assertEqual(proof['used_bytes'], allowed)
        self.assertEqual(proof['plan_sha256'], plan['plan_sha256'])
        usage.f_bfree -= 1
        with mock.patch.object(LIFECYCLE.os, 'statvfs', return_value=usage):
            with self.assertRaisesRegex(ValueError, 'cópia'):
                LIFECYCLE.measured_capacity(plan, Path('/unused'))

    def test_activation_refuses_stale_or_full_capacity_before_efi_write(self):
        table, legacy, args = fixture()
        plan = plan_second_windows(table, legacy, **args)
        generation = plan['new']['generation']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            job = root / 'job'; job.mkdir()
            LIFECYCLE.write(job / 'plan.json', plan)
            record = {'generation': generation, 'stage': 'prepared', 'target': 'windows-games'}
            LIFECYCLE.write(job / 'job.json', record)
            pending = root / 'pending.json'; LIFECYCLE.write(pending, record)
            lock = root / 'lock'; lock.write_text('owned-token\n')
            proof = {'schema': 3, 'profile': 'apx-native-measured-capacity-v3',
                     'plan_sha256': plan['plan_sha256'], 'apx_payload_bytes': plan['apx_payload_bytes'],
                     'headroom_bytes': 16 * 1024**3, 'used_bytes': 120 * 1024**3}
            LIFECYCLE.write(job / 'capacity.json', proof)
            patches = (mock.patch.object(LIFECYCLE, 'target'),
                       mock.patch.object(LIFECYCLE, 'LOCK', lock),
                       mock.patch.object(LIFECYCLE, 'PENDING', pending),
                       mock.patch.object(LIFECYCLE, 'job_path', return_value=job),
                       mock.patch.object(LIFECYCLE, 'layout', return_value=plan['before']),
                       mock.patch.object(LIFECYCLE.shutil, 'copyfile'))
            with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5] as copy, \
                 mock.patch.object(LIFECYCLE, 'measured_capacity', return_value=proof):
                changed = dict(proof, plan_sha256='0' * 64)
                LIFECYCLE.write(job / 'capacity.json', changed)
                with self.assertRaisesRegex(ValueError, 'capacity proof'):
                    LIFECYCLE.activate(generation, 'owned-token')
                copy.assert_not_called()
                LIFECYCLE.write(job / 'capacity.json', proof)
                with mock.patch.object(LIFECYCLE, 'measured_capacity', side_effect=ValueError('APX full')):
                    with self.assertRaisesRegex(ValueError, 'APX full'):
                        LIFECYCLE.activate(generation, 'owned-token')
                copy.assert_not_called()

    def test_preparation_records_capacity_only_after_backup_and_recovery_images(self):
        table, legacy, args = fixture()
        plan = plan_second_windows(table, legacy, **args)
        generation = plan['new']['generation']
        preview = {'plan': plan, 'target': plan['new']['name'],
                   'description': 'Novo Windows', 'size_gib': plan['new']['size_gib']}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            job = root / 'job'
            pending = root / 'pending.json'
            lock = root / 'lock'; lock.write_text('owned-token\n')
            media = root / 'media'; (media / 'sources').mkdir(parents=True)
            (media / 'sources/boot.wim').write_bytes(b'fixture-wim')
            assets = {'script': 'script', 'contract': 'contract', 'media_directory': 'APX\\Native'}
            events = []
            def backup(*_args, **_kwargs):
                events.append('backup')
                (job / 'images').mkdir()
            def build(_job, rollback=False):
                events.append('rollback-image' if rollback else 'migration-image')
            def measure(_plan, _job):
                events.append('capacity')
                return {'schema': 3, 'profile': 'apx-native-measured-capacity-v3',
                        'plan_sha256': plan['plan_sha256'], 'used_bytes': 120 * 1024**3,
                        'apx_payload_bytes': plan['apx_payload_bytes'], 'headroom_bytes': 16 * 1024**3}
            @contextmanager
            def mounted(_device):
                yield media
            original_trusted = LIFECYCLE.trusted
            original_read_text = Path.read_text
            def trusted(path, *args, **kwargs):
                if path.name == generation + '.json': return preview
                return original_trusted(path, *args, **kwargs)
            planner = mock.Mock(preview=mock.Mock(return_value=preview))
            builder = mock.Mock(build=build)
            def module(name): return planner if name == 'apx-native-windows-plan-v3' else builder
            with mock.patch.object(LIFECYCLE, 'target'), \
                     mock.patch.object(LIFECYCLE, 'LOCK', lock), \
                     mock.patch.object(LIFECYCLE, 'PENDING', pending), \
                     mock.patch.object(LIFECYCLE, 'job_path', return_value=job), \
                     mock.patch.object(LIFECYCLE, 'layout', return_value=plan['before']), \
                     mock.patch.object(LIFECYCLE, 'trusted', side_effect=trusted), \
                     mock.patch.object(LIFECYCLE, 'module', side_effect=module), \
                     mock.patch.object(LIFECYCLE, 'display_drivers', return_value=['nv_fixture', 'u_fixture']), \
                     mock.patch.object(LIFECYCLE, 'render', return_value=assets), \
                     mock.patch.object(LIFECYCLE, 'prepare_images', side_effect=backup), \
                     mock.patch.object(LIFECYCLE, 'mounted', mounted), \
                     mock.patch.object(LIFECYCLE, 'command', return_value=''), \
                     mock.patch.object(LIFECYCLE, 'measured_capacity', side_effect=measure), \
                     mock.patch.object(LIFECYCLE, 'state'), \
                 mock.patch.object(Path, 'read_text', autospec=True, side_effect=lambda path, *a, **k: 'fixture' if path == Path('/usr/share/apx/native-windows-lifecycle-v1/winpe/apx-media.cmd') else original_read_text(path, *a, **k)):
                LIFECYCLE.prepare(generation, 'owned-token')
            self.assertEqual(events, ['backup', 'migration-image', 'rollback-image', 'capacity'])
            self.assertEqual(json.loads((job / 'capacity.json').read_text())['plan_sha256'], plan['plan_sha256'])
            self.assertEqual(json.loads(pending.read_text())['stage'], 'prepared')

    def test_retry_only_rearms_exact_failed_new_installer(self):
        table, legacy, args = fixture()
        plan = plan_second_windows(table, legacy, **args)
        generation = plan['new']['generation']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            job, media = root / 'job', root / 'media'
            job.mkdir();media.mkdir()
            (job / 'plan.json').write_text(json.dumps(plan));(job / 'plan.json').chmod(0o400)
            assets = {'media_directory': 'APX\\Native\\windows-games\\' + generation}
            (job / 'assets.json').write_text(json.dumps(assets));(job / 'assets.json').chmod(0o400)
            status = media / assets['media_directory'].replace('\\', '/') / 'install-status-v3.ini'
            status.parent.mkdir(parents=True)
            status.write_text('profile=apx-native-windows-install-status-v3\n'
                              'generation=' + generation + '\nplan_sha256=' + plan['plan_sha256'] + '\n'
                              'status=failed\nerror=APX-APPLY-01\nstep=apply-windows-11-pro\n')
            pending = root / 'pending.json'
            pending.write_text(json.dumps({'generation': generation, 'target': 'windows-games',
                                           'stage': 'installing', 'error': 'setup failed',
                                           'install_failure_kind': 'winpe-failed',
                                           'setup_entry': '0008', 'plan_sha256': plan['plan_sha256']}))
            pending.chmod(0o400)
            lock = root / 'lock';lock.write_text('owned-token\n')
            setup_uuid = plan['after']['partitions'][3]['uuid']
            firmware = ('BootCurrent: 0005\nBootOrder: 0005,0008\n'
                        f'Boot0008* APX setup {generation[:8]} HD(4,GPT,{setup_uuid},0,1)/File(\\EFI\\BOOT\\BOOTX64.EFI)\n')
            @contextmanager
            def mounted(_device):
                yield media
            with mock.patch.object(LIFECYCLE, 'target'), \
                 mock.patch.object(LIFECYCLE, 'LOCK', lock), \
                 mock.patch.object(LIFECYCLE, 'PENDING', pending), \
                 mock.patch.object(LIFECYCLE, 'job_path', return_value=job), \
                 mock.patch.object(LIFECYCLE, 'layout', return_value=plan['after']), \
                 mock.patch.object(LIFECYCLE, 'mounted', mounted), \
                 mock.patch.object(LIFECYCLE, 'command', return_value=firmware) as command, \
                 mock.patch.object(LIFECYCLE, 'state'), \
                 mock.patch.object(LIFECYCLE, 'reboot_entry') as reboot:
                LIFECYCLE.retry_install(generation, 'owned-token')
                reboot.assert_called_once_with('0008')
                command.assert_called_once_with('efibootmgr', '-v')
            updated = json.loads(pending.read_text())
            self.assertEqual(updated['install_retries'], 1)
            self.assertNotIn('error', updated)

    def test_exact_existing_firmware_entry_is_reused_without_aliases(self):
        uuid = '11111111-2222-4333-8444-555555555555'
        loader = '\\EFI\\Microsoft\\Boot\\bootmgfw.efi'
        label = 'APX windows-games'
        line = f'Boot0007* {label} HD(6,GPT,{uuid},0,1)/File({loader})'
        self.assertEqual(LIFECYCLE.find_matching_entry(line, 6, uuid, label, loader), '0007')
        for changed in (line.replace('HD(6,', 'HD(1,'),
                        line.replace(label, 'APX different'),
                        line.replace(uuid, 'aaaaaaaa-2222-4333-8444-555555555555')):
            with self.assertRaises(ValueError):
                LIFECYCLE.find_matching_entry(changed, 6, uuid, label, loader)
        with self.assertRaises(ValueError):
            LIFECYCLE.find_matching_entry(line + '\n' + line.replace('0007', '0008'), 6, uuid, label, loader)

    def test_windows_installer_firmware_entry_is_reused_only_for_new_esp(self):
        uuid = '10783707-92f8-5f8a-9407-1c4fb92ab0ea'
        loader = '\\EFI\\Microsoft\\Boot\\bootmgfw.efi'
        label = 'APX windows-testes'
        line = f'Boot0000* Windows Boot Manager\tHD(6,GPT,{uuid},0x306d9000,0x100000)/{loader}RC'
        self.assertEqual(LIFECYCLE.find_matching_entry(line, 6, uuid, label, loader,
                         allow_windows_manager=True), '0000')
        with self.assertRaisesRegex(ValueError, 'aliases'):
            LIFECYCLE.find_matching_entry(line, 6, uuid, label, loader)
        self.assertIsNone(LIFECYCLE.find_matching_entry(line.replace('HD(6,', 'HD(1,'),
                          6, uuid, label, loader, allow_windows_manager=True))
        for changed in (line.replace(uuid, 'aaaaaaaa-2222-4333-8444-555555555555'),
                        line.replace('Windows Boot Manager', 'Unrelated manager')):
            with self.assertRaises(ValueError):
                LIFECYCLE.find_matching_entry(changed, 6, uuid, label, loader,
                                              allow_windows_manager=True)
        original = 'Boot0006* Windows Boot Manager\tHD(1,GPT,9625f250-9acc-453a-ae63-0c863ade440f,0,1)/'+loader
        self.assertEqual(LIFECYCLE.find_matching_entry(original+'\n'+line, 6, uuid, label, loader,
                         allow_windows_manager=True), '0000')

    def test_restore_installer_preserves_reused_windows_boot_entry(self):
        table, legacy, args = fixture()
        plan = plan_second_windows(table, legacy, **args)
        uuid = plan['new']['esp_partuuid']
        loader = '\\EFI\\Microsoft\\Boot\\bootmgfw.efi'
        firmware = f'Boot0000* Windows Boot Manager\tHD(6,GPT,{uuid},0,1)/{loader}RC\n'
        record = {'stage':'installing','setup_entry':'0000','target':plan['new']['name'],
                  'generation':plan['new']['generation']}
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            LIFECYCLE.write(job/'plan.json', plan)
            with mock.patch.object(LIFECYCLE, 'command', return_value=firmware) as command:
                LIFECYCLE.restore_installer(job, record)
                command.assert_called_once_with('efibootmgr', '-v')
            with mock.patch.object(LIFECYCLE, 'command', return_value=firmware.replace(uuid, 'aaaaaaaa-2222-4333-8444-555555555555')):
                with self.assertRaises(ValueError):
                    LIFECYCLE.restore_installer(job, record)
