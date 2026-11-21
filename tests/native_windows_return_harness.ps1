param([string]$Source)
$ErrorActionPreference = 'Stop'
$tokens = $null; $errors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile($Source, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw ($errors | Out-String) }
$function = $ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Set-ApxLinuxDefault'}, $true)
. ([scriptblock]::Create($function.Extent.Text))
$linux = '{cf5b40db-a4b3-11f1-a094-9dba6ec176b3}'
$script:firmware = @"
Firmware Boot Manager
---------------------
identifier              {fwbootmgr}
displayorder            {bootmgr}
                        $linux

Firmware Application (101fffff)
-------------------------------
identifier              $linux
device                  partition=\Device\HarddiskVolume1
path                    \EFI\systemd\systemd-bootx64.efi
description             Linux Boot Manager

Windows Boot Manager
--------------------
identifier              {bootmgr}
path                    \EFI\Microsoft\Boot\bootmgfw.efi
"@
$script:manager = "identifier {fwbootmgr}`ndisplayorder $linux`n               {bootmgr}`nbootsequence $linux`n"
$script:calls = @(); $script:logs = @()
function Invoke-ApxBcd([string[]]$Arguments) {
    $script:calls += ,$Arguments
    if ($Arguments[0] -eq '/set') { return '' }
    if ($Arguments[1] -eq 'firmware') { return $script:firmware }
    return $script:manager
}
function Write-ApxLog([string]$Message) { $script:logs += $Message }
Set-ApxLinuxDefault
if ($script:calls.Count -ne 4 -or $script:logs.Count -ne 1) { throw 'Expected two reads and two scoped writes.' }
if (($script:calls[1] -join ' ') -ne "/set {fwbootmgr} displayorder $linux /addfirst") { throw 'Wrong default write.' }
if (($script:calls[2] -join ' ') -ne "/set {fwbootmgr} bootsequence $linux") { throw 'Wrong next boot write.' }
$valid = $script:firmware
foreach ($bad in @($valid.Replace('systemd-bootx64.efi','other.efi'), ($valid + "`n`n" + $valid))) {
    $script:firmware = $bad; $script:calls = @(); $failed = $false
    try { Set-ApxLinuxDefault } catch { $failed = $true }
    if (-not $failed -or $script:calls.Count -ne 1) { throw 'Missing/ambiguous Linux must fail before writes.' }
}
$script:firmware = $valid
foreach ($bad in @("displayorder {bootmgr}`nbootsequence $linux", "displayorder $linux`nbootsequence {bootmgr}")) {
    $script:manager = $bad; $failed = $false; $script:logs = @()
    try { Set-ApxLinuxDefault } catch { $failed = $true }
    if (-not $failed -or $script:logs.Count) { throw 'Unverified firmware selection must fail without success log.' }
}
'PASS: PowerShell parser, target selection, scoped writes, ambiguity and failed readback'
