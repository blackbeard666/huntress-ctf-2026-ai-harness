@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:dGFkLjhiYmJlMmNjM2YtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnw4YmJiZTJjYzNmLW5naWFwbWFjPWRpX25naWFwbWFjfGVub249ZWdhdWduYWxfdHhlbnxlZ2F1Z25hbF9zc29yYz1ocGFyZ3wxPXRudW9jX2VnYXRzfGV4ZS5saXR1dHJlYz1yZXRwYWRhfGVsaWZfZXRpcncsZGVkZGVibWVfZWRvY2VkPXNwZXRzfDE9dg==
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set v_a0=v=1^|steps=decode_embedded,write_file^|adapter=certut
set v_a1=il.exe^|stage_count=1^|graph=cross_language^|next_lang
set v_a2=uage=none^|campaign_id=campaign-f3cc2ebbb8^|file_path
set v_a3==C:\Users\Public\HuntressLab\stage-f3cc2ebbb8.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=33d9142c"
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%v_a%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo certutil.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-f3cc2ebbb8.dat
exit /b 0
