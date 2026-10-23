import json,os,signal,subprocess,time
from pathlib import Path
OUT=Path(__file__).resolve().parent
pid=1234
stage=Path(f'/proc/{pid}/root/run/apx/multimonitor-check')
runtime=Path(f'/proc/{pid}/root/run/apx/session-1000')
before={p.name for p in (runtime/'hypr').iterdir()}
prefix=['nsenter','-t',str(pid),'-U','-m','-p','-n','--','setpriv','--reuid=1000','--regid=1000','--clear-groups','env','HOME=/home/apx','XDG_RUNTIME_DIR=/run/apx/session-1000']
log=open(OUT/'nested-hyprland-final.log','w')
process=subprocess.Popen(prefix+['WAYLAND_DISPLAY=wayland-1','AQ_BACKEND=wayland','timeout','45','Hyprland','-c','/run/apx/multimonitor-check/hyprland.lua'],stdout=log,stderr=log,start_new_session=True)
shell=None
try:
    for _ in range(100):
        new=[p.name for p in (runtime/'hypr').iterdir() if p.name not in before and (p/'.socket.sock').is_socket()]
        if len(new)==1:break
        time.sleep(.05)
    assert len(new)==1
    prefix+=['WAYLAND_DISPLAY=wayland-2','HYPRLAND_INSTANCE_SIGNATURE='+new[0]]
    def run(args):
        r=subprocess.run(prefix+args,check=True,capture_output=True,text=True,timeout=4)
        return r.stdout
    def ctl(*args):return run(['hyprctl',*args])
    assert not ctl('configerrors').strip()
    assert ctl('output','create','headless').strip()=='ok'
    assert ctl('output','create','headless').strip()=='ok'
    assert ctl('eval','hl.monitor({output="WAYLAND-1",disabled=true})').strip()=='ok'
    layouts={}
    for side in ['left','right']:
        code='hl.monitor({output="",mode="1280x720",position="auto-'+side+'",scale=1}); hl.monitor({output="HEADLESS-1",mode="1280x720",position="0x0",scale=1})'
        assert ctl('eval',code).strip()=='ok'
        time.sleep(.2)
        monitors=json.loads(ctl('-j','monitors'));layouts[side]=monitors
        first=next(m for m in monitors if m['name']=='HEADLESS-1')
        second=next(m for m in monitors if m['name']=='HEADLESS-2')
        assert second['x']<first['x'] if side=='left' else second['x']>first['x']
        assert all(m['mirrorOf']=='none' for m in monitors)
    (OUT/'layout-verified.json').write_text(json.dumps(layouts,indent=2))
    log2=open(OUT/'nested-quickshell-final.log','w')
    shell=subprocess.Popen(prefix+['timeout','20','quickshell','-p','/run/apx/multimonitor-check'],stdout=log2,stderr=log2,start_new_session=True)
    time.sleep(1)
    ipc=['quickshell','-p','/run/apx/multimonitor-check','ipc','call','host']
    reports=[]
    for screen in ['HEADLESS-1','HEADLESS-2']:
        assert ctl('eval','hl.dispatch(hl.dsp.focus({monitor="'+screen+'"}))').strip()=='ok'
        time.sleep(.1)
        run(ipc+['toggleControls']);time.sleep(.3)
        report=json.loads(run(ipc+['popupStatus']));reports.append(report)
        assert report['screen']==screen and report['bars']==['HEADLESS-1','HEADLESS-2'] and report['visible']
        if screen=='HEADLESS-2':
            run(['grim','-o',screen,'/run/apx/session-1000/apx-display-test.png'])
            (OUT/'controls-second-monitor.png').write_bytes((runtime/'apx-display-test.png').read_bytes())
            (runtime/'apx-display-test.png').unlink()
        run(ipc+['toggleControls'])
    (OUT/'popup-verified.json').write_text(json.dumps(reports,indent=2))
    run(ipc+['toggleControls']);time.sleep(.3)
    ctl('eval','hl.dispatch(hl.dsp.send_shortcut({mods="",key="Tab"}))')
    time.sleep(.2)
    keyboard=json.loads(run(ipc+['popupStatus']))
    assert keyboard['keyboard_index'] >= 0,keyboard
    ctl('eval','hl.dispatch(hl.dsp.send_shortcut({mods="",key="Escape"}))')
    time.sleep(.2)
    assert not json.loads(run(ipc+['popupStatus']))['visible']
    clicks=[]
    for screen,x in [('HEADLESS-1',1800),('HEADLESS-2',500)]:
        ctl('eval','hl.dispatch(hl.dsp.focus({monitor="'+screen+'"}))')
        layers=json.loads(ctl('-j','layers'))[screen]['levels']
        bar=next(layer for layer in layers['2'] if layer['h']==46)
        run(['/run/apx/multimonitor-check/click-nested',str(bar['x']+bar['w']-24),str(bar['y']+23),'2560','720'])
        time.sleep(.3)
        assert json.loads(run(ipc+['popupStatus']))['visible']
        run(['/run/apx/multimonitor-check/click-nested',str(x),'300','2560','720'])
        time.sleep(.3)
        report=json.loads(run(ipc+['popupStatus']));clicks.append(report)
        assert not report['visible'],report
    (OUT/'cross-monitor-clicks.json').write_text(json.dumps(clicks,indent=2))
    # Exercise the real helper against a disposable application on nested outputs.
    ctl('eval','hl.dispatch(hl.dsp.focus({monitor="HEADLESS-1"}))')
    app=subprocess.Popen(prefix+['kitty','--class','apx-monitor-move-check','sh','-c','sleep 20'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            clients=json.loads(ctl('-j','clients'))
            target=next((c for c in clients if c.get('class')=='apx-monitor-move-check'),None)
            if target:break
            time.sleep(.05)
        assert target
        run(['/home/apx/.local/bin/apx-laptop-action-v1','window-right'])
        time.sleep(.2)
        moved=next(c for c in json.loads(ctl('-j','clients')) if c['address']==target['address'])
        second=next(m for m in json.loads(ctl('-j','monitors')) if m['name']=='HEADLESS-2')
        assert moved['monitor']==second['id'],moved
        active=json.loads(ctl('-j','activewindow'))
        cursor=json.loads(ctl('-j','cursorpos'))
        assert active['address']==target['address'],active
        assert moved['at'][0] <= cursor['x'] <= moved['at'][0]+moved['size'][0],cursor
        assert moved['at'][1] <= cursor['y'] <= moved['at'][1]+moved['size'][1],cursor

        ctl('eval','hl.dispatch(hl.dsp.focus({window="address:'+target['address']+'"}))')
        run(['/home/apx/.local/bin/apx-laptop-action-v1','window-left'])
        time.sleep(.2)
        returned=next(c for c in json.loads(ctl('-j','clients')) if c['address']==target['address'])
        first=next(m for m in json.loads(ctl('-j','monitors')) if m['name']=='HEADLESS-1')
        assert returned['monitor']==first['id'],returned
        assert json.loads(ctl('-j','activewindow'))['address']==target['address']
        cursor=json.loads(ctl('-j','cursorpos'))
        assert returned['at'][0] <= cursor['x'] <= returned['at'][0]+returned['size'][0]

        (OUT/'window-move-verified.json').write_text(json.dumps({'right':moved['monitor'],'left':returned['monitor']}))
    finally:
        app.terminate()
    ctl('eval','hl.dispatch(hl.dsp.focus({monitor="HEADLESS-2"}))')
    run(ipc+['showNativePreviewForTest']);time.sleep(.5)
    native_form=json.loads(run(ipc+['popupStatus']))
    assert native_form['visible'] and native_form['environment_form_name']=='windows-2',native_form
    run(['grim','-o','HEADLESS-2','/run/apx/session-1000/apx-native-preview-test.png'])
    (OUT/'hub-native-preview.png').write_bytes((runtime/'apx-native-preview-test.png').read_bytes())
    (runtime/'apx-native-preview-test.png').unlink()
    run(ipc+['closePreviewForTest'])
    (OUT/'layers-verified.json').write_text(ctl('-j','layers'))
    run(ipc+['toggleControls'])
    assert ctl('output','remove','HEADLESS-2').strip()=='ok'
    time.sleep(.4)
    detached=json.loads(run(ipc+['popupStatus']))
    assert detached['bars']==['HEADLESS-1'] and not detached['visible'], detached
    (OUT/'monitor-removal-verified.json').write_text(json.dumps(detached,indent=2))
    print('Verified left/right geometry, two bars and menu placement on both outputs.')
finally:
    try:
        subprocess.run(prefix+['hyprctl','dispatch','hl.dsp.exit()'],capture_output=True,timeout=2)
    except Exception:pass
    for p in [shell,process]:
        if p:
            try:os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError:pass
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL)
