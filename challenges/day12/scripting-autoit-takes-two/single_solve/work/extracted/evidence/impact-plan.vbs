Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_7fe6d440 = "84:4b:3f:8a:81:82:73:7e:81:4b:73:7c:83:7b:73:80:6f:82:73:6d:82:6f:80:75:73:82:81:3a:82:80:6f:7c:81:74:7d:80:7b:6d:71:7d:7c:82:73:7c:82:3a:85:80:77:82:73:6d:80:73:71:7d:84:73:80:87:6d:7c:7d:82:73:8a:6f:72:6f:7e:82:73:80:4b:4f:52:5d:52:50:3c:61:82:80:73:6f:7b:8a:81:82:6f:75:73:6d:71:7d:83:7c:82:4b:40:8a:71:6f:7b:7e:6f:77:75:7c:6d:77:72:4b:71:6f:7b:7e:6f:77:75:7c:3b:40:71:70:6f:72:71:73:42:46:73:8a:73:86:82:73:7c:81:77:7d:7c:4b:3c:43:43:43:6f:3e:3c:7a:7d:71:79:73:72:8a:7c:7d:82:73:6d:7c:6f:7b:73:4b:60:53:51:5d:64:53:60:3b:6f:72:74:73:40:45:41:41:3c:82:86:82"
Const Codec_7fe6d440 = "hex_colon|add_modulo_256|0e"

Function Load_7fe6d440()
  Dim parts, result(), i
  parts = Split(Material_7fe6d440, ":")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt("&H" & parts(i))
  Next
  Load_7fe6d440 = result
End Function

Function Decode_7fe6d440(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) - 14 + 256) Mod 256
  Next
  Decode_7fe6d440 = result
End Function

Function Recover_7fe6d440()
  Dim s, d, t, n, i, p, e, q
  ' configuration reconstruction
n = UBound(Array(3, 5, 8, 13))
  s = Load_7fe6d440()
  On Error Resume Next
  d = Decode_7fe6d440(s)
  e = Err.Number
  q = Err.Description
  On Error GoTo 0
  If e <> 0 Then Err.Raise e, "HuntressFixture", q
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
' reconstruction complete
  Recover_7fe6d440 = t
End Function

Function Inspect_7fe6d440()
  Inspect_7fe6d440 = Recover_7fe6d440()
End Function
