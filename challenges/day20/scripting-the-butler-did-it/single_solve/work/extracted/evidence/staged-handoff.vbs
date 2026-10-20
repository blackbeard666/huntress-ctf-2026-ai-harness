Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_2182c7a9 = "49,115,112,46,101,108,112,109,97,115,45,101,99,114,117,111,115,101,114,61,101,103,97,116,115,95,116,120,101,110,124,57,49,48,55,48,53,97,49,97,100,92,101,108,98,97,115,111,112,115,105,68,92,98,97,76,115,115,101,114,116,110,117,72,92,101,114,97,119,116,102,111,83,92,85,67,75,72,61,104,116,97,112,95,121,114,116,115,105,103,101,114,124,116,97,100,46,57,49,48,55,48,53,97,49,97,100,45,101,103,97,116,115,92,98,97,76,115,115,101,114,116,110,117,72,92,99,105,108,98,117,80,92,115,114,101,115,85,92,58,67,61,104,116,97,112,95,101,108,105,102,124,57,49,48,55,48,53,97,49,97,100,47,98,97,76,115,115,101,114,116,110,117,72,61,116,110,101,103,97,95,114,101,115,117,124,116,97,100,46,100,102,54,54,55,56,52,53,47,100,105,108,97,118,110,105,46,101,108,112,109,97,120,101,46,57,49,48,55,48,53,97,49,97,100,47,47,58,115,112,116,116,104,61,108,114,117,124,57,49,48,55,48,53,97,49,97,100,45,110,103,105,97,112,109,97,99,61,100,105,95,110,103,105,97,112,109,97,99,124,52,61,116,110,117,111,99,95,101,103,97,116,115,124,48,46,54,46,80,84,84,72,76,77,88,46,50,76,77,88,83,77,61,114,101,116,112,97,100,97,124,116,112,105,114,99,115,95,102,102,111,100,110,97,104,44,115,115,101,99,111,114,112,95,104,99,116,97,112,115,105,100,44,101,108,105,102,95,101,116,105,114,119,44,101,116,111,109,101,114,95,101,114,105,117,113,99,97,61,115,112,101,116,115,124,49,61,118"
Const Codec_2182c7a9 = "reversed_decimal|identity|"

Function Load_2182c7a9()
  Dim parts, result(), item5
  parts = Split(Material_2182c7a9, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt(parts(item5))
  Next
  Load_2182c7a9 = result
End Function

Function Decode_2182c7a9(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5)
  Next
  Decode_2182c7a9 = result
End Function

Function Recover_2182c7a9()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
item4 = (19 * 7) - 133
  item1 = Load_2182c7a9()
  item6 = 0
  While item6 < 1
    item2 = Decode_2182c7a9(item1)
    item6 = item6 + 1
  Wend
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_2182c7a9 = item3
End Function

Function Inspect_2182c7a9()
  Inspect_2182c7a9 = Recover_2182c7a9()
End Function
