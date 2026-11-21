param([switch]$Install, [switch]$ArmOnly, [switch]$Remove)
$ErrorActionPreference = 'Stop'
$taskName = 'APX-LinuxDefault-v1'
$directory = Join-Path $env:ProgramData 'APX\ReturnToHub'
$scriptPath = Join-Path $directory 'APX-ReturnToHub.ps1'
$marker = Join-Path $directory 'installed.json'
$logPath = Join-Path $directory 'ReturnToHub.log'

function Write-ApxLog([string]$Message) {
    Add-Content -LiteralPath $logPath -Value ((Get-Date).ToString('o') + ' ' + $Message)
}
function Invoke-ApxBcd([string[]]$Arguments) {
    $output = (& "$env:SystemRoot\System32\bcdedit.exe" @Arguments 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0) { throw ('BCDEdit failed: ' + $output.Trim()) }
    return $output
}
function Set-ApxLinuxDefault {
    $firmware = Invoke-ApxBcd @('/enum', 'firmware', '/v')
    $candidates = @()
    foreach ($section in ($firmware -split '(?:\r?\n){2,}')) {
        if ($section -match '(?im)^\S+\s+\\EFI\\systemd\\systemd-bootx64\.efi\s*$') {
            $ids = [regex]::Matches($section, '(?im)^\S+\s+(\{[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\})\s*$')
            if ($ids.Count -ne 1) { throw 'Ambiguous Linux firmware entry.' }
            $candidates += $ids[0].Groups[1].Value
        }
    }
    if ($candidates.Count -ne 1) { throw 'Expected one Linux Boot Manager.' }
    $linux = $candidates[0]
    $null = Invoke-ApxBcd @('/set', '{fwbootmgr}', 'displayorder', $linux, '/addfirst')
    # Also arm the next restart. This does not restart Windows itself.
    $null = Invoke-ApxBcd @('/set', '{fwbootmgr}', 'bootsequence', $linux)
    $manager = Invoke-ApxBcd @('/enum', '{fwbootmgr}', '/v')
    foreach ($field in @('displayorder', 'bootsequence')) {
        if ($manager -notmatch ('(?im)^' + $field + '\s+' + [regex]::Escape($linux) + '\s*$')) {
            throw ('Linux selection was not confirmed in ' + $field)
        }
    }
    Write-ApxLog ('Linux selected for next restart: ' + $linux)
}

# The Startup launcher only bootstraps the SYSTEM task once. No hotkeys,
# resident keyboard hook, automatic restart, or repeated UAC prompts.
if (-not ($Install -or $ArmOnly -or $Remove)) {
    try {
        $installed = Get-Content -LiteralPath $marker -Raw | ConvertFrom-Json
        if ($installed.sha256 -eq (Get-FileHash -LiteralPath $scriptPath -Algorithm SHA256).Hash) { exit 0 }
    } catch { }
    try {
        $process = Start-Process -FilePath "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Verb RunAs -Wait -PassThru -ArgumentList ('-NoLogo -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + $scriptPath + '" -Install')
        exit $process.ExitCode
    } catch {
        # Cancellation leaves bootstrap available at the next login.
        exit 1
    }
}

try {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'Administrator or SYSTEM privileges required.'
    }
    if ($PSCommandPath -ne $scriptPath) { throw 'Unexpected APX helper location.' }
    foreach ($path in @((Join-Path $env:ProgramData 'APX'), $directory, $scriptPath)) {
        if ((Get-Item -LiteralPath $path).Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw 'APX helper path must not contain links.'
        }
    }
    if ($Remove) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $marker -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath (Join-Path $env:ProgramData 'Microsoft\Windows\Start Menu\Programs\Startup\APX-ReturnToHub.vbs') -Force -ErrorAction SilentlyContinue
        exit 0
    }
    if ($Install) {
        # Protect every file used by the privileged task before registering it.
        $paths = @((Get-Item -LiteralPath (Join-Path $env:ProgramData 'APX')), (Get-Item -LiteralPath $directory)) + @(Get-ChildItem -LiteralPath $directory -Force -Recurse)
        foreach ($item in $paths) {
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked task file refused.' }
            if ($item.PSIsContainer) {
                $acl = New-Object Security.AccessControl.DirectorySecurity
                $inherit = [Security.AccessControl.InheritanceFlags]'ContainerInherit, ObjectInherit'
            } else {
                $acl = New-Object Security.AccessControl.FileSecurity
                $inherit = [Security.AccessControl.InheritanceFlags]::None
            }
            $acl.SetAccessRuleProtection($true, $false)
            $acl.SetOwner((New-Object Security.Principal.SecurityIdentifier('S-1-5-32-544')))
            foreach ($grant in @(@('S-1-5-18', 'FullControl'), @('S-1-5-32-544', 'FullControl'), @('S-1-5-32-545', 'ReadAndExecute'))) {
                $sid = New-Object Security.Principal.SecurityIdentifier($grant[0])
                $rule = New-Object Security.AccessControl.FileSystemAccessRule($sid, $grant[1], $inherit, [Security.AccessControl.PropagationFlags]::None, [Security.AccessControl.AccessControlType]::Allow)
                $acl.AddAccessRule($rule)
            }
            Set-Acl -LiteralPath $item.FullName -AclObject $acl
        }
        $action = New-ScheduledTaskAction -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument ('-NoLogo -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + $scriptPath + '" -ArmOnly')
        $triggers = @((New-ScheduledTaskTrigger -AtStartup), (New-ScheduledTaskTrigger -AtLogOn))
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 1) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
        $null = Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $triggers -Settings $settings -User 'SYSTEM' -RunLevel Highest -Force
    }
    Set-ApxLinuxDefault
    if ($Install) {
        @{sha256=(Get-FileHash -LiteralPath $scriptPath -Algorithm SHA256).Hash; task=$taskName} | ConvertTo-Json | Set-Content -LiteralPath $marker
    }
    exit 0
} catch {
    try { Write-ApxLog ('FAILED: ' + $_.Exception.Message) } catch { }
    exit 1
}
