import importlib.machinery
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-audio-categories-v1'
loader = importlib.machinery.SourceFileLoader('apx_audio_categories', str(SOURCE))
spec = importlib.util.spec_from_loader(loader.name, loader)
audio = importlib.util.module_from_spec(spec)
loader.exec_module(audio)


def node(ident, serial, role=None, media_class='Stream/Output/Audio'):
    props = {'media.class': media_class, 'object.serial': serial}
    if role: props['media.role'] = role
    return {'type': 'PipeWire:Interface:Node', 'id': ident, 'info': {'props': props}}


class AudioCategoriesTests(unittest.TestCase):
    def test_output_streams_are_classified_without_touching_capture_or_sinks(self):
        found = audio.streams([node(1, 101, 'Music'), node(2, 102, 'Notification'),
                               node(3, 103, media_class='Stream/Input/Audio'),
                               node(4, 104, media_class='Audio/Sink')])
        self.assertEqual(found, {'101': (1, 'media'), '102': (2, 'notifications')})

    @patch.object(audio.subprocess, 'run')
    def test_new_streams_receive_saved_levels_once(self, run):
        run.return_value.returncode = 0
        data = {'levels': {'media': 65, 'notifications': 20}, 'seen': {}}
        current = {'101': (7, 'media'), '102': (8, 'notifications')}
        audio.apply(data, current)
        self.assertEqual([call.args[0][-2:] for call in run.call_args_list],
                         [['7', '65%'], ['8', '20%']])
        audio.apply(data, current)
        self.assertEqual(run.call_count, 2)
        audio.apply(data, current, changed='media')
        self.assertEqual(run.call_count, 3)
        self.assertEqual(run.call_args.args[0][-2:], ['7', '65%'])


if __name__ == '__main__':
    unittest.main()
