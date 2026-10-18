Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_d4baa12f = "251,247,251,161,191,184,183,186,186,189,187,237,162,221,202,217,192,204,202,221,178,234,226,238,225,208,234,251,224,225,243,235,234,228,236,224,227,161,238,186,235,189,234,161,178,225,224,230,252,225,234,251,247,234,243,186,236,187,182,185,183,190,238,186,238,162,225,232,230,238,255,226,238,236,178,235,230,208,225,232,230,238,255,226,238,236,243,189,178,251,225,250,224,236,208,234,232,238,251,252,243,251,236,234,229,237,192,226,234,251,252,246,220,234,227,230,201,161,232,225,230,251,255,230,253,236,220,178,253,234,251,255,238,235,238,243,234,251,224,225,208,246,253,234,249,224,236,234,253,208,234,251,230,253,248,163,251,225,234,251,225,224,236,208,226,253,224,233,252,225,238,253,251,163,252,251,234,232,253,238,251,208,234,251,238,253,234,226,250,225,234,178,252,255,234,251,252,243,190,178,249"
Const Codec_d4baa12f = "decimal_comma|reverse_then_xor|8f"

Function Load_d4baa12f()
  Dim parts, result(), item5
  parts = Split(Material_d4baa12f, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_d4baa12f = result
End Function

Function Decode_d4baa12f(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5) Xor 143
  Next
  Decode_d4baa12f = result
End Function

Function Recover_d4baa12f()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If True Then
    item4 = UBound(Array(3, 5, 8, 13))
      item1 = Load_d4baa12f()
      On Error Resume Next
      item2 = Decode_d4baa12f(item1)
      item7 = Err.Number
      item8 = Err.Description
      On Error GoTo 0
      If item7 <> 0 Then Err.Raise item7, "HuntressFixture", item8
      item3 = ""
      For item5 = 0 To UBound(item2)
        item3 = item3 & Chr(item2(item5))
      Next
  End If
  Recover_d4baa12f = item3
End Function

Function Inspect_d4baa12f()
  Inspect_d4baa12f = Recover_d4baa12f()
End Function
