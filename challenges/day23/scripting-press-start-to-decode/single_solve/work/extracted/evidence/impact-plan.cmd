@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|add_7
rem HUNTRESS-MATERIAL:==we/tXN90mao1jO7gjOtRTWM1lVKxUWExGdoVnZstnd1N4asJna2NXN90mao1jO7gjOtVDR1ZHc6VHb79HbDuHarVTPtpGa9ozO4oTb0wmbotnejlGaTpnesl3e1x3TjpGczlGfXNme5xmecNWQKR0b7h2dmx2cw12g90mao1jO7gjOtRTduBHa3RHaqR0awZWduBHa3RHaqNIb1ZXdExmboxnb1h2cmt3fsV3g5hGb1B3cE92dolnbDiDR7VHf2pmZs5Ga7p3gs9Hb1kHbvdHcqRUest3dotGaDy2e2VnZAmHb9ZnaslnZstHc553M7VHb7VndqZGd5ZXb6VHa5t3M6tHbulHa7ZGb7hWesRHf1xGR6dHb7p3g4QUf
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "v_a0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapt"
SeT "v_a1=er=cipher.exe|stage_count=1|graph=linear|next_language=none|campaign_id"
SeT "v_a2==campaign-f31436acf6|file_path=C:\Users\Public\HuntressLab\stage-f31436"
SeT "v_a3=acf6.dat|extension=.f31436acf6.locked|note_name=RECOVER-f31436acf6.txt"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo for targets then cipher.exe transform and write RECOVER-f31436acf6.txt
exit /b 0
