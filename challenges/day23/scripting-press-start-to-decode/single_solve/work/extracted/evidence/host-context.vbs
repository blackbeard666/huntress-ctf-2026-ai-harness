Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_6d35d2bd = "49,53,103,49,99,100,55,53,98,58,46,117,116,112,105,62,101,106,96,117,116,112,105,125,49,53,103,49,99,100,55,53,98,58,46,111,104,106,98,113,110,98,100,62,101,106,96,111,104,106,98,113,110,98,100,125,50,62,117,111,118,112,100,96,102,104,98,117,116,125,122,115,98,111,112,106,117,100,106,69,47,104,111,106,117,113,106,115,100,84,62,115,102,117,113,98,101,98,125,111,112,106,117,98,115,118,104,106,103,111,112,100,96,111,115,118,117,102,115,45,111,112,106,117,98,115,118,104,106,103,111,112,100,96,102,101,112,100,102,101,62,116,113,102,117,116,125,50,62,119"
Const Codec_6d35d2bd = "reversed_decimal|add_modulo_256|01"

Function Load_6d35d2bd()
  Dim parts, result(), item5
  parts = Split(Material_6d35d2bd, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt(parts(item5))
  Next
  Load_6d35d2bd = result
End Function

Function Decode_6d35d2bd(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = (item1(item5) - 1 + 256) Mod 256
  Next
  Decode_6d35d2bd = result
End Function

Function Recover_6d35d2bd()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If True Then
    item4 = LCase(UCase("Host"))
      item1 = Load_6d35d2bd()
      On Error Resume Next
      item2 = Decode_6d35d2bd(item1)
      item7 = Err.Number
      item8 = Err.Description
      On Error GoTo 0
      If item7 <> 0 Then Err.Raise item7, "HuntressFixture", item8
      item3 = ""
      For item5 = 0 To UBound(item2)
        item3 = item3 & Chr(item2(item5))
      Next
  End If
  Recover_6d35d2bd = item3
End Function

Sub Copy_6d35d2bd(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_6d35d2bd()
  Dim resultText
  Call Copy_6d35d2bd(Recover_6d35d2bd(), resultText)
  Inspect_6d35d2bd = resultText
End Function
