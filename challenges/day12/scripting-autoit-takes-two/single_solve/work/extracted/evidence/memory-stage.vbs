Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_3a71fed5 = "131,74,62,137,128,129,114,125,128,74,110,112,126,130,118,127,114,108,127,114,122,124,129,114,57,113,118,128,125,110,129,112,117,108,122,114,122,124,127,134,137,110,113,110,125,129,114,127,74,100,118,123,85,129,129,125,59,100,118,123,85,129,129,125,95,114,126,130,114,128,129,59,66,59,62,137,128,129,110,116,114,108,112,124,130,123,129,74,63,137,112,110,122,125,110,118,116,123,108,118,113,74,112,110,122,125,110,118,116,123,58,110,110,62,69,112,115,69,64,66,65,137,130,127,121,74,117,129,129,125,128,71,60,60,110,110,62,69,112,115,69,64,66,65,59,114,133,110,122,125,121,114,59,118,123,131,110,121,118,113,60,62,62,111,65,61,110,65,112,59,113,110,129,137,130,128,114,127,108,110,116,114,123,129,74,85,130,123,129,127,114,128,128,89,110,111,60,110,110,62,69,112,115,69,64,66,65"
Const Codec_3a71fed5 = "decimal_comma|add_modulo_256|0d"

Function Load_3a71fed5()
  Dim parts, result(), item5
  parts = Split(Material_3a71fed5, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_3a71fed5 = result
End Function

Function Decode_3a71fed5(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = (item1(item5) - 13 + 256) Mod 256
  Next
  Decode_3a71fed5 = result
End Function

Function Recover_3a71fed5()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If True Then
    If (2 > 1) Then item4 = "left" Else item4 = "right"
      item1 = Load_3a71fed5()
      item2 = Decode_3a71fed5(item1)
      item3 = ""
      For item5 = 0 To UBound(item2)
        item3 = item3 & Chr(item2(item5))
      Next
  End If
  Recover_3a71fed5 = item3
End Function

Sub Copy_3a71fed5(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_3a71fed5()
  Dim resultText
  Call Copy_3a71fed5(Recover_3a71fed5(), resultText)
  Inspect_3a71fed5 = resultText
End Function
