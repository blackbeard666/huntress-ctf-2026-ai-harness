; installer banner
!define A "VGhhbmsgeW91IGZvciBpbnN0YWxsaW5nIEh1bnRy"
!define B "ZXNzIE5vdGVwYWQgMS4yIC0tIHNlZSByZWFkbWUudHh0"
OutFile "np.exe"
Section
  StrCpy $0 "${A}"
  StrCpy $0 "$0${B}"
  MessageBox MB_OK $0
SectionEnd
