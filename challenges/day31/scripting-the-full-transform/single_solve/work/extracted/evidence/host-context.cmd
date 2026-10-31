@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:ZjE2M2JlZTk5NS10c29oPWRpX3Rzb2h8ZjE2M2JlZTk5NS1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xlbm9uPWVnYXVnbmFsX3R4ZW58ZWdhdWduYWxfZW1hcz1ocGFyZ3wxPXRudW9jX2VnYXRzfHRlcz1yZXRwYWRhfG5vaXRhcnVnaWZub2NfbnJ1dGVyLG5vaXRhcnVnaWZub2NfZWRvY2VkPXNwZXRzfDE9dg==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=decode_configuration,return_confi"& rem HUNTRESS quote compound
set "h1=guration|adapter=set|stage_count=1|graph=sa"& rem HUNTRESS quote compound
set "h2=me_language|next_language=none|campaign_id="& rem HUNTRESS quote compound
set "h3=campaign-599eeb361f|host_id=host-599eeb361f"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=e9d42e0b"
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-599eeb361f
exit /b 0
