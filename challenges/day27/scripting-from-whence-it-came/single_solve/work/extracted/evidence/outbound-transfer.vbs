Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_456d1b25 = "2c:11:20:5c:2f:5b:3e:4e:3d:00:6c:03:60:01:75:10:4f:23:4c:2f:4e:22:0e:7e:0c:69:19:78:0a:6f:30:44:36:57:39:4a:2c:49:3b:17:62:12:7e:11:70:14:4b:39:5c:31:5e:2a:4f:33:52:36:57:27:53:36:44:79:3a:55:3b:5d:34:53:00:65:06:73:01:68:1c:65:35:5a:36:5f:3c:45:6b:0e:76:13:6f:1c:68:09:6e:0b:54:37:58:2d:43:37:0a:38:44:27:46:2b:5b:3a:53:34:5a:05:6c:08:35:56:37:5a:2a:4b:22:45:2b:06:33:51:37:00:62:06:3e:5a:39:0d:71:04:76:1a:27:4f:3b:4f:3f:4c:76:59:76:43:21:47:70:12:76:4e:2a:49:7d:53:36:4e:2f:42:32:5e:3b:15:7c:12:64:05:69:00:64:4b:28:4e:79:1b:7d:4c:2a:19:37:53:32:46:3a:4f:3c:59:2b:74:15:72:17:79:0d:30:78:0d:63:17:65:00:73:00:4c:2d:4f:60:55:37:51:66:04:60:58:3c:5f:6b:17:71:18:74:11:4e:3e:5f:2b:43:7e:3d:07:5b:0e:7d:18:6a:19:45:15:60:02:6e:07:64:38:70:05:6b:1f:6d:08:7b:08:44:25:47:1b:68:1c:7d:1a:7f:52:67:05:63:54:36:52:6a:0e:6d:59:77:13:72:06:7a:0f:7f:13:7c:1d:79:26:53:21:4d:70:18:6c:18:68:1b:21:0e:21:14:76:10:27:45:21:19:7d:1e:2a:04:61:19:78:15:65:09:6c:42:2b:45:33:52:3e:57:33:1c:69:19:75:1a:7b:1f:30:56:32:0b:68:0c:35:57:61"
Const Codec_456d1b25 = "hex_colon|rolling_xor|5a"

Function Load_456d1b25()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_456d1b25, ":")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt("&H" & parts(ByTeInDeX))
  Next
  Load_456d1b25 = result
End Function

Function Decode_456d1b25(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  previous = 90
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor previous
    previous = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_456d1b25 = result
End Function

Function Recover_456d1b25()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = Join(Array("north", "south"), ":")
  SoUrCeByTeS = Load_456d1b25()
  Do
    DeCoDeDByTeS = Decode_456d1b25(SoUrCeByTeS)
    Exit Do
  Loop
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
  Recover_456d1b25 = DeScRiPtOrTeXt
End Function

Function Inspect_456d1b25()
  Dim fields
  fields = Split(Recover_456d1b25(), "|")
  Inspect_456d1b25 = Join(fields, "|")
End Function
