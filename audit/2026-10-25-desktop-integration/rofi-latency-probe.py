import subprocess,time,json,statistics,os

def layers():
    data=json.loads(subprocess.check_output(['hyprctl','-j','layers'],text=True))
    return any(layer.get('namespace')=='rofi' for monitor in data.values() for group in monitor.get('levels',{}).values() for layer in group)
assert not layers(), 'Existing Rofi must not be interrupted'
rows=[]
for i in range(4):
    t=time.monotonic()
    env=dict(os.environ,LD_PRELOAD='/home/apx/.local/libexec/apx-rofi-secondary-v1.so',ROFI_PLUGIN_PATH='/home/apx/.local/lib/rofi')
    p=subprocess.Popen(['/usr/bin/rofi','-modi','apps,files,system','-show','apps','-me-select-entry','','-me-accept-entry','MousePrimary','-me-accept-custom','MouseSecondary','-kb-cancel','Escape,Control+g,Control+bracketleft'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        while not layers():
            if p.poll() is not None:raise RuntimeError('Rofi exited before map')
            if time.monotonic()-t>6:raise RuntimeError('Rofi map timeout')
            time.sleep(.01)
        rows.append(round((time.monotonic()-t)*1000,1))
        time.sleep(.4)
    finally:
        p.terminate();p.wait(timeout=4)
    time.sleep(.3)
print(json.dumps({'mapped_ms':rows,'median_ms':statistics.median(rows),'scope':'real Apps mode process to layer registration; includes polling overhead; not first rendered frame or animation complete','remaining':layers()},indent=2))
