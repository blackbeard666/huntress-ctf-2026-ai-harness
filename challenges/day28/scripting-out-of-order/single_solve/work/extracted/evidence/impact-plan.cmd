@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGx1fHRseWh7bGZ7aHlubHt6M3t5aHV6bXZ5dGZqdnV7bHV7M355cHtsZnlsanZ9bHmAZnV2e2yDaGtod3tseURqcHdvbHk1bH9sg3p7aG5sZmp2fHV7RDiDbnlod29Eanl2enpmc2h1bnxobmyDdWx/e2ZzaHVufGhubER1dnVsg2podHdocG51ZnBrRGpodHdocG51NDhraW1sbT9tPT+DbXBzbGZ3aHtvREpBY1x6bHl6Y1d8aXNwamNPfHV7eWx6elNoaWN6e2hubDQ4a2ltbG0/bT0/NWtoe4Nsf3tsdXpwdnVENThraW1sbT9tPT81c3Zqcmxrg3V2e2xmdWh0bERZTEpWXUxZNDhraW1sbT9tPT81e397
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "v_a0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapter"
SeT "v_a1==cipher.exe|stage_count=1|graph=cross_language|next_language=none|campaig"
SeT "v_a2=n_id=campaign-1dbfef8f68|file_path=C:\Users\Public\HuntressLab\stage-1dbf"
SeT "v_a3=ef8f68.dat|extension=.1dbfef8f68.locked|note_name=RECOVER-1dbfef8f68.txt"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=f54bc25c"
ver >nul
if errorlevel 1 exit /b 1
set "cfg=%v_a0%%v_a1%%v_a2%%v_a3%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo for targets then cipher.exe transform and write RECOVER-1dbfef8f68.txt
exit /b 0
