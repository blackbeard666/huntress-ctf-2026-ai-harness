Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_e838efaa = "105,29,124,24,54,14,57,93,62,13,62,91,109,11,51,30,123,28,125,9,122,38,68,37,105,26,105,12,126,10,100,17,89,5,102,15,99,1,116,36,120,11,121,28,111,58,102,92,31,34,74,62,95,47,112,21,121,16,118,10,50,5,97,2,49,2,103,81,55,15,32,66,35,111,28,111,10,120,12,98,23,95,98,22,120,29,122,27,68,54,83,32,85,41,93,60,88,118,64,35,26,123,76,117,65,34,13,105,0,108,13,123,21,124,82,55,91,43,70,39,95,58,20,44,27,127,28,47,28,121,79,41,17,62,17,43,88,40,92,40,64,125,17,99,22,106,82,101,1,98,81,98,7,49,87,111,66,44,75,34,67,51,94,63,92,97,5,108,51,93,58,83,50,66,47,78,45,81,99,94,42,68,49,94,61,98,7,96,1,117,6,122,74,100,82,124,44,120,44,100,40,101,61,19,33,109,32,120,43,102,91,41,76,56,72,41,77,44,80,53,89,48,86,9,108,24,113,3,116,88,61,73,38,75,46,92,3,102,20,125,8,121,26,123,70,53,69,32,84,39,91,106,87"
Const Codec_e838efaa = "reversed_decimal|rolling_xor|21"

Function Load_e838efaa()
  Dim parts, result(), item5
  parts = Split(Material_e838efaa, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt(parts(item5))
  Next
  Load_e838efaa = result
End Function

Function Decode_e838efaa(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  previous = 33
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor previous
    previous = item1(item5)
  Next
  Decode_e838efaa = result
End Function

Function Recover_e838efaa()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If (2 > 1) Then item4 = "left" Else item4 = "right"

  item1 = Load_e838efaa()

  item6 = 0

  While item6 < 1

    item2 = Decode_e838efaa(item1)

    item6 = item6 + 1

  Wend

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_e838efaa = item3
End Function

Function Inspect_e838efaa()
  Inspect_e838efaa = Recover_e838efaa()
End Function
