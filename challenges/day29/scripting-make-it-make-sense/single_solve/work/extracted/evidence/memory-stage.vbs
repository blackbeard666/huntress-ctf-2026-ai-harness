Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_455c6700 = "118,61,49,124,115,116,101,112,115,61,97,99,113,117,105,114,101,95,114,101,109,111,116,101,44,100,105,115,112,97,116,99,104,95,109,101,109,111,114,121,124,97,100,97,112,116,101,114,61,87,105,110,72,116,116,112,46,87,105,110,72,116,116,112,82,101,113,117,101,115,116,46,53,46,49,124,115,116,97,103,101,95,99,111,117,110,116,61,50,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,54,101,56,50,101,97,54,100,48,102,124,117,114,108,61,104,116,116,112,115,58,47,47,54,101,56,50,101,97,54,100,48,102,46,101,120,97,109,112,108,101,46,105,110,118,97,108,105,100,47,53,57,102,57,99,49,49,54,46,100,97,116,124,117,115,101,114,95,97,103,101,110,116,61,72,117,110,116,114,101,115,115,76,97,98,47,54,101,56,50,101,97,54,100,48,102"
Const Codec_455c6700 = "reversed_decimal|reverse_bytes|"

Function Load_455c6700()
  Dim parts, result(), i
  parts = Split(Material_455c6700, ",")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt(parts(i))
  Next
  Load_455c6700 = result
End Function

Function Decode_455c6700(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(UBound(s) - i) = s(i)
  Next
  Decode_455c6700 = result
End Function

Function Recover_455c6700()
  Dim s, d, t, n, i, p, e, q
  n = LCase(UCase("Host"))
  s = Load_455c6700()
  d = Decode_455c6700(s)
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
  Recover_455c6700 = t
End Function

Sub Copy_455c6700(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_455c6700()
  Dim resultText
  Call Copy_455c6700(Recover_455c6700(), resultText)
  Inspect_455c6700 = resultText
End Function
