"""MPRIS positions are seconds, seeks must target the still-current track."""
from pathlib import Path
import importlib.machinery,importlib.util,sys,types,unittest,io
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]

def helper():
    p=ROOT/'config/environment-shell-v1/local/bin/apx-desktop-activity-v1'
    loader=importlib.machinery.SourceFileLoader('media_trial',str(p));spec=importlib.util.spec_from_loader(loader.name,loader);module=importlib.util.module_from_spec(spec);loader.exec_module(module);return module

class MediaProgressTests(unittest.TestCase):
    def setUp(self):
        self.m=helper()
        self.modules=patch.dict(sys.modules,{'gi':types.SimpleNamespace(), 'gi.repository':types.SimpleNamespace(GLib=types.SimpleNamespace(Variant=lambda signature,value:(signature,value)))})
        self.modules.start();self.addCleanup(self.modules.stop)
        self.props={'PlaybackStatus':'Playing','Position':42000000,'Rate':1.5,'CanSeek':True,'Metadata':{'mpris:length':180000000,'mpris:trackid':'/test/one','xesam:title':'Teste'}}
    def test_player_units_and_capabilities(self):
        def call(connection,destination,path,interface,method,*args):
            return (['org.mpris.MediaPlayer2.test'],) if method=='ListNames' else (self.props,)
        with patch.object(self.m,'bus',return_value=object()),patch.object(self.m,'call',side_effect=call):
            result=self.m.players()[0]
        self.assertEqual((result['position'],result['length'],result['rate']),(42,180,1.5));self.assertTrue(result['can_seek'])
        self.assertEqual(result['track_id'],'/test/one')
    def test_seek_uses_track_id_and_microseconds(self):
        calls=[]
        def call(*args):
            calls.append(args)
            return (self.props,) if args[4]=='GetAll' else ()
        with patch.object(self.m,'bus',return_value=object()),patch.object(self.m,'call',side_effect=call),patch.object(self.m,'players',return_value=[]),patch('sys.stdout',new=io.StringIO()):
            self.m.main(['seek','org.mpris.MediaPlayer2.test','/test/one','70','180'])
        self.assertEqual(calls[-1][4:6],('SetPosition',('(ox)',('/test/one',70000000))))
    def test_stale_track_and_nonfinite_positions_are_rejected(self):
        with patch.object(self.m,'bus',return_value=object()),patch.object(self.m,'call',return_value=(self.props,)) as call:
            with self.assertRaises(ValueError):self.m.main(['seek','org.mpris.MediaPlayer2.test','/test/stale','70','180'])
            self.assertEqual(call.call_count,1)
            for value in ['nan','inf','-1','181']:
                with self.assertRaises(ValueError):self.m.main(['seek','org.mpris.MediaPlayer2.test','/test/one',value,'180'])

    def test_transport_does_not_wait_for_notification_history(self):
        with patch.object(self.m,'bus',return_value=object()), patch.object(self.m,'call') as call, patch.object(self.m,'players',return_value=[]) as players, patch.object(self.m,'notifications',side_effect=AssertionError('media must not read notifications')), patch('sys.stdout',new=io.StringIO()):
            self.m.main(['media','org.mpris.MediaPlayer2.test','play-pause'])
            self.assertEqual(call.call_args.args[4],'PlayPause')
            players.assert_called_once()

    def test_start_and_end_seek_current_track(self):
        for position in (0,180):
            with self.subTest(position=position), patch.object(self.m,'bus',return_value=object()), patch.object(self.m,'call',side_effect=[(self.props,),()]) as call, patch.object(self.m,'players',return_value=[]), patch('sys.stdout',new=io.StringIO()):
                self.m.main(['seek','org.mpris.MediaPlayer2.test','/test/one',str(position),'180'])
                self.assertEqual(call.call_args.args[4:6],('SetPosition',('(ox)',('/test/one',position*1000000))))

    def test_progress_sampling_drift_is_smoothed_but_seeks_and_pause_are_preserved(self):
        import shutil, subprocess
        if not shutil.which('node'): self.skipTest('node unavailable')
        source=(ROOT/'config/environment-shell-v1/quickshell/apx/DesktopActivity.qml').read_text()
        position=source[source.index('    function position('):source.index('    function timeLabel(')]
        accept=source[source.index('    function accept('):source.index('    function refresh(')]
        script="""
const assert=require('node:assert/strict');
let clock=12000;
let state={players:[{name:'test',track_id:'/one',position:10,sampled_at:10000,status:'Playing',rate:1,length:100}],notifications:[{id:1}]};
const activity={busy:false};
function settlePlaybackFeedback() {}
Date.now=()=>12000;
"""+position+accept+"""
const player={name:'test',track_id:'/one',position:11.9,sampled_at:12000,status:'Playing',rate:1,length:100};
accept(JSON.stringify({players:[player]}));
assert.equal(state.players[0].position,12);
assert.equal(state.notifications.length,1);
accept(JSON.stringify({players:[{...player,position:80}]}));
assert.equal(state.players[0].position,80);
accept(JSON.stringify({players:[{...player,status:'Paused',position:80.15}]}));
assert.equal(state.players[0].position,80.15);
assert.equal(state.players[0].status,'Paused');
"""
        subprocess.run(['node','-e',script],check=True,capture_output=True,text=True)

    def test_transport_feedback_survives_stale_reports_and_rapid_clicks(self):
        import shutil, subprocess
        if not shutil.which('node'): self.skipTest('node unavailable')
        source=(ROOT/'config/environment-shell-v1/quickshell/apx/DesktopActivity.qml').read_text()
        feedback=source[source.index('    function clearPlaybackFeedback('):source.index('    property Timer feedbackTimeout:')]
        icon=source[source.index('    function playbackIcon('):source.index('    function position(')]
        position=source[source.index('    function position('):source.index('    function timeLabel(')]
        accept=source[source.index('    function accept('):source.index('    function refresh(')]
        exited=source[source.index('        onExited: function(code, status)'):source.index('        stdout: StdioCollector',source.index('        onExited: function(code, status)'))].replace('onExited: function(code, status)','function exited(code, status)',1)
        script="""
const assert=require('node:assert/strict');
let pendingPlayer='',pendingStatus='',pendingTrack='',pendingSince=0,sentPlayer='',sentStatus='',busy=false,error='',clock=1000;
let state={players:[{name:'test',track_id:'/one',status:'Playing',can_control:true,sampled_at:900,position:10,length:120,rate:1}]};
const readProcess={running:false};
const feedbackTimeout={restart(){},stop(){}};
const actionProcess={command:[],set running(value){busy=value;}};
const Qt={callLater(callback){callback();}};
function refresh() {}
Date.now=()=>1000;
"""+feedback+icon+position+accept+"""
const activity={get busy(){return busy;},get sentPlayer(){return sentPlayer;},set sentPlayer(v){sentPlayer=v;},get sentStatus(){return sentStatus;},set sentStatus(v){sentStatus=v;},get pendingPlayer(){return pendingPlayer;},get pendingStatus(){return pendingStatus;},sendPlayback,settlePlaybackFeedback,clearPlaybackFeedback,refresh};
"""+exited+"""
togglePlayback(state.players[0]);
assert.equal(playbackIcon(state.players[0]),'play');
assert.equal(actionProcess.command.at(-1),'pause');
togglePlayback(state.players[0]);
assert.equal(playbackIcon(state.players[0]),'pause');
assert.equal(actionProcess.command.at(-1),'pause');
accept(JSON.stringify({players:[{...state.players[0],status:'Paused',sampled_at:1005}]}));
assert.equal(playbackIcon(state.players[0]),'pause');
busy=false; exited(0,0);
assert.equal(actionProcess.command.at(-1),'play');
assert.equal(busy,true);
accept(JSON.stringify({players:[{...state.players[0],status:'Playing',sampled_at:1007}]}));
busy=false; exited(0,0);
assert.equal(pendingPlayer,'');
assert.equal(playbackIcon(state.players[0]),'pause');
accept(JSON.stringify({players:[{...state.players[0],status:'Paused',sampled_at:1006}]}));
assert.equal(playbackIcon(state.players[0]),'pause');
togglePlayback(state.players[0]);
assert.equal(playbackIcon(state.players[0]),'play');
busy=false; exited(1,0);
assert.equal(pendingPlayer,'');
assert.equal(playbackIcon(state.players[0]),'pause');
"""
        subprocess.run(['node','-e',script],check=True,capture_output=True,text=True)

    def test_finished_browser_media_is_distinct_from_ordinary_pause(self):
        import shutil, subprocess
        if not shutil.which('node'): self.skipTest('node unavailable')
        source=(ROOT/'config/environment-shell-v1/quickshell/apx/DesktopActivity.qml').read_text()
        function=source[source.index('    function hasMedia('):source.index('    function playbackIcon(')]
        script="const assert=require('node:assert/strict');"+function+"""
assert.equal(hasMedia({status:'Paused',position:10,length:120}),true);
assert.equal(hasMedia({status:'Paused',position:119.9,length:120}),true);
assert.equal(hasMedia({status:'Paused',position:120,length:120}),false);
assert.equal(hasMedia({status:'Stopped',position:0,length:120}),false);
assert.equal(hasMedia({status:'Paused',position:0,length:0}),true);
assert.equal(hasMedia({status:'Playing',position:120,length:120}),true);
"""
        subprocess.run(['node','-e',script],check=True,capture_output=True,text=True)
