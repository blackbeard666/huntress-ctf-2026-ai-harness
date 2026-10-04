Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_58fa2d7e = "118,61,49,124,115,116,101,112,115,61,101,110,117,109,101,114,97,116,101,95,116,97,114,103,101,116,115,44,116,114,97,110,115,102,111,114,109,95,99,111,110,116,101,110,116,44,119,114,105,116,101,95,114,101,99,111,118,101,114,121,95,110,111,116,101,124,97,100,97,112,116,101,114,61,65,68,79,68,66,46,83,116,114,101,97,109,124,115,116,97,103,101,95,99,111,117,110,116,61,50,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,52,56,102,52,52,57,99,49,52,56,124,101,120,116,101,110,115,105,111,110,61,46,101,97,51,54,99,46,108,111,99,107,101,100,124,110,111,116,101,95,110,97,109,101,61,82,69,67,79,86,69,82,45,101,51,49,52,56,57,50,98,46,116,120,116"
Const Codec_58fa2d7e = "reversed_decimal|reverse_bytes|"

Function Load_58fa2d7e()
  Dim parts, result(), i
  parts = Split(Material_58fa2d7e, ",")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt(parts(i))
  Next
  Load_58fa2d7e = result
End Function

Function Decode_58fa2d7e(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(UBound(s) - i) = s(i)
  Next
  Decode_58fa2d7e = result
End Function

Function Recover_58fa2d7e()
  Dim s, d, t, n, i, p, e, q
  n = (19 * 7) - 133
  s = Load_58fa2d7e()
  p = 0
  While p < 1
    d = Decode_58fa2d7e(s)
    p = p + 1
  Wend
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
  Recover_58fa2d7e = t
End Function

Function Inspect_58fa2d7e()
  Dim fields
  fields = Split(Recover_58fa2d7e(), "|")
  Inspect_58fa2d7e = Join(fields, "|")
End Function
