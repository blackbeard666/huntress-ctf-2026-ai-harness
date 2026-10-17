@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|reverse_xor
rem HUNTRESS-MATERIAL:=UkDC8EQHZ1QA5wVWBFXXZFbQxVXVpFVGFkUHpFXd9RQWdkRB1FbQxVXVpFVGFkUHpFXd9kUXJ1QHZVQOUFXB9EQHJFVWxGUcZUXH5gAPRVQSN0WOUlUf9VUSBFWsFkVHFkSP1lVLdEbfJVXUZkUUZlDdxVXW9EUS51QSpFVdxmWX5AUS51QSpFVd5RVQFgADYlVBUFAPtFXAdEbadlDbxFQH5RVQFgADYlVBUFA
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=decode_configuration,return_config"
set "FrAg1=uration|adapter=for|stage_count=1|graph=fall"
set "FrAg2=back_retry|next_language=none|campaign_id=ca"
set "FrAg3=mpaign-fc210ee2f3|host_id=host-fc210ee2f3"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=ee085af7"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "ReCoVeReD=%FrAg0%%FrAg1%%FrAg2%%FrAg3%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-fc210ee2f3
exit /b 0
