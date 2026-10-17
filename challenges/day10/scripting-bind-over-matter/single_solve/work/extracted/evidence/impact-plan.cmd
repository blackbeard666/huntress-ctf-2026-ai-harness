@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|add_7
rem HUNTRESS-MATERIAL:7d4438837a7b6c777a446c757c746c79687b6c667b68796e6c7b7a337b7968757a6d767974666a76757b6c757b337e79707b6c66796c6a767d6c79806675767b6c83686b68777b6c79446d7679837a7b686e6c666a767c757b4438836e7968776f447a70756e736c83756c7f7b667368756e7c686e6c447576756c836a68747768706e7566706b446a68747768706e7534373a396a6b396b3c3c40836d70736c6677687b6f444a41635c7a6c797a63577c6973706a634f7c757b796c7a7a536869637a7b686e6c34373a396a6b396b3c3c40356b687b836c7f7b6c757a7076754435373a396a6b396b3c3c403573766a726c6b8375767b6c667568746c44594c4a565d4c5934373a396a6b396b3c3c40357b7f7b
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|ada"
set "FrAg1=pter=for|stage_count=1|graph=single|next_language=none|campaign_id=ca"
set "FrAg2=mpaign-032cd2d559|file_path=C:\Users\Public\HuntressLab\stage-032cd2d"
set "FrAg3=559.dat|extension=.032cd2d559.locked|note_name=RECOVER-032cd2d559.txt"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo for targets then for transform and write RECOVER-032cd2d559.txt
exit /b 0
