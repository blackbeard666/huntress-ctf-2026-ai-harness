Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_6f9f2d08 = "76:3d:31:7c:73:74:65:70:73:3d:61:63:71:75:69:72:65:5f:72:65:6d:6f:74:65:2c:77:72:69:74:65:5f:66:69:6c:65:2c:64:69:73:70:61:74:63:68:5f:70:72:6f:63:65:73:73:2c:68:61:6e:64:6f:66:66:5f:73:63:72:69:70:74:7c:61:64:61:70:74:65:72:3d:4d:69:63:72:6f:73:6f:66:74:2e:58:4d:4c:48:54:54:50:7c:73:74:61:67:65:5f:63:6f:75:6e:74:3d:34:7c:63:61:6d:70:61:69:67:6e:5f:69:64:3d:63:61:6d:70:61:69:67:6e:2d:33:66:64:35:36:31:30:33:37:32:7c:75:72:6c:3d:68:74:74:70:73:3a:2f:2f:33:66:64:35:36:31:30:33:37:32:2e:65:78:61:6d:70:6c:65:2e:69:6e:76:61:6c:69:64:2f:34:34:66:63:31:38:65:36:2e:64:61:74:7c:75:73:65:72:5f:61:67:65:6e:74:3d:48:75:6e:74:72:65:73:73:4c:61:62:2f:33:66:64:35:36:31:30:33:37:32:7c:66:69:6c:65:5f:70:61:74:68:3d:43:3a:5c:55:73:65:72:73:5c:50:75:62:6c:69:63:5c:48:75:6e:74:72:65:73:73:4c:61:62:5c:73:74:61:67:65:2d:33:66:64:35:36:31:30:33:37:32:2e:64:61:74:7c:72:65:67:69:73:74:72:79:5f:70:61:74:68:3d:48:4b:43:55:5c:53:6f:66:74:77:61:72:65:5c:48:75:6e:74:72:65:73:73:4c:61:62:5c:44:69:73:70:6f:73:61:62:6c:65:5c:33:66:64:35:36:31:30:33:37:32:7c:6e:65:78:74:5f:73:74:61:67:65:3d:72:65:73:6f:75:72:63:65:2d:73:61:6d:70:6c:65:2e:70:73:31"
Const Codec_6f9f2d08 = "hex_colon|identity|"

Function Load_6f9f2d08()
  Dim parts, result(), materialIndex
  parts = Split(Material_6f9f2d08, ":")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_6f9f2d08 = result
End Function

Function Decode_6f9f2d08(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex)
  Next
  Decode_6f9f2d08 = result
End Function

Function Recover_6f9f2d08()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = (19 * 7) - 133

  storedMaterial = Load_6f9f2d08()

  Do

    recoveredMaterial = Decode_6f9f2d08(storedMaterial)

    Exit Do

  Loop

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_6f9f2d08 = configurationText
End Function

Sub Copy_6f9f2d08(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_6f9f2d08()
  Dim resultText
  Call Copy_6f9f2d08(Recover_6f9f2d08(), resultText)
  Inspect_6f9f2d08 = resultText
End Function
