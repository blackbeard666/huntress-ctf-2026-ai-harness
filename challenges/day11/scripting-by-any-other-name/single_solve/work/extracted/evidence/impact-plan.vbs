Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_6eb1f6e6 = "5f:63:5f:19:20:20:4f:4c:1d:4e:20:4f:18:3d:30:41:3a:2e:30:3d:28:50:58:4c:59:4a:50:5f:5a:59:67:4f:50:56:4e:5a:57:19:1f:1d:4e:1c:4e:19:28:59:5a:54:5e:59:50:5f:63:50:67:22:21:23:1f:1d:4f:4c:4f:51:4f:18:59:52:54:4c:5b:58:4c:4e:28:4f:54:4a:59:52:54:4c:5b:58:4c:4e:67:1d:28:5f:59:60:5a:4e:4a:50:52:4c:5f:5e:67:5f:4e:50:55:4d:3a:58:50:5f:5e:64:3e:50:57:54:31:19:52:59:54:5f:5b:54:5d:4e:3e:28:5d:50:5f:5b:4c:4f:4c:67:50:5f:5a:59:4a:64:5d:50:61:5a:4e:50:5d:4a:50:5f:54:5d:62:17:5f:59:50:5f:59:5a:4e:4a:58:5d:5a:51:5e:59:4c:5d:5f:17:5e:5f:50:52:5d:4c:5f:4a:50:5f:4c:5d:50:58:60:59:50:28:5e:5b:50:5f:5e:67:1c:28:61"
Const Codec_6eb1f6e6 = "reversed_hex|subtract_modulo_256|15"

Function Load_6eb1f6e6()
  Dim parts, result(), i
  parts = Split(Material_6eb1f6e6, ":")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt("&H" & parts(i))
  Next
  Load_6eb1f6e6 = result
End Function

Function Decode_6eb1f6e6(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) + 21) Mod 256
  Next
  Decode_6eb1f6e6 = result
End Function

Function Recover_6eb1f6e6()
  Dim s, d, t, n, i, p, e, q
  n = Empty

  s = Load_6eb1f6e6()

  On Error Resume Next

  d = Decode_6eb1f6e6(s)

  e = Err.Number

  q = Err.Description

  On Error GoTo 0

  If e <> 0 Then Err.Raise e, "HuntressFixture", q

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_6eb1f6e6 = t
End Function

Function Inspect_6eb1f6e6()
  Inspect_6eb1f6e6 = Recover_6eb1f6e6()
End Function
