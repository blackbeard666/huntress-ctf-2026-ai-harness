Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_15f5944d = "116,97,100,46,57,100,99,48,101,99,55,98,48,101,45,101,103,97,116,115,92,98,97,76,115,115,101,114,116,110,117,72,92,99,105,108,98,117,80,92,115,114,101,115,85,92,58,67,61,104,116,97,112,95,101,108,105,102,124,57,100,99,48,101,99,55,98,48,101,47,98,97,76,115,115,101,114,116,110,117,72,61,116,110,101,103,97,95,114,101,115,117,124,116,97,100,46,98,55,55,48,52,99,55,53,47,100,105,108,97,118,110,105,46,101,108,112,109,97,120,101,46,57,100,99,48,101,99,55,98,48,101,47,47,58,115,112,116,116,104,61,108,114,117,124,57,100,99,48,101,99,55,98,48,101,45,110,103,105,97,112,109,97,99,61,100,105,95,110,103,105,97,112,109,97,99,124,50,61,116,110,117,111,99,95,101,103,97,116,115,124,49,46,53,46,116,115,101,117,113,101,82,112,116,116,72,110,105,87,46,112,116,116,72,110,105,87,61,114,101,116,112,97,100,97,124,101,108,105,102,95,101,116,105,114,119,44,101,116,111,109,101,114,95,101,114,105,117,113,99,97,61,115,112,101,116,115,124,49,61,118"
Const Codec_15f5944d = "decimal_comma|reverse_bytes|"

Function Load_15f5944d()
  Dim parts, result(), materialIndex
  parts = Split(Material_15f5944d, ",")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_15f5944d = result
End Function

Function Decode_15f5944d(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(UBound(storedMaterial) - materialIndex) = storedMaterial(materialIndex)
  Next
  Decode_15f5944d = result
End Function

Function Recover_15f5944d()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = Join(Array("north", "south"), ":")
  storedMaterial = Load_15f5944d()
  On Error Resume Next
  recoveredMaterial = Decode_15f5944d(storedMaterial)
  savedError = Err.Number
  savedDescription = Err.Description
  On Error GoTo 0
  If savedError <> 0 Then Err.Raise savedError, "HuntressFixture", savedDescription
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
  Recover_15f5944d = configurationText
End Function

Function Inspect_15f5944d()
  Inspect_15f5944d = Recover_15f5944d()
End Function
