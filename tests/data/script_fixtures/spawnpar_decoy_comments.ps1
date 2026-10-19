# notes on detection only -- nothing here launches or persists anything
$Codec_00d1 = 'base64|identity|'
$Material_00d1 = 'dGhlbWU9ZGFya3xmb250PUNvbnNvbGFzfGF1dG9zYXZlPW9ufGludGVydmFsPTMwMHx3aW5kb3c9VGVybWluYWx8dGVsZW1ldHJ5PW9mZg=='
# UpdateProcThreadAttribute PROC_THREAD_ATTRIBUTE_PARENT_PROCESS STARTUPINFOEX CreateProcess
# schtasks /create /tn x /tr calc.exe ; Win32_Process Create ; MMC20.Application ExecuteShellCommand
Write-Host "Watch for WmiPrvSE.exe spawning powershell and services.exe spawning sc-created services"
