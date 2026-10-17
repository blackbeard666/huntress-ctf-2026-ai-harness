@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|add_7
rem HUNTRESS-MATERIAL:7d4438837a7b6c777a446b6c6a766b6c666a76756d706e7c79687b70767533796c7b7c7975666a76756d706e7c79687b70767583686b68777b6c79447a6c7b837a7b686e6c666a767c757b4438836e7968776f446b70687476756b83756c7f7b667368756e7c686e6c447576756c836a68747768706e7566706b446a68747768706e7534406b3c3b6b3b3f6a3b3f836f767a7b66706b446f767a7b34406b3c3b6b3b3f6a3b3f
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set v_a0=v=1^|steps=decode_configuration,return_conf
set v_a1=iguration^|adapter=set^|stage_count=1^|graph=
set v_a2=diamond^|next_language=none^|campaign_id=cam
set v_a3=paign-9d54d48c48^|host_id=host-9d54d48c48
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=d2678690"
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-9d54d48c48
exit /b 0
