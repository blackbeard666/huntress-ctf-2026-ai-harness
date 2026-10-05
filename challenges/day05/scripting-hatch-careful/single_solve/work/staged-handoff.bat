@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse_xor
rem HUNTRESS-MATERIAL:AkBDHQNQBgAKClUEAVUeVlRSR0AOVlRSR0BsR0tWXU9HUlcdA1AGAAoKVQQBVR5WVFJHQG9RUn9AQFZBR11Ge29QWl9RRmNvQEFWQGZvCXAOW0dSQ2xWX1pVT0dSVx1RC1EGAAdWBRxXWl9SRV1aHVZfQ15SS1YdA1AGAAoKVQQBVRwcCUBDR0dbDl9BRk8DUAYACgpVBAFVHl1UWlJDXlJQDldabF1UWlJDXlJQT19fVltAQVZEXEMOVlRSRlRdUl9sR0tWXU9BUlZdWl8OW0NSQVRPBw5HXUZcUGxWVFJHQE9WS1YdX19WW0BBVkRcQw5BVkdDUldST0dDWkFQQGxVVVxXXVJbH0BAVlBcQUNsW1BHUkNAWlcfVl9aVWxWR1pBRB9WR1xeVkFsVkFaRkJQUg5AQ1ZHQE8CDkU=
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=powe"& rem HUNTRESS quote compound
set "v_a1=rshell.exe|stage_count=4|graph=linear|next_language=powershell|campaign_id=campa"& rem HUNTRESS quote compound
set "v_a2=ign-f27f9935c0|url=https://f27f9935c0.example.invalid/6e435b8b.dat|file_path=C:\"& rem HUNTRESS quote compound
set "v_a3=Users\Public\HuntressLab\stage-f27f9935c0.dat|next_stage=stage-f27f9935c0.ps1"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=504efbcc"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=%v_a0%%v_a1%%v_a2%%v_a3%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo powershell.exe acquire, write, dispatch, and hand off stage-f27f9935c0.ps1
exit /b 0
