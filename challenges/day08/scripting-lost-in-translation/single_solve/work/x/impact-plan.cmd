@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:decimal_bytes|add_7

rem HUNTRESS-MATERIAL:125.68.56.131.122.123.108.119.122.68.108.117.124.116.108.121.104.123.108.102.123.104.121.110.108.123.122.51.123.121.104.117.122.109.118.121.116.102.106.118.117.123.108.117.123.51.126.121.112.123.108.102.121.108.106.118.125.108.121.128.102.117.118.123.108.131.104.107.104.119.123.108.121.68.106.118.116.119.104.106.123.53.108.127.108.131.122.123.104.110.108.102.106.118.124.117.123.68.56.131.110.121.104.119.111.68.106.121.118.122.122.102.115.104.117.110.124.104.110.108.131.117.108.127.123.102.115.104.117.110.124.104.110.108.68.117.118.117.108.131.106.104.116.119.104.112.110.117.102.112.107.68.106.104.116.119.104.112.110.117.52.107.61.107.61.55.60.62.62.106.109.131.109.112.115.108.102.119.104.123.111.68.74.65.99.92.122.108.121.122.99.87.124.105.115.112.106.99.79.124.117.123.121.108.122.122.83.104.105.99.122.123.104.110.108.52.107.61.107.61.55.60.62.62.106.109.53.107.104.123.131.108.127.123.108.117.122.112.118.117.68.53.107.61.107.61.55.60.62.62.106.109.53.115.118.106.114.108.107.131.117.118.123.108.102.117.104.116.108.68.89.76.74.86.93.76.89.52.107.61.107.61.55.60.62.62.106.109.53.123.127.123

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "h0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapter"& rem HUNTRESS quote compound
set "h1==compact.exe|stage_count=1|graph=cross_language|next_language=none|campai"& rem HUNTRESS quote compound
set "h2=gn_id=campaign-d6d60577cf|file_path=C:\Users\Public\HuntressLab\stage-d6d"& rem HUNTRESS quote compound
set "h3=60577cf.dat|extension=.d6d60577cf.locked|note_name=RECOVER-d6d60577cf.txt"& rem HUNTRESS quote compound

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_string_join=f7c09676"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"
exit /b 0
:HUNTRESS_EMIT

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo for targets then compact.exe transform and write RECOVER-d6d60577cf.txt

exit /b 0

