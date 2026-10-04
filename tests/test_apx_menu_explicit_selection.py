from pathlib import Path
import shutil
import subprocess
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/quickshell/apx/shell.qml'

@unittest.skipUnless(shutil.which('node'), 'Node required for real menu state transitions')
class ExplicitSelectionTests(unittest.TestCase):
    def test_focus_does_not_commit_and_enter_selects_before_environment_open(self):
        source = SOURCE.read_text()
        names = ['setCalendarKeyboardAction', 'selectCalendarDate', 'activateCalendarKeyboardFocus',
                 'moveEnvironmentFocus', 'activateEnvironmentFocus', 'selectEnvironment']
        functions = []
        for name in names:
            start = source.index('    function ' + name + '(')
            end = source.index('\n    function ', start + 1)
            functions.append(source[start:end])
        script = '''const assert = require('node:assert/strict');
let calendarDate = new Date(2026, 8, 14), calendarSelectedDateKey = '';
let calendarFocusAction = {}, environmentFocusIndex = -1;
let environmentManagementBusy = false, environmentMetadataBusy = false;
let environmentDeleteConfirm = false, environmentEditOpen = false;
let selectedEnvironmentName = '', selectedEnvironmentGeneration = '', opens = 0;
let environmentCatalog = [{name:'test-one', generation:'one'}, {name:'test-two', generation:'two'}];
function dateKey(d) {return [d.getFullYear(),d.getMonth()+1,d.getDate()].join('-')}
function environmentIsOpenable(item) {return !!item}
function openSelectedEnvironment() {opens++}
''' + '\n'.join(functions) + '''
setCalendarKeyboardAction({kind:'date', key:'2026-9-15'});
assert.equal(calendarDate.getDate(),14);
assert.equal(calendarSelectedDateKey,'');
activateCalendarKeyboardFocus();
assert.equal(calendarDate.getDate(),15);
assert.equal(calendarSelectedDateKey,'2026-9-15');
setCalendarKeyboardAction({kind:'date',key:'2026-9-16'});
assert.equal(calendarSelectedDateKey,'2026-9-15');
moveEnvironmentFocus(1);
assert.equal(selectedEnvironmentName,'');
activateEnvironmentFocus();
assert.equal(selectedEnvironmentName,'test-one');
assert.equal(opens,0);
moveEnvironmentFocus(1);
assert.equal(selectedEnvironmentName,'test-one');
activateEnvironmentFocus();
assert.equal(selectedEnvironmentName,'test-two');
assert.equal(opens,0);
activateEnvironmentFocus();
assert.equal(opens,1);
'''
        subprocess.run(['node', '-e', script], check=True, capture_output=True, text=True)
