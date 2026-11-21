# Visible per-user Return to Hub. Only the small signed-source helper elevates.
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$created = $false
$mutex = New-Object Threading.Mutex($true, 'Local\APXReturnToHub', [ref]$created)
if (-not $created) { $mutex.Dispose(); exit }
$icon = New-Object Windows.Forms.NotifyIcon
$icon.Icon = [Drawing.SystemIcons]::Application
$icon.Text = 'APX — Voltar ao Hub'
$menu = New-Object Windows.Forms.ContextMenuStrip
$item = $menu.Items.Add('Voltar ao Hub')
$item.add_Click({
    try {
        $job = Start-Process -FilePath "$env:ProgramData\APX\ReturnToHub\apx-native.exe" -ArgumentList '--return' -Verb RunAs -Wait -PassThru
        if ($job.ExitCode -ne 0) { throw 'Não foi possível confirmar o arranque do APX.' }
    } catch { [Windows.Forms.MessageBox]::Show($_.Exception.Message, 'APX') }
})
$icon.ContextMenuStrip = $menu
$icon.Visible = $true
try { [Windows.Forms.Application]::Run() } finally { $icon.Dispose(); $mutex.Dispose() }
