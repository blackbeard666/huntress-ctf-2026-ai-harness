@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:decimal_bytes|rotate_left

rem HUNTRESS-MATERIAL:236.122.98.248.230.232.202.224.230.122.200.202.198.222.200.202.190.202.218.196.202.200.200.202.200.88.238.228.210.232.202.190.204.210.216.202.248.194.200.194.224.232.202.228.122.202.240.232.228.194.198.102.100.92.202.240.202.248.230.232.194.206.202.190.198.222.234.220.232.122.98.248.206.228.194.224.208.122.198.228.222.230.230.190.216.194.220.206.234.194.206.202.248.220.202.240.232.190.216.194.220.206.234.194.206.202.122.220.222.220.202.248.198.194.218.224.194.210.206.220.190.210.200.122.198.194.218.224.194.210.206.220.90.204.104.112.106.202.112.108.110.202.198.248.204.210.216.202.190.224.194.232.208.122.134.116.184.170.230.202.228.230.184.160.234.196.216.210.198.184.144.234.220.232.228.202.230.230.152.194.196.184.230.232.194.206.202.90.204.104.112.106.202.112.108.110.202.198.92.200.194.232

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set item0=v=1^|steps=decode_embedded,write_file^|adapter=extrac
set item1=32.exe^|stage_count=1^|graph=cross_language^|next_lang
set item2=uage=none^|campaign_id=campaign-f485e867ec^|file_path
set item3==C:\Users\Public\HuntressLab\stage-f485e867ec.dat

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_dead_label=2ddc3a1f"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=!item0!!item1!!item2!!item3!"
exit /b 0
:HUNTRESS_EMIT

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo extrac32.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-f485e867ec.dat

exit /b 0

