@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|reverse_xor
rem HUNTRESS-MATERIAL:AkBDHQNSUgcCVgUGVlIeVlRSR0AOVlRSR0BsR0tWXU9HUlcdA1JSBwJWBQZWUh5WVFJHQG9RUn9AQFZBR11Ge29QWl9RRmNvQEFWQGZvCXAOW0dSQ2xWX1pVT0dSVx0DBlECUQpQUBxXWl9SRV1aHVZfQ15SS1YdA1JSBwJWBQZWUhwcCUBDR0dbDl9BRk8DUlIHAlYFBlZSHl1UWlJDXlJQDldabF1UWlJDXlJQT19fVltAQVZEXEMOVlRSRlRdUl9sR0tWXU9WX1RdWkAOW0NSQVRPBw5HXUZcUGxWVFJHQE9WS1YdX19WW0BBVkRcQw5BVkdDUldST0dDWkFQQGxVVVxXXVJbH0BAVlBcQUNsW1BHUkNAWlcfVl9aVWxWR1pBRB9WR1xeVkFsVkFaRkJQUg5AQ1ZHQE8CDkU=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=powe"
SeT "item1=rshell.exe|stage_count=4|graph=single|next_language=powershell|campaign_id=campa"
SeT "item2=ign-ae56e14aa0|url=https://ae56e14aa0.example.invalid/cc9b1b50.dat|file_path=C:\"
SeT "item3=Users\Public\HuntressLab\stage-ae56e14aa0.dat|next_stage=stage-ae56e14aa0.ps1"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=79e5512f"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=!item0!!item1!!item2!!item3!"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo powershell.exe acquire, write, dispatch, and hand off stage-ae56e14aa0.ps1
exit /b 0
