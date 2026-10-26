@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|rotate_left
rem HUNTRESS-MATERIAL:=Im5gzFbwhGZwJHyETMcapszCju56pszCju5+iO8KzN+oLMycxGcoRGcyhMxEDnWK7swobOuELMmmbuykjO3qDJuGLN2ErOo4aO5Kbuq4Snh6BN6CDuvKjt0MjP6CjMXK7GckBHbyhsXILN2CzO3SzlyYDu2CDvycxGcoRGcyhMxEDnXeRn5gjO6QrH2krO+sBHakBncITMxwpF3OLtwgrtwGrHyS7L3OLtwgrtwGjP2YrM0mTuyu7N46pszCruzcLM2+iO8KzN+kLsycLN26BN4CTuz4jmeozt6ebsvK7swobO+KDvychN2KDt5krs7eDuekrM6gLMyCjP6gLN5GbuvMzs3IztwQjl5mrsxeTO4+CtxoLM4mLNyYpM2SzsvKju0k7OWKju3arM5+qM5Sru4GLsemDuyobO+ipH7
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=powe"
set "v_a1=rshell.exe|stage_count=4|graph=linear|next_language=powershell|campaign_id=campa"
set "v_a2=ign-8bbd982486|url=https://8bbd982486.example.invalid/d968287e.dat|file_path=C:\"
set "v_a3=Users\Public\HuntressLab\stage-8bbd982486.dat|next_stage=stage-8bbd982486.ps1"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=2a7d8bdc"
ver >nul
if errorlevel 1 exit /b 1
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%v_a%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo powershell.exe acquire, write, dispatch, and hand off stage-8bbd982486.ps1
exit /b 0
