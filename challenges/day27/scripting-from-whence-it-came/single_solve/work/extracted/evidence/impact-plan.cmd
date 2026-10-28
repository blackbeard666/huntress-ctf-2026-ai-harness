@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGx1fHRseWh7bGZ7aHlubHt6M3t5aHV6bXZ5dGZqdnV7bHV7M355cHtsZnlsanZ9bHmAZnV2e2yDaGtod3tseURqdnR3aGp7NWx/bIN6e2hubGZqdnx1e0Q4g255aHdvRGtwaHR2dWuDdWx/e2ZzaHVufGhubER1dnVsg2podHdocG51ZnBrRGpodHdocG51NDw4PDk3bD9tajyDbXBzbGZ3aHtvREpBY1x6bHl6Y1d8aXNwamNPfHV7eWx6elNoaWN6e2hubDQ8ODw5N2w/bWo8NWtoe4Nsf3tsdXpwdnVENTw4PDk3bD9tajw1c3Zqcmxrg3V2e2xmdWh0bERZTEpWXUxZNDw4PDk3bD9tajw1e397
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set v_a0=v=1^|steps=enumerate_targets,transform_content,write_recovery_note^|adapte
set v_a1=r=compact.exe^|stage_count=1^|graph=diamond^|next_language=none^|campaign_id
set v_a2==campaign-51520e8fc5^|file_path=C:\Users\Public\HuntressLab\stage-51520e8
set v_a3=fc5.dat^|extension=.51520e8fc5.locked^|note_name=RECOVER-51520e8fc5.txt
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=91397d60"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=!v_a0!!v_a1!!v_a2!!v_a3!"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo for targets then compact.exe transform and write RECOVER-51520e8fc5.txt
exit /b 0
