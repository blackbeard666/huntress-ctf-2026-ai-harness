@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:hex_pairs|add_7

rem HUNTRESS-MATERIAL:7d4438837a7b6c777a44686a787c70796c66796c74767b6c337e79707b6c666d70736c336b707a77687b6a6f667779766a6c7a7a336f68756b766d6d667a6a7970777b83686b68777b6c7944797c756b73733a39356c7f6c837a7b686e6c666a767c757b443b836e7968776f447370756c687983756c7f7b667368756e7c686e6c4477767e6c797a6f6c7373836a68747768706e7566706b446a68747768706e75343c6a6b3b4069393c3b3d837c7973446f7b7b777a4136363c6a6b3b4069393c3b3d356c7f687477736c3570757d6873706b363e3d3a6d3c393a6d356b687b836d70736c6677687b6f444a41635c7a6c797a63577c6973706a634f7c757b796c7a7a536869637a7b686e6c343c6a6b3b4069393c3b3d356b687b83756c7f7b667a7b686e6c447a7b686e6c343c6a6b3b4069393c3b3d35777a38

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set fragment0=v=1^|steps=acquire_remote,write_file,dispatch_process,handoff_script^|adapter=run
set fragment1=dll32.exe^|stage_count=4^|graph=linear^|next_language=powershell^|campaign_id=campa
set fragment2=ign-5cd49b2546^|url=https://5cd49b2546.example.invalid/763f523f.dat^|file_path=C:
set fragment3=\Users\Public\HuntressLab\stage-5cd49b2546.dat^|next_stage=stage-5cd49b2546.ps1

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_string_join=5fccecc3"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
exit /b 0
:HUNTRESS_EMIT

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo rundll32.exe acquire, write, dispatch, and hand off stage-5cd49b2546.ps1

exit /b 0

