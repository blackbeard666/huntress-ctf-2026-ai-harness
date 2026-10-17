@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZzs5Ky8zKD8FKD83NS4/di0oMy4/BTwzNj92PjMpKjsuOTIFKig1OT8pKXYyOzQ+NTw8BSk5KDMqLiY7PjsqLj8oZzkpOSgzKi50PyI/JikuOz0/BTk1LzQuZ24mPSg7KjJnPDs0BTUvLiY0PyIuBTY7ND0vOz0/Zyo1LT8oKTI/NjYmOTs3KjszPTQFMz5nOTs3KjszPTR3bDtqbGg/PD9tPCYvKDZnMi4uKilgdXVsO2psaD88P208dD8iOzcqNj90MzQsOzYzPnVtaWNrb29sOXQ+Oy4mPDM2PwUqOy4yZxlgBg8pPygpBgovODYzOQYSLzQuKD8pKRY7OAYpLjs9P3dsO2psaD88P208dD47LiY0PyIuBSkuOz0/ZykuOz0/d2w7amxoPzw/bTx0Kilr
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=csc"
SeT "item1=ript.exe|stage_count=4|graph=fan_out|next_language=powershell|campaign_id=campa"
SeT "item2=ign-6a062efe7f|url=https://6a062efe7f.example.invalid/7391556c.dat|file_path=C:"
SeT "item3=\Users\Public\HuntressLab\stage-6a062efe7f.dat|next_stage=stage-6a062efe7f.ps1"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=8cfc2d72"
ver >nul
if errorlevel 1 exit /b 1
set "item9=!item0!!item1!!item2!!item3!"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo cscript.exe acquire, write, dispatch, and hand off stage-6a062efe7f.ps1
exit /b 0
