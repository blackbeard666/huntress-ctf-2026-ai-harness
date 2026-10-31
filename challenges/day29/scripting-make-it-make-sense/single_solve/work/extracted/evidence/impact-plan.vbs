Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_fcc1cf0b = "29:14:25:59:2a:5e:3b:4b:38:05:60:0e:7b:16:73:01:60:14:71:2e:5a:3b:49:2e:4b:3f:4c:60:14:66:07:69:1a:7c:13:61:0c:53:30:5f:31:45:20:4e:3a:16:61:13:7a:0e:6b:34:46:23:40:2f:59:3c:4e:37:68:06:69:1d:78:04:65:01:60:10:64:01:73:4e:0f:4b:04:40:02:2c:7f:0b:79:1c:7d:10:6c:1f:6b:0a:6d:08:57:34:5b:2e:40:34:09:3b:47:24:45:28:58:39:50:37:59:06:6f:0b:36:55:34:59:29:48:21:46:28:05:30:51:68:5a:6d:0b:6e:57:65:57:2b:4e:36:42:27:49:3a:53:3c:52:6f:41:25:41:75:47:75:5b:37:58:3b:50:35:51:2d:43:2c:58:3d:62:0c:6d:00:65:58:0a:4f:0c:43:15:50:02:2f:4c:2e:1e:78:1a:2a:48:2b:05:71:09:7d"
Const Codec_fcc1cf0b = "hex_colon|rolling_xor|5f"

Function Load_fcc1cf0b()
  Dim parts, result(), materialIndex
  parts = Split(Material_fcc1cf0b, ":")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_fcc1cf0b = result
End Function

Function Decode_fcc1cf0b(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  previous = 95
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor previous
    previous = storedMaterial(materialIndex)
  Next
  Decode_fcc1cf0b = result
End Function

Function Recover_fcc1cf0b()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  ' configuration reconstruction
harmlessValue = UBound(Array(3, 5, 8, 13))
  storedMaterial = Load_fcc1cf0b()
  decodePass = 0
  While decodePass < 1
    recoveredMaterial = Decode_fcc1cf0b(storedMaterial)
    decodePass = decodePass + 1
  Wend
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
' reconstruction complete
  Recover_fcc1cf0b = configurationText
End Function

Function Inspect_fcc1cf0b()
  Inspect_fcc1cf0b = Recover_fcc1cf0b()
End Function
