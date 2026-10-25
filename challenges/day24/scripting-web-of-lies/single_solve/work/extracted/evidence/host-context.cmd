@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|reverse_xor

rem HUNTRESS-MATERIAL:B1UKAAIEAFVWVR5HQFxbDldabEdAXFtPB1UKAAIEAFVWVR5dVFpSQ15SUA5XWmxdVFpSQ15SUE9WXVxdDlZUUkZUXVJfbEdLVl1PSkFHVkFsWFBSUV9fUlUOW0NSQVRPAg5HXUZcUGxWVFJHQE9fX1JQDkFWR0NSV1JPXVxaR1JBRlRaVV1cUGxdQUZHVkEfXVxaR1JBRlRaVV1cUGxWV1xQVlcOQENWR0BPAg5F

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "item0=v=1|steps=decode_configuration,return_config"
set "item1=uration|adapter=call|stage_count=1|graph=fal"
set "item2=lback_retry|next_language=none|campaign_id=c"
set "item3=ampaign-fef37139f4|host_id=host-fef37139f4"

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_opaque_branch=77d269dd"

call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=!item0!!item1!!item2!!item3!"
exit /b 0
:HUNTRESS_EMIT

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo set HUNTRESS_HOST=host-fef37139f4

exit /b 0

