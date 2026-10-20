Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_98758940 = "192,139,135,202,197,194,211,198,197,139,218,217,213,215,194,211,233,218,217,213,215,218,154,210,223,197,198,215,194,213,222,233,198,196,217,213,211,197,197,202,215,210,215,198,194,211,196,139,225,229,213,196,223,198,194,152,229,222,211,218,218,202,197,194,215,209,211,233,213,217,195,216,194,139,132,202,213,215,219,198,215,223,209,216,233,223,210,139,213,215,219,198,215,223,209,216,155,128,135,213,133,142,135,215,142,211,132,202,208,223,218,211,233,198,215,194,222,139,245,140,234,227,197,211,196,197,234,230,195,212,218,223,213,234,254,195,216,194,196,211,197,197,250,215,212,234,197,194,215,209,211,155,128,135,213,133,142,135,215,142,211,132,152,210,215,194"
Const Codec_98758940 = "decimal_comma|single_byte_xor|b6"

Function Load_98758940()
  Dim parts, result(), item5
  parts = Split(Material_98758940, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_98758940 = result
End Function

Function Decode_98758940(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor 182
  Next
  Decode_98758940 = result
End Function

Function Recover_98758940()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = LCase(UCase("Host"))
  item1 = Load_98758940()
  Do
    item2 = Decode_98758940(item1)
    Exit Do
  Loop
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_98758940 = item3
End Function

Function Inspect_98758940()
  Inspect_98758940 = Recover_98758940()
End Function
