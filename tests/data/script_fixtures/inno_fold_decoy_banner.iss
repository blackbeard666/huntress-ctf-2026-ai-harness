[Setup]
AppName=Huntress Notepad
DefaultDirName={autopf}\NP
[Code]
{ banner }
var
  Banner: String;
procedure InitializeWizard();
begin
  Banner := 'VGhhbmsgeW91IGZvciBpbnN0YWxsaW5nIEh1bnRy' + 'ZXNzIE5vdGVwYWQgMS4yIC0tIHNlZSByZWFkbWUudHh0';
  MsgBox(Banner, mbInformation, MB_OK);
end;
