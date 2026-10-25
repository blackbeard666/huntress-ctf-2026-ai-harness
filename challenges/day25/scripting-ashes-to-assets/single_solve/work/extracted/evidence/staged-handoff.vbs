Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_1cca281f = "76:3d:31:7c:73:74:65:70:73:3d:61:63:71:75:69:72:65:5f:72:65:6d:6f:74:65:2c:77:72:69:74:65:5f:66:69:6c:65:2c:64:69:73:70:61:74:63:68:5f:70:72:6f:63:65:73:73:2c:68:61:6e:64:6f:66:66:5f:73:63:72:69:70:74:7c:61:64:61:70:74:65:72:3d:57:69:6e:48:74:74:70:2e:57:69:6e:48:74:74:70:52:65:71:75:65:73:74:2e:35:2e:31:7c:73:74:61:67:65:5f:63:6f:75:6e:74:3d:34:7c:63:61:6d:70:61:69:67:6e:5f:69:64:3d:63:61:6d:70:61:69:67:6e:2d:30:65:39:31:64:64:32:31:64:61:7c:75:72:6c:3d:68:74:74:70:73:3a:2f:2f:30:65:39:31:64:64:32:31:64:61:2e:65:78:61:6d:70:6c:65:2e:69:6e:76:61:6c:69:64:2f:38:38:63:39:64:65:39:33:2e:64:61:74:7c:75:73:65:72:5f:61:67:65:6e:74:3d:48:75:6e:74:72:65:73:73:4c:61:62:2f:30:65:39:31:64:64:32:31:64:61:7c:66:69:6c:65:5f:70:61:74:68:3d:43:3a:5c:55:73:65:72:73:5c:50:75:62:6c:69:63:5c:48:75:6e:74:72:65:73:73:4c:61:62:5c:73:74:61:67:65:2d:30:65:39:31:64:64:32:31:64:61:2e:64:61:74:7c:72:65:67:69:73:74:72:79:5f:70:61:74:68:3d:48:4b:43:55:5c:53:6f:66:74:77:61:72:65:5c:48:75:6e:74:72:65:73:73:4c:61:62:5c:44:69:73:70:6f:73:61:62:6c:65:5c:30:65:39:31:64:64:32:31:64:61:7c:6e:65:78:74:5f:73:74:61:67:65:3d:72:65:73:6f:75:72:63:65:2d:73:61:6d:70:6c:65:2e:70:73:31"
Const Codec_1cca281f = "reversed_hex|reverse_bytes|"

Function Load_1cca281f()
  Dim parts, result(), i
  parts = Split(Material_1cca281f, ":")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt("&H" & parts(i))
  Next
  Load_1cca281f = result
End Function

Function Decode_1cca281f(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(UBound(s) - i) = s(i)
  Next
  Decode_1cca281f = result
End Function

Function Recover_1cca281f()
  Dim s, d, t, n, i, p, e, q
  If True Then
    n = (19 * 7) - 133
      s = Load_1cca281f()
      On Error Resume Next
      d = Decode_1cca281f(s)
      e = Err.Number
      q = Err.Description
      On Error GoTo 0
      If e <> 0 Then Err.Raise e, "HuntressFixture", q
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_1cca281f = t
End Function

Function Inspect_1cca281f()
  Inspect_1cca281f = Recover_1cca281f()
End Function
