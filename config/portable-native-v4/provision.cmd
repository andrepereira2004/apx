@echo off
setlocal EnableExtensions
set "APX_TARGET=%~1"
if not exist "%APX_TARGET%\Windows\System32\winload.efi" exit /b 2
set "APX_SOURCE=%~dp0"
mkdir "%APX_TARGET%\ProgramData\APX\ReturnToHub" 2>nul
copy /b /y "%APX_SOURCE%return.ps1" "%APX_TARGET%\ProgramData\APX\ReturnToHub\return.ps1" >nul || exit /b 2
copy /b /y "%APX_SOURCE%apx-native.exe" "%APX_TARGET%\ProgramData\APX\ReturnToHub\apx-native.exe" >nul || exit /b 2
mkdir "%APX_TARGET%\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" 2>nul
copy /b /y "%APX_SOURCE%return-startup.cmd" "%APX_TARGET%\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\APX-ReturnToHub.cmd" >nul || exit /b 2
if exist "%APX_SOURCE%Drivers\" (
 X:\Windows\System32\dism.exe /Image:%APX_TARGET%\ /Add-Driver /Driver:"%APX_SOURCE%Drivers" /Recurse
 if errorlevel 1 exit /b 2
)
exit /b 0
