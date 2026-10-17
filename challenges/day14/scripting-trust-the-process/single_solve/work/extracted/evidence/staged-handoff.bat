@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|rotate_left

rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesLG4urS5Mq+5Mra3ujKWO7k0ujKvszS2MpYyNLm4MLoxtC+4OTexsrm5ljQwtzI3szMvubG5NLg6PjCyMLg6MrkeuDe7srk5tDK2NhcyvDK+Obows7Kvsbe6tzoemj4zuTC4NB6xuTe5ua+2MLczurCzsr43Mrw6L7YwtzO6sLOynrU5sbk0uDo+MbC2uDC0s7cvtLIesbC2uDC0s7cWm5uxG5gam5ucHD46uTYetDo6ODmdF5ebm7EbmBqbm5wcFzK8MLa4NjKXNLc7MLY0shewmrGyMJscMhcyMLo+MzS2Mq+4MLo0HqGdLiq5srk5rig6sTY0sa4kOrc6OTK5uaYwsS45ujCzspabm7EbmBqbm5wcFzIwuj43Mrw6L7m6MLOynrm6MLOylpubsRuYGpubnBwXNTm

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "h0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=power"
SeT "h1=shell.exe|stage_count=4|graph=cross_language|next_language=jscript|campaign_id=ca"
SeT "h2=mpaign-77b7057788|url=https://77b7057788.example.invalid/a5cda68d.dat|file_path=C"
SeT "h3=:\Users\Public\HuntressLab\stage-77b7057788.dat|next_stage=stage-77b7057788.js"

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_opaque_branch=bcb86655"

set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo powershell.exe acquire, write, dispatch, and hand off stage-77b7057788.js

exit /b 0

