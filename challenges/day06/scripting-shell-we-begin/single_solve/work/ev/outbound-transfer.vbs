Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_60d8b1b1 = "76:3d:31:7c:73:74:65:70:73:3d:6c:6f:63:61:74:65:5f:6c:6f:63:61:6c:2c:70:72:65:70:61:72:65:5f:74:72:61:6e:73:66:65:72:2c:75:70:6c:6f:61:64:5f:72:65:6d:6f:74:65:7c:61:64:61:70:74:65:72:3d:4d:53:58:4d:4c:32:2e:53:65:72:76:65:72:58:4d:4c:48:54:54:50:2e:36:2e:30:7c:73:74:61:67:65:5f:63:6f:75:6e:74:3d:32:7c:63:61:6d:70:61:69:67:6e:5f:69:64:3d:63:61:6d:70:61:69:67:6e:2d:66:39:65:37:61:62:64:30:30:63:7c:75:72:6c:3d:68:74:74:70:73:3a:2f:2f:66:39:65:37:61:62:64:30:30:63:2e:65:78:61:6d:70:6c:65:2e:69:6e:76:61:6c:69:64:2f:65:35:64:64:35:37:37:63:2e:64:61:74:7c:75:73:65:72:5f:61:67:65:6e:74:3d:48:75:6e:74:72:65:73:73:4c:61:62:2f:66:39:65:37:61:62:64:30:30:63:7c:66:69:6c:65:5f:70:61:74:68:3d:43:3a:5c:55:73:65:72:73:5c:50:75:62:6c:69:63:5c:48:75:6e:74:72:65:73:73:4c:61:62:5c:73:74:61:67:65:2d:66:39:65:37:61:62:64:30:30:63:2e:64:61:74:7c:75:70:6c:6f:61:64:5f:75:72:6c:3d:68:74:74:70:73:3a:2f:2f:66:39:65:37:61:62:64:30:30:63:2e:65:78:61:6d:70:6c:65:2e:69:6e:76:61:6c:69:64:2f:75:70:6c:6f:61:64:2f:35:36:37:32:66:63:32:30"
Const Codec_60d8b1b1 = "hex_colon|identity|"

Function Load_60d8b1b1()
  Dim parts, result(), materialIndex
  parts = Split(Material_60d8b1b1, ":")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_60d8b1b1 = result
End Function

Function Decode_60d8b1b1(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex)
  Next
  Decode_60d8b1b1 = result
End Function

Function Recover_60d8b1b1()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = Join(Array("north", "south"), ":")

  storedMaterial = Load_60d8b1b1()

  On Error Resume Next

  recoveredMaterial = Decode_60d8b1b1(storedMaterial)

  savedError = Err.Number

  savedDescription = Err.Description

  On Error GoTo 0

  If savedError <> 0 Then Err.Raise savedError, "HuntressFixture", savedDescription

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_60d8b1b1 = configurationText
End Function

Function Inspect_60d8b1b1()
  Inspect_60d8b1b1 = Recover_60d8b1b1()
End Function
