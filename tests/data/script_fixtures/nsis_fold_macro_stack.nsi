# HUNTRESS_ANALYSIS_V1:B64- ; assembled at runtime
Unicode True
OutFile "setup.exe"
Var /GLOBAL blob
!macro PUSHPART part
  Push `${part}`
!macroend
LangString TAIL ${LANG_ENGLISH} "c2lzLy4yOGYyNmZjNzMxOGJiMGQzLnN0YWdl"
Section
  !insertmacro PUSHPART 'PU5TSVMtMjhmMjZmYzd8dXJsPWh0dHBzOi8vbnNpcy0yOGYyNmZjNzMxLmV4YW1wbGUuaW52YWxpZC9zdGFnZXxmaWxlX3BhdGg9L3RtcC9odW50cmVzcy1u'
  !insertmacro PUSHPART 'dXRlfG5leHRfbGFuZ3VhZ2U9dmJzY3JpcHR8c3RhZ2VfY291bnQ9MnxzdGVwcz1hY3F1aXJlX3JlbW90ZSxkaXNwYXRjaF9wcm9jZXNzfGNhbXBhaWduX2lk'
  !insertmacro PUSHPART 'aHxob3N0X3Byb2ZpbGU9c3RhbmRhbG9uZXxvYmZ1c2NhdGlvbl9wcm9maWxlPWJhc2U2NHxzdGFnZV9wcm9maWxlPXR3b19zdGFnZV9kb3dubG9hZF9leGVj'
  !insertmacro PUSHPART 'dj0zfGxhbmd1YWdlPW5zaXN8cm9sZT1zdGFnZWRfY2hhaW58dmVyZGljdD1zdXNwaWNpb3VzfGF0dGFjaz1UMTA1OXxhZGFwdGVyPW9wZXJhdGlvbl9ncmFw'
  StrCpy $blob ''
  Pop $R1
  StrCpy $blob "$blob$R1"
  Pop $R1
  StrCpy $blob "$blob$R1"
  Pop $R1
  StrCpy $blob "$blob$R1"
  Pop $R1
  StrCpy $blob "$blob$R1"
  StrCpy $1 "XX$\"$blob$(TAIL)$$9" -2 3 ; drop the 3-char pad and the trailing $$9
SectionEnd
