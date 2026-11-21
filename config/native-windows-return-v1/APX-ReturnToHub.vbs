Option Explicit
Dim shell, command
Set shell = CreateObject("WScript.Shell")
command = "powershell.exe -NoLogo -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & shell.ExpandEnvironmentStrings("%ProgramData%\APX\ReturnToHub\APX-ReturnToHub.ps1") & """"
' One attempt per login. Cancellation never creates a retry loop.
shell.Run command, 0, False
