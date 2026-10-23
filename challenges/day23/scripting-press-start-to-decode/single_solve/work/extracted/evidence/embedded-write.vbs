Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_16c233ff = "244,128,225,133,171,156,253,206,249,204,255,155,168,204,250,215,178,213,180,192,179,239,141,236,160,211,160,197,183,195,173,216,144,204,175,198,170,200,189,237,177,194,176,213,166,243,175,149,214,235,131,247,150,230,185,220,176,217,191,195,244,149,166,145,164,151,243,192,164,146,191,209,182,223,190,206,163,194,161,156,248,145,206,160,199,174,207,191,210,179,208,172,158,163,215,185,204,163,192,159,250,157,252,136,251,135,243,144,245,159,253,178,223,186,206,189,196,151,242,158,247,177,159,248,150,255,139,251,146,224,131,208,237,159,250,142,254,159,251,154,230,131,239,134,224,191,218,174,199,181,194,238,138,239,139,239,138,232,133,224,191,218,190,209,178,215,179,142,253,141,232,156,239,147,162,159"
Const Codec_16c233ff = "reversed_decimal|rolling_xor|e9"

Function Load_16c233ff()
  Dim parts, result(), item5
  parts = Split(Material_16c233ff, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt(parts(item5))
  Next
  Load_16c233ff = result
End Function

Function Decode_16c233ff(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  previous = 233
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor previous
    previous = item1(item5)
  Next
  Decode_16c233ff = result
End Function

Function Recover_16c233ff()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If True Then
    item4 = UBound(Array(3, 5, 8, 13))
      item1 = Load_16c233ff()
      Do
        item2 = Decode_16c233ff(item1)
        Exit Do
      Loop
      item3 = ""
      For item5 = 0 To UBound(item2)
        item3 = item3 & Chr(item2(item5))
      Next
  End If
  Recover_16c233ff = item3
End Function

Sub Copy_16c233ff(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_16c233ff()
  Dim resultText
  Call Copy_16c233ff(Recover_16c233ff(), resultText)
  Inspect_16c233ff = resultText
End Function
