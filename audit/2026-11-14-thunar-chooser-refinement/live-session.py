import subprocess,json,time
from pathlib import Path
PREFIX=['nsenter','-t','15141','-U','-m','-u','-i','-n','-p','-r','-S','1000','-G','1000','env','HOME=/home/apx','XDG_RUNTIME_DIR=/run/apx/session-1000','WAYLAND_DISPLAY=wayland-1','XDG_SESSION_TYPE=wayland','XDG_CURRENT_DESKTOP=Hyprland','DBUS_SESSION_BUS_ADDRESS=unix:path=/run/apx/session-1000/bus','HYPRLAND_INSTANCE_SIGNATURE=efb50993780079460b0cbed1363e2166a2de1d9f_1794650102_926429744']
def run(*args):return subprocess.check_output(PREFIX+list(args),text=True)
def dispatch(expr):return run('hyprctl','dispatch',expr)
def clients():return json.loads(run('hyprctl','-j','clients'))
def key(mods,key):return dispatch('hl.dsp.send_shortcut({mods='+json.dumps(mods)+',key='+json.dumps(key)+'})')
def capture(name):
 time.sleep(.5);run('grim','/tmp/apx-live-check.png')
 Path(__file__).with_name(name).write_bytes(Path('/proc/15141/root/tmp/apx-live-check.png').read_bytes())
