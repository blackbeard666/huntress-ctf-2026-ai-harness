@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|add_7
rem HUNTRESS-MATERIAL:7d4438837a7b6c777a446c757c746c79687b6c667b68796e6c7b7a337b7968757a6d767974666a76757b6c757b337e79707b6c66796c6a767d6c79806675767b6c83686b68777b6c79446a70776f6c79356c7f6c837a7b686e6c666a767c757b4438836e7968776f447370756c687983756c7f7b667368756e7c686e6c447576756c836a68747768706e7566706b446a68747768706e75343f37693c39373a69686b836d70736c6677687b6f444a41635c7a6c797a63577c6973706a634f7c757b796c7a7a536869637a7b686e6c343f37693c39373a69686b356b687b836c7f7b6c757a70767544353f37693c39373a69686b3573766a726c6b8375767b6c667568746c44594c4a565d4c59343f37693c39373a69686b357b7f7b
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set item0=v=1^|steps=enumerate_targets,transform_content,write_recovery_note^|adapt
set item1=er=cipher.exe^|stage_count=1^|graph=linear^|next_language=none^|campaign_id
set item2==campaign-80b5203bad^|file_path=C:\Users\Public\HuntressLab\stage-80b520
set item3=3bad.dat^|extension=.80b5203bad.locked^|note_name=RECOVER-80b5203bad.txt
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=57c9246b"
set "item9=!item0!!item1!!item2!!item3!"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo for targets then cipher.exe transform and write RECOVER-80b5203bad.txt
exit /b 0
