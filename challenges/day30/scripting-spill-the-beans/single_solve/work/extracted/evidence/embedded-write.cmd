@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse
rem HUNTRESS-MATERIAL:116.97.100.46.50.98.102.101.98.101.98.102.49.99.45.101.103.97.116.115.92.98.97.76.115.115.101.114.116.110.117.72.92.99.105.108.98.117.80.92.115.114.101.115.85.92.58.67.61.104.116.97.112.95.101.108.105.102.124.50.98.102.101.98.101.98.102.49.99.45.110.103.105.97.112.109.97.99.61.100.105.95.110.103.105.97.112.109.97.99.124.101.110.111.110.61.101.103.97.117.103.110.97.108.95.116.120.101.110.124.101.108.103.110.105.115.61.104.112.97.114.103.124.49.61.116.110.117.111.99.95.101.103.97.116.115.124.101.120.101.46.108.105.116.117.116.114.101.99.61.114.101.116.112.97.100.97.124.101.108.105.102.95.101.116.105.114.119.44.100.101.100.100.101.98.109.101.95.101.100.111.99.101.100.61.115.112.101.116.115.124.49.61.118
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set v_a0=v=1^|steps=decode_embedded,write_file^|adapter=cert
set v_a1=util.exe^|stage_count=1^|graph=single^|next_language
set v_a2==none^|campaign_id=campaign-c1fbebefb2^|file_path=C
set v_a3=:\Users\Public\HuntressLab\stage-c1fbebefb2.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=dc9c2b43"
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-c1fbebefb2.dat
exit /b 0
