Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_8171023f = "34:66:35:3c:68:34:34:34:66:3a:31:78:77:73:6c:41:68:6d:63:78:77:73:6c:80:34:66:35:3c:68:34:34:34:66:3a:31:72:6b:6d:65:74:71:65:67:41:68:6d:63:72:6b:6d:65:74:71:65:67:80:35:41:78:72:79:73:67:63:69:6b:65:78:77:80:78:67:69:6e:66:53:71:69:78:77:7d:57:69:70:6d:4a:32:6b:72:6d:78:74:6d:76:67:57:41:76:69:78:74:65:68:65:80:72:73:6d:78:65:76:79:6b:6d:6a:72:73:67:63:72:76:79:78:69:76:30:72:73:6d:78:65:76:79:6b:6d:6a:72:73:67:63:69:68:73:67:69:68:41:77:74:69:78:77:80:35:41:7a"
Const Codec_8171023f = "reversed_hex|add_modulo_256|04"

Function Load_8171023f()
  Dim parts, result(), i
  parts = Split(Material_8171023f, ":")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt("&H" & parts(i))
  Next
  Load_8171023f = result
End Function

Function Decode_8171023f(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) - 4 + 256) Mod 256
  Next
  Decode_8171023f = result
End Function

Function Recover_8171023f()
  Dim s, d, t, n, i, p, e, q
  n = (19 * 7) - 133
  s = Load_8171023f()
  p = 0
  While p < 1
    d = Decode_8171023f(s)
    p = p + 1
  Wend
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
  Recover_8171023f = t
End Function

Function Inspect_8171023f()
  Inspect_8171023f = Recover_8171023f()
End Function
