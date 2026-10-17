Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_1027683c = "118,61,49,124,115,116,101,112,115,61,97,99,113,117,105,114,101,95,114,101,109,111,116,101,44,119,114,105,116,101,95,102,105,108,101,124,97,100,97,112,116,101,114,61,77,83,88,77,76,50,46,88,77,76,72,84,84,80,46,54,46,48,124,115,116,97,103,101,95,99,111,117,110,116,61,50,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,54,54,102,52,56,51,48,102,52,48,124,117,114,108,61,104,116,116,112,115,58,47,47,54,54,102,52,56,51,48,102,52,48,46,101,120,97,109,112,108,101,46,105,110,118,97,108,105,100,47,97,102,100,101,53,56,50,50,46,100,97,116,124,117,115,101,114,95,97,103,101,110,116,61,72,117,110,116,114,101,115,115,76,97,98,47,54,54,102,52,56,51,48,102,52,48,124,102,105,108,101,95,112,97,116,104,61,67,58,92,85,115,101,114,115,92,80,117,98,108,105,99,92,72,117,110,116,114,101,115,115,76,97,98,92,115,116,97,103,101,45,54,54,102,52,56,51,48,102,52,48,46,100,97,116"
Const Codec_1027683c = "reversed_decimal|reverse_bytes|"

Function Load_1027683c()
  Dim parts, result(), v_e598
  parts = Split(Material_1027683c, ",")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(UBound(parts) - v_e598) = CInt(parts(v_e598))
  Next
  Load_1027683c = result
End Function

Function Decode_1027683c(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(UBound(v_a19c) - v_e598) = v_a19c(v_e598)
  Next
  Decode_1027683c = result
End Function

Function Recover_1027683c()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If (2 > 1) Then v_d41a = "left" Else v_d41a = "right"
  v_a19c = Load_1027683c()
  Do
    v_b27e = Decode_1027683c(v_a19c)
    Exit Do
  Loop
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_1027683c = v_c304
End Function

Sub Copy_1027683c(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_1027683c()
  Dim resultText
  Call Copy_1027683c(Recover_1027683c(), resultText)
  Inspect_1027683c = resultText
End Function
