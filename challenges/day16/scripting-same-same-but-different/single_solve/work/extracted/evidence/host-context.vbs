Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_555f71ab = "4f:7e:83:81:55:82:54:4e:54:4e:4a:91:90:8c:85:5a:81:86:7c:91:90:8c:85:99:4f:7e:83:81:55:82:54:4e:54:4e:4a:8b:84:86:7e:8d:8a:7e:80:5a:81:86:7c:8b:84:86:7e:8d:8a:7e:80:99:4e:5a:91:8b:92:8c:80:7c:82:84:7e:91:90:99:91:80:82:87:7f:6c:8a:82:91:90:96:70:82:89:86:63:4b:84:8b:86:91:8d:86:8f:80:70:5a:8f:82:91:8d:7e:81:7e:99:8b:8c:86:91:7e:8f:92:84:86:83:8b:8c:80:7c:8b:8f:92:91:82:8f:49:8b:8c:86:91:7e:8f:92:84:86:83:8b:8c:80:7c:82:81:8c:80:82:81:5a:90:8d:82:91:90:99:4e:5a:93"
Const Codec_555f71ab = "reversed_hex|add_modulo_256|1d"

Function Load_555f71ab()
  Dim parts, result(), i
  parts = Split(Material_555f71ab, ":")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt("&H" & parts(i))
  Next
  Load_555f71ab = result
End Function

Function Decode_555f71ab(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) - 29 + 256) Mod 256
  Next
  Decode_555f71ab = result
End Function

Function Recover_555f71ab()
  Dim s, d, t, n, i, p, e, q
  n = (19 * 7) - 133
  s = Load_555f71ab()
  d = Decode_555f71ab(s)
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
  Recover_555f71ab = t
End Function

Function Inspect_555f71ab()
  Inspect_555f71ab = Recover_555f71ab()
End Function
