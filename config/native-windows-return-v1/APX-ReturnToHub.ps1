param([switch]$ArmAndRestart)
$ErrorActionPreference = "Stop"

if ($ArmAndRestart) {
    function Write-ApxReturnLog([string]$Message) {
        $directory = Join-Path $env:LOCALAPPDATA "APX"
        New-Item -Path $directory -ItemType Directory -Force | Out-Null
        Add-Content -Path (Join-Path $directory "ReturnToHub.log") -Value ((Get-Date).ToString("o") + " " + $Message)
    }
    try {
        $bcdedit = Join-Path $env:WINDIR "System32\bcdedit.exe"
        $firmware = (& $bcdedit /enum firmware /v 2>&1 | Out-String)
        if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel ler as entradas UEFI." }
        $linuxCandidates = @()
        foreach ($section in ($firmware -split '(?:\r?\n){2,}')) {
            if ($section -match '(?i)\\EFI\\systemd\\systemd-bootx64\.efi') {
                $ids = [regex]::Matches($section, '\{[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\}')
                if ($ids.Count -ne 1) { throw "A entrada Linux UEFI e ambigua." }
                $linuxCandidates += $ids[0].Value
            }
        }
        if ($linuxCandidates.Count -ne 1) { throw "Nao foi encontrada uma entrada Linux UEFI unica." }
        $linux = $linuxCandidates[0]
        & $bcdedit /set '{fwbootmgr}' displayorder $linux /addfirst | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel colocar Linux primeiro na ordem UEFI." }
        & $bcdedit /set '{fwbootmgr}' bootsequence $linux | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel selecionar Linux para o proximo arranque." }
        $manager = (& $bcdedit /enum '{fwbootmgr}' 2>&1 | Out-String)
        if ($LASTEXITCODE -ne 0 -or $manager -notmatch [regex]::Escape($linux)) {
            throw "A selecao UEFI do Linux nao foi confirmada."
        }
        Write-ApxReturnLog "Linux UEFI selected: $linux"
        & (Join-Path $env:WINDIR "System32\shutdown.exe") /r /t 0 /d p:0:0 /c "Regressar ao APX HUB"
        if ($LASTEXITCODE -ne 0) { throw "O Windows recusou o reinicio." }
    } catch {
        Write-ApxReturnLog ("return failed: " + $_.Exception.Message)
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, "APX - Regresso ao HUB") | Out-Null
        exit 1
    }
    exit 0
}

# Older APX releases disabled Explorer's WIN+E action and then tried to claim
# the same OS-reserved chord through the global-hotkey API. Restore the fallback:
# the low-level hook below suppresses WIN+E only while APX is actually running.
$advanced = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
$disabled = (Get-ItemProperty -Path $advanced -Name DisabledHotkeys -ErrorAction SilentlyContinue).DisabledHotkeys
if ($null -ne $disabled -and $disabled.Contains("E")) {
    $restored = $disabled.Replace("E", "")
    if ([String]::IsNullOrEmpty($restored)) {
        Remove-ItemProperty -Path $advanced -Name DisabledHotkeys -ErrorAction SilentlyContinue
    } else {
        Set-ItemProperty -Path $advanced -Name DisabledHotkeys -Type String -Value $restored
    }
}

Add-Type -TypeDefinition @"
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;

public static class APXReturnToHubKeyboardHook {
    private const int WhKeyboardLl = 13;
    private const int WmKeyDown = 0x0100;
    private const int WmSysKeyDown = 0x0104;
    private const int WmKeyUp = 0x0101;
    private const int WmSysKeyUp = 0x0105;
    private const uint WmTimer = 0x0113;
    private static bool leftWin, rightWin;
    private const int VirtualKeyE = 0x45;
    private const int VirtualKeyLeftWin = 0x5B;
    private const int VirtualKeyRightWin = 0x5C;

    private delegate IntPtr LowLevelKeyboardProc(int code, IntPtr message, IntPtr data);
    private static readonly LowLevelKeyboardProc Callback = HookCallback;
    private static IntPtr hook = IntPtr.Zero;
    private static volatile bool rebootStarted;
    private static DateTime lastRequest = DateTime.MinValue;

