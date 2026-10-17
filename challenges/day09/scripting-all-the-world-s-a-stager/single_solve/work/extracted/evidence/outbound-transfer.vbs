Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_435c9e1b = "118,61,49,124,115,116,101,112,115,61,108,111,99,97,116,101,95,108,111,99,97,108,44,112,114,101,112,97,114,101,95,116,114,97,110,115,102,101,114,44,117,112,108,111,97,100,95,114,101,109,111,116,101,124,97,100,97,112,116,101,114,61,67,101,114,116,82,101,113,46,101,120,101,124,115,116,97,103,101,95,99,111,117,110,116,61,50,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,57,101,98,50,97,53,97,102,100,51,124,117,114,108,61,104,116,116,112,115,58,47,47,57,101,98,50,97,53,97,102,100,51,46,101,120,97,109,112,108,101,46,105,110,118,97,108,105,100,47,101,102,53,54,51,52,56,55,46,100,97,116,124,117,115,101,114,95,97,103,101,110,116,61,72,117,110,116,114,101,115,115,76,97,98,47,57,101,98,50,97,53,97,102,100,51,124,102,105,108,101,95,112,97,116,104,61,67,58,92,85,115,101,114,115,92,80,117,98,108,105,99,92,72,117,110,116,114,101,115,115,76,97,98,92,115,116,97,103,101,45,57,101,98,50,97,53,97,102,100,51,46,100,97,116,124,117,112,108,111,97,100,95,117,114,108,61,104,116,116,112,115,58,47,47,57,101,98,50,97,53,97,102,100,51,46,101,120,97,109,112,108,101,46,105,110,118,97,108,105,100,47,117,112,108,111,97,100,47,53,101,56,48,57,97,57,57"
Const Codec_435c9e1b = "reversed_decimal|reverse_bytes|"

Function Load_435c9e1b()
  Dim parts, result(), item5
  parts = Split(Material_435c9e1b, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt(parts(item5))
  Next
  Load_435c9e1b = result
End Function

Function Decode_435c9e1b(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5)
  Next
  Decode_435c9e1b = result
End Function

Function Recover_435c9e1b()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If (2 > 1) Then item4 = "left" Else item4 = "right"
  item1 = Load_435c9e1b()
  On Error Resume Next
  item2 = Decode_435c9e1b(item1)
  item7 = Err.Number
  item8 = Err.Description
  On Error GoTo 0
  If item7 <> 0 Then Err.Raise item7, "HuntressFixture", item8
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_435c9e1b = item3
End Function

Function Inspect_435c9e1b()
  Dim fields
  fields = Split(Recover_435c9e1b(), "|")
  Inspect_435c9e1b = Join(fields, "|")
End Function
