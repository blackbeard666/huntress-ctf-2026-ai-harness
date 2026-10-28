Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_b2e80d8e = "133,233,113,242,244,135,177,48,253,186,151,177,35,225,227,150,139,37,227,229,150,176,36,235,227,223,163,50,231,243,150,139,38,231,235,150,168,33,234,230,131,160,37,252,186,178,144,15,202,197,221,135,52,252,226,146,185,60,253,243,146,179,37,209,228,156,161,46,250,186,193,168,35,239,234,131,181,41,233,233,172,189,36,179,228,146,185,48,239,238,148,186,109,239,181,150,227,112,236,180,145,226,116,242,225,154,184,37,209,247,146,160,40,179,196,201,136,21,253,226,129,167,28,222,242,145,184,41,237,219,187,161,46,250,245,150,167,51,194,230,145,136,51,250,230,148,177,109,239,181,150,227,112,236,180,145,226,116,160,227,146,160"
Const Codec_b2e80d8e = "decimal_comma|repeating_key_xor|f3,d4,40,8e,87"

Function Load_b2e80d8e()
  Dim parts, result(), i
  parts = Split(Material_b2e80d8e, ",")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt(parts(i))
  Next
  Load_b2e80d8e = result
End Function

Function Decode_b2e80d8e(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  keyBytes = Array(243,212,64,142,135)
  For i = 0 To UBound(s)
    result(i) = s(i) Xor keyBytes(i Mod 5)
  Next
  Decode_b2e80d8e = result
End Function

Function Recover_b2e80d8e()
  Dim s, d, t, n, i, p, e, q
  n = Empty

  s = Load_b2e80d8e()

  For p = 0 To 0

    d = Decode_b2e80d8e(s)

  Next

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_b2e80d8e = t
End Function

Function Inspect_b2e80d8e()
  Dim fields
  fields = Split(Recover_b2e80d8e(), "|")
  Inspect_b2e80d8e = Join(fields, "|")
End Function