    [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    private static extern IntPtr SetWindowsHookEx(
        int hookId, LowLevelKeyboardProc callback, IntPtr module, uint threadId);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool UnhookWindowsHookEx(IntPtr hookHandle);

    [DllImport("user32.dll")]
    private static extern IntPtr CallNextHookEx(
        IntPtr hookHandle, int code, IntPtr message, IntPtr data);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern UIntPtr SetTimer(IntPtr window, UIntPtr id, uint milliseconds, IntPtr callback);
    [DllImport("user32.dll")]
    private static extern bool KillTimer(IntPtr window, UIntPtr id);

    [DllImport("user32.dll")]
    private static extern int GetMessage(
        out Message message, IntPtr window, uint minimum, uint maximum);

    [DllImport("user32.dll")]
    private static extern void PostQuitMessage(int exitCode);

    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    private static extern IntPtr GetModuleHandle(string moduleName);

    [StructLayout(LayoutKind.Sequential)]
    private struct Point { public int X; public int Y; }

    [StructLayout(LayoutKind.Sequential)]
    private struct Message {
        public IntPtr Window;
        public uint Id;
        public UIntPtr WParam;
        public IntPtr LParam;
        public uint Time;
        public Point Cursor;
        public uint Private;
    }

    private static void Log(string text) {
        try {
            string directory = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "APX");
            Directory.CreateDirectory(directory);
            File.AppendAllText(Path.Combine(directory, "ReturnToHub.log"),
                DateTimeOffset.Now.ToString("o") + " " + text + Environment.NewLine);
        } catch { }
    }

    private static bool RebootToApx() {
        try {
            string powershell = Environment.ExpandEnvironmentVariables(
                @"%WINDIR%\System32\WindowsPowerShell\v1.0\powershell.exe");
            string script = Path.Combine(Environment.GetFolderPath(
                Environment.SpecialFolder.CommonApplicationData),
                @"APX\ReturnToHub\APX-ReturnToHub.ps1");
            Process.Start(new ProcessStartInfo {
                FileName = powershell,
                Arguments = "-NoLogo -NoProfile -ExecutionPolicy Bypass -File \"" + script + "\" -ArmAndRestart",
                UseShellExecute = true,
                Verb = "runas"
            });
            Log("WIN+E accepted; UEFI selection requested");
            return true;
        } catch (Exception error) {
            Log("reboot failed: " + error.GetType().Name + ": " + error.Message);
            return false;
        }
    }

    private static IntPtr HookCallback(int code, IntPtr message, IntPtr data) {
        long kind = message.ToInt64();
        if (code < 0) return CallNextHookEx(hook, code, message, data);
        int key = Marshal.ReadInt32(data);
        bool down = kind == WmKeyDown || kind == WmSysKeyDown;
        bool up = kind == WmKeyUp || kind == WmSysKeyUp;
        if (down || up) {
            if (key == VirtualKeyLeftWin) leftWin = down;
            if (key == VirtualKeyRightWin) rightWin = down;
        }
        if (down && key == VirtualKeyE) {
            bool windowsPressed = leftWin || rightWin;
            if (windowsPressed && !rebootStarted &&
                    DateTime.UtcNow.Subtract(lastRequest).TotalSeconds >= 5) {
                rebootStarted = true;
                lastRequest = DateTime.UtcNow;
                System.Threading.ThreadPool.QueueUserWorkItem(delegate(object state) {
                    try { RebootToApx(); }
                    finally { rebootStarted = false; }
                });
                return new IntPtr(1);
            }
        }
        return CallNextHookEx(hook, code, message, data);
    }

    private static bool InstallHook() {
        if (hook != IntPtr.Zero) UnhookWindowsHookEx(hook);
        leftWin = rightWin = false;
        using (Process process = Process.GetCurrentProcess())
        using (ProcessModule module = process.MainModule) {
            hook = SetWindowsHookEx(WhKeyboardLl, Callback,
                GetModuleHandle(module.ModuleName), 0);
        }
        if (hook == IntPtr.Zero) {
            Log("keyboard hook failed; win32=" + Marshal.GetLastWin32Error());
            return false;
        }
        return true;
    }

    public static int Run() {
        bool created;
        using (var singleton = new System.Threading.Mutex(true, "Local\\APXReturnToHub", out created)) {
            if (!created) return 0;
            if (!InstallHook()) return 2;
            Log("keyboard hook ready v3; tracked Win keys; periodic recovery");
            UIntPtr timer = SetTimer(IntPtr.Zero, UIntPtr.Zero, 20000, IntPtr.Zero);
            if (timer == UIntPtr.Zero) { UnhookWindowsHookEx(hook); return 2; }
            try {
                Message message;
                int result;
                while ((result = GetMessage(out message, IntPtr.Zero, 0, 0)) > 0) {
                    // Windows can silently remove a timed-out low-level hook.
                    if (message.Id == WmTimer && message.WParam == timer && !InstallHook()) return 2;
                }
                return result == 0 ? 0 : 2;
            } finally {
                KillTimer(IntPtr.Zero, timer);
                UnhookWindowsHookEx(hook);
                hook = IntPtr.Zero;
                singleton.ReleaseMutex();
            }
        }
    }
}
"@

[void][APXReturnToHubKeyboardHook]::Run()
