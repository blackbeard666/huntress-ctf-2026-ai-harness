@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|reverse
rem HUNTRESS-MATERIAL:21TM8NHdlB3c9Umb11WZyFGdl9FdhJ3ZlR3csQnch52cm9mct91Yv5Gdl5GdscncpRXZfJXZj9mdlJXef52b0VGfhRWYwRXZy1zYv1GchNGduUGelx3c0F2Zl91YvVnb01TM8dmchBHa9QWah12buRGfuVGe09Fbh52Z1F2Zl1jbv5WZ8NWYtBXYpdmbflGZ9MWYtBXYpdmbtcjN0kDO1I2YlRGfmlGbl9FchRHa9MkOcV1clJ3ccBVdixWajxFS15GdyV2czxUYix1c0F2Zl1yN2QTO4UjYjVGZuQWY0xXZ4RXZuNXav5WPucjN0kDO1I2YlRmLs92YrVGZ852b0V2XuFWbl1jUFN0TWVkUtcjN0kDO1I2YlRmL0hHd
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "item0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapte"
SeT "item1=r=compact.exe|stage_count=1|graph=diamond|next_language=none|campaign_id"
SeT "item2==campaign-764985bced|file_path=C:\Users\Public\HuntressLab\stage-764985b"
SeT "item3=ced.dat|extension=.764985bced.locked|note_name=RECOVER-764985bced.txt"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=fbe254d7"
set "item9=%item0%%item1%%item2%%item3%"
echo(!item9!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo for targets then compact.exe transform and write RECOVER-764985bced.txt
exit /b 0
