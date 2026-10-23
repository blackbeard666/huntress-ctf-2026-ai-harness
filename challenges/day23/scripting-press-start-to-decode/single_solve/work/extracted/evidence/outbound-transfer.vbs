Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_1664093e = "39:72:7e:33:3c:3b:2a:3f:3c:72:23:20:2c:2e:3b:2a:10:23:20:2c:2e:23:63:3f:3d:2a:3f:2e:3d:2a:10:3b:3d:2e:21:3c:29:2a:3d:63:3a:3f:23:20:2e:2b:10:3d:2a:22:20:3b:2a:33:2e:2b:2e:3f:3b:2a:3d:72:0c:2a:3d:3b:1d:2a:3e:61:2a:37:2a:33:3c:3b:2e:28:2a:10:2c:20:3a:21:3b:72:7d:33:2c:2e:22:3f:2e:26:28:21:10:26:2b:72:2c:2e:22:3f:2e:26:28:21:62:7a:7e:76:78:7a:77:7d:79:76:7f:33:3a:3d:23:72:27:3b:3b:3f:3c:75:60:60:7a:7e:76:78:7a:77:7d:79:76:7f:61:2a:37:2e:22:3f:23:2a:61:26:21:39:2e:23:26:2b:60:2c:29:2a:79:79:7b:7d:2d:61:2b:2e:3b:33:3a:3c:2a:3d:10:2e:28:2a:21:3b:72:07:3a:21:3b:3d:2a:3c:3c:03:2e:2d:60:7a:7e:76:78:7a:77:7d:79:76:7f:33:29:26:23:2a:10:3f:2e:3b:27:72:0c:75:13:1a:3c:2a:3d:3c:13:1f:3a:2d:23:26:2c:13:07:3a:21:3b:3d:2a:3c:3c:03:2e:2d:13:3c:3b:2e:28:2a:62:7a:7e:76:78:7a:77:7d:79:76:7f:61:2b:2e:3b:33:3a:3f:23:20:2e:2b:10:3a:3d:23:72:27:3b:3b:3f:3c:75:60:60:7a:7e:76:78:7a:77:7d:79:76:7f:61:2a:37:2e:22:3f:23:2a:61:26:21:39:2e:23:26:2b:60:3a:3f:23:20:2e:2b:60:7c:2b:7a:7e:2c:77:7e:76"
Const Codec_1664093e = "hex_colon|single_byte_xor|4f"

Function Load_1664093e()
  Dim parts, result(), materialIndex
  parts = Split(Material_1664093e, ":")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_1664093e = result
End Function

Function Decode_1664093e(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor 79
  Next
  Decode_1664093e = result
End Function

Function Recover_1664093e()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"

  storedMaterial = Load_1664093e()

  decodePass = 0

  While decodePass < 1

    recoveredMaterial = Decode_1664093e(storedMaterial)

    decodePass = decodePass + 1

  Wend

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_1664093e = configurationText
End Function

Function Inspect_1664093e()
  Inspect_1664093e = Recover_1664093e()
End Function
