Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_74dc273f = "165,176,181,255,178,180,227,232,228,231,228,229,232,230,252,180,182,176,165,162,141,179,176,157,162,162,180,163,165,191,164,153,141,178,184,189,179,164,129,141,162,163,180,162,132,141,235,146,236,185,165,176,161,142,180,189,184,183,173,178,180,227,232,228,231,228,229,232,230,252,191,182,184,176,161,188,176,178,236,181,184,142,191,182,184,176,161,188,176,178,173,227,236,165,191,164,190,178,142,180,182,176,165,162,173,165,178,180,187,179,158,188,180,165,162,168,130,180,189,184,151,255,182,191,184,165,161,184,163,178,130,236,163,180,165,161,176,181,176,173,180,189,184,183,142,180,165,184,163,166,253,181,180,181,181,180,179,188,180,142,180,181,190,178,180,181,236,162,161,180,165,162,173,224,236,167"
Const Codec_74dc273f = "decimal_comma|reverse_then_xor|d1"

Function Load_74dc273f()
  Dim parts, result(), item5
  parts = Split(Material_74dc273f, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_74dc273f = result
End Function

Function Decode_74dc273f(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5) Xor 209
  Next
  Decode_74dc273f = result
End Function

Function Recover_74dc273f()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = (19 * 7) - 133
  item1 = Load_74dc273f()
  Do
    item2 = Decode_74dc273f(item1)
    Exit Do
  Loop
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_74dc273f = item3
End Function

Function Inspect_74dc273f()
  Dim fields
  fields = Split(Recover_74dc273f(), "|")
  Inspect_74dc273f = Join(fields, "|")
End Function
