Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_e2cd6f85 = "214,235,218,166,213,161,196,180,199,250,155,248,137,252,149,231,130,221,175,202,167,200,188,217,245,145,248,139,251,154,238,141,229,186,215,178,223,176,194,187,199,166,194,163,211,167,194,176,141,192,169,202,184,215,164,203,173,217,247,175,226,174,230,178,230,182,202,185,205,172,203,174,241,146,253,136,230,146,175,157,225,130,227,142,254,159,246,145,255,160,201,173,144,243,146,255,143,238,135,224,142,163,198,241,200,252,158,174,203,242,148,166,218,175,221,177,140,228,144,228,148,231,221,242,221,184,143,182,130,224,208,181,140,234,216,246,147,235,138,231,151,251,158,176,217,183,193,160,204,165,193,238,214,183,130,228,214,238,223,234,196,160,193,181,201,188,207,170,216,135,230,129,228,138,254,195,139,254,144,228,150,243,128,243,191,222,188,147,246,193,248,204,174,158,251,194,164,150"
Const Codec_e2cd6f85 = "decimal_comma|rolling_xor|a0"

Function Load_e2cd6f85()
  Dim parts, result(), item5
  parts = Split(Material_e2cd6f85, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_e2cd6f85 = result
End Function

Function Decode_e2cd6f85(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  previous = 160
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor previous
    previous = item1(item5)
  Next
  Decode_e2cd6f85 = result
End Function

Function Recover_e2cd6f85()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = Join(Array("north", "south"), ":")
  item1 = Load_e2cd6f85()
  For item6 = 0 To 0
    item2 = Decode_e2cd6f85(item1)
  Next
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_e2cd6f85 = item3
End Function

Function Inspect_e2cd6f85()
  Dim fields
  fields = Split(Recover_e2cd6f85(), "|")
  Inspect_e2cd6f85 = Join(fields, "|")
End Function
