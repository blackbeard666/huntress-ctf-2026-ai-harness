@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|reverse_xor
rem HUNTRESS-MATERIAL:AkBDHVIGVVIGAAIHCwceVlRSR0AOVlRSR0BsR0tWXU9HUlcdUgZVUgYAAgcLBx5WVFJHQG9RUn9AQFZBR11Ge29QWl9RRmNvQEFWQGZvCXAOW0dSQ2xWX1pVT0dSVx1VCgoAAQcBCxxXWl9SRV1aHVZfQ15SS1YdUgZVUgYAAgcLBxwcCUBDR0dbDl9BRk9SBlVSBgACBwsHHl1UWlJDXlJQDldabF1UWlJDXlJQT19fVltAQVZEXEMOVlRSRlRdUl9sR0tWXU9HRlxsXVJVDltDUkFUTwcOR11GXFBsVlRSR0BPVktWHQEAQUVAVFZBDkFWR0NSV1JPR0NaQVBAbFVVXFddUlsfQEBWUFxBQ2xbUEdSQ0BaVx9WX1pVbFZHWkFEH1ZHXF5WQWxWQVpGQlBSDkBDVkdATwIORQ==
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "v_a0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=reg"
SeT "v_a1=svr32.exe|stage_count=4|graph=fan_out|next_language=powershell|campaign_id=camp"
SeT "v_a2=aign-484135af5a|url=https://484135af5a.example.invalid/8242399f.dat|file_path=C"
SeT "v_a3=:\Users\Public\HuntressLab\stage-484135af5a.dat|next_stage=stage-484135af5a.ps1"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=0f21e041"
ver >nul
if errorlevel 1 exit /b 1
set "cfg=%v_a0%%v_a1%%v_a2%%v_a3%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo regsvr32.exe acquire, write, dispatch, and hand off stage-484135af5a.ps1
exit /b 0
