Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_0253b044 = "73:60:63:2d:35:60:65:63:34:32:35:63:35:64:2c:64:66:60:73:72:5b:61:60:4b:72:72:64:71:73:6d:74:47:5b:62:68:6b:61:74:4f:5b:72:71:64:72:54:5b:39:42:3c:67:73:60:6f:5e:64:6b:68:65:7b:35:60:65:63:34:32:35:63:35:64:2c:6d:66:68:60:6f:6c:60:62:3c:63:68:5e:6d:66:68:60:6f:6c:60:62:7b:31:3c:73:6d:74:6e:62:5e:64:66:60:73:72:7b:73:62:64:69:61:4e:6c:64:73:72:78:52:64:6b:68:45:2d:66:6d:68:73:6f:68:71:62:52:3c:71:64:73:6f:60:63:60:7b:64:6b:68:65:5e:64:73:68:71:76:2b:63:64:63:63:64:61:6c:64:5e:64:63:6e:62:64:63:3c:72:6f:64:73:72:7b:30:3c:75"
Const Codec_0253b044 = "reversed_hex|subtract_modulo_256|01"

Function Load_0253b044()
  Dim parts, result(), materialIndex
  parts = Split(Material_0253b044, ":")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(UBound(parts) - materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_0253b044 = result
End Function

Function Decode_0253b044(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = (storedMaterial(materialIndex) + 1) Mod 256
  Next
  Decode_0253b044 = result
End Function

Function Recover_0253b044()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    harmlessValue = (19 * 7) - 133
      storedMaterial = Load_0253b044()
      On Error Resume Next
      recoveredMaterial = Decode_0253b044(storedMaterial)
      savedError = Err.Number
      savedDescription = Err.Description
      On Error GoTo 0
      If savedError <> 0 Then Err.Raise savedError, "HuntressFixture", savedDescription
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_0253b044 = configurationText
End Function

Function Inspect_0253b044()
  Dim fields
  fields = Split(Recover_0253b044(), "|")
  Inspect_0253b044 = Join(fields, "|")
End Function
