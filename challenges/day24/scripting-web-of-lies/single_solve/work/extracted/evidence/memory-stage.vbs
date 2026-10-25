Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_bd734480 = "49,48,57,100,55,57,49,48,98,102,47,98,97,76,115,115,101,114,116,110,117,72,61,116,110,101,103,97,95,114,101,115,117,124,116,97,100,46,49,49,99,50,101,102,55,99,47,100,105,108,97,118,110,105,46,101,108,112,109,97,120,101,46,49,48,57,100,55,57,49,48,98,102,47,47,58,115,112,116,116,104,61,108,114,117,124,49,48,57,100,55,57,49,48,98,102,45,110,103,105,97,112,109,97,99,61,100,105,95,110,103,105,97,112,109,97,99,124,50,61,116,110,117,111,99,95,101,103,97,116,115,124,48,46,54,46,80,84,84,72,76,77,88,46,50,76,77,88,83,77,61,114,101,116,112,97,100,97,124,121,114,111,109,101,109,95,104,99,116,97,112,115,105,100,44,101,116,111,109,101,114,95,101,114,105,117,113,99,97,61,115,112,101,116,115,124,49,61,118"
Const Codec_bd734480 = "reversed_decimal|identity|"

Function Load_bd734480()
  Dim parts, result(), item5
  parts = Split(Material_bd734480, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt(parts(item5))
  Next
  Load_bd734480 = result
End Function

Function Decode_bd734480(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5)
  Next
  Decode_bd734480 = result
End Function

Function Recover_bd734480()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
If (2 > 1) Then item4 = "left" Else item4 = "right"
  item1 = Load_bd734480()
  On Error Resume Next
  item2 = Decode_bd734480(item1)
  item7 = Err.Number
  item8 = Err.Description
  On Error GoTo 0
  If item7 <> 0 Then Err.Raise item7, "HuntressFixture", item8
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_bd734480 = item3
End Function

Function Inspect_bd734480()
  Dim fields
  fields = Split(Recover_bd734480(), "|")
  Inspect_bd734480 = Join(fields, "|")
End Function
