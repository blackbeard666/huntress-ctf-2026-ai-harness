@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|identity
rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLHdyaXRlX2ZpbGUsZGlzcGF0Y2hfcHJvY2VzcyxoYW5kb2ZmX3NjcmlwdHxhZGFwdGVyPWNtZC5leGV8c3RhZ2VfY291bnQ9NHxncmFwaD1zYW1lX2xhbmd1YWdlfG5leHRfbGFuZ3VhZ2U9YmF0Y2h8Y2FtcGFpZ25faWQ9Y2FtcGFpZ24tOTA3YTFhMDk0MHx1cmw9aHR0cHM6Ly85MDdhMWEwOTQwLmV4YW1wbGUuaW52YWxpZC9kMWY0NTYwMy5kYXR8ZmlsZV9wYXRoPUM6XFVzZXJzXFB1YmxpY1xIdW50cmVzc0xhYlxzdGFnZS05MDdhMWEwOTQwLmRhdHxuZXh0X3N0YWdlPXN0YWdlLTkwN2ExYTA5NDAuY21k
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=cm"
set "fragment1=d.exe|stage_count=4|graph=same_language|next_language=batch|campaign_id=campai"
set "fragment2=gn-907a1a0940|url=https://907a1a0940.example.invalid/d1f45603.dat|file_path=C:"
set "fragment3=\Users\Public\HuntressLab\stage-907a1a0940.dat|next_stage=stage-907a1a0940.cmd"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=d95d8e4f"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo cmd.exe acquire, write, dispatch, and hand off stage-907a1a0940.cmd
exit /b 0
