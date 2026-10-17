@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|add_7
rem HUNTRESS-MATERIAL:6cTO8omP6sDOrRze6Z3bEtGcmtne292g6cTO8omP6sDOrRTduBHa3RHaqR0awZWduBHa3RHaqNIb1ZXdExmboxnb1h2cmt3fsV3g5hGb1B3cE92dolnbDiDR7VHf2pmZs5Ga7p3g5ZXbElHb7dHarh2g1ZHc7hWe85GctVndqZWd5x3esl3M1ZHc7hWe85GctVndqZGbrZnastGR6dHb7p3g4QUf
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set fragment0=v=1^|steps=decode_configuration,return_conf
set fragment1=iguration^|adapter=for^|stage_count=1^|graph=
set fragment2=linear^|next_language=none^|campaign_id=camp
set fragment3=aign-d1437c5203^|host_id=host-d1437c5203
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-d1437c5203
exit /b 0
