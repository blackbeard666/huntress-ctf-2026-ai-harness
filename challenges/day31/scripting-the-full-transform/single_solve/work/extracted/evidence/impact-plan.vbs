Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ee8d88b2 = "116,120,116,46,98,56,54,55,55,98,99,51,45,82,69,86,79,67,69,82,61,101,109,97,110,95,101,116,111,110,124,100,101,107,99,111,108,46,100,101,55,97,52,46,61,110,111,105,115,110,101,116,120,101,124,101,48,50,55,53,54,51,57,57,50,45,110,103,105,97,112,109,97,99,61,100,105,95,110,103,105,97,112,109,97,99,124,50,61,116,110,117,111,99,95,101,103,97,116,115,124,116,99,101,106,98,79,109,101,116,115,121,83,101,108,105,70,46,103,110,105,116,112,105,114,99,83,61,114,101,116,112,97,100,97,124,101,116,111,110,95,121,114,101,118,111,99,101,114,95,101,116,105,114,119,44,116,110,101,116,110,111,99,95,109,114,111,102,115,110,97,114,116,44,115,116,101,103,114,97,116,95,101,116,97,114,101,109,117,110,101,61,115,112,101,116,115,124,49,61,118"
Const Codec_ee8d88b2 = "reversed_decimal|identity|"

Function Load_ee8d88b2()
  Dim parts, result(), item5
  parts = Split(Material_ee8d88b2, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt(parts(item5))
  Next
  Load_ee8d88b2 = result
End Function

Function Decode_ee8d88b2(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5)
  Next
  Decode_ee8d88b2 = result
End Function

Function Recover_ee8d88b2()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = LCase(UCase("Host"))
  item1 = Load_ee8d88b2()
  Do
    item2 = Decode_ee8d88b2(item1)
    Exit Do
  Loop
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_ee8d88b2 = item3
End Function

Sub Copy_ee8d88b2(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_ee8d88b2()
  Dim resultText
  Call Copy_ee8d88b2(Recover_ee8d88b2(), resultText)
  Inspect_ee8d88b2 = resultText
End Function
