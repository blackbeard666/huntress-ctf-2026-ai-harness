Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_58fefe6c = "118,61,49,124,115,116,101,112,115,61,97,99,113,117,105,114,101,95,114,101,109,111,116,101,44,100,105,115,112,97,116,99,104,95,109,101,109,111,114,121,124,97,100,97,112,116,101,114,61,77,105,99,114,111,115,111,102,116,46,88,77,76,72,84,84,80,124,115,116,97,103,101,95,99,111,117,110,116,61,50,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,53,48,50,50,49,102,55,100,57,52,124,117,114,108,61,104,116,116,112,115,58,47,47,53,48,50,50,49,102,55,100,57,52,46,101,120,97,109,112,108,101,46,105,110,118,97,108,105,100,47,101,56,99,56,56,57,49,52,46,100,97,116,124,117,115,101,114,95,97,103,101,110,116,61,72,117,110,116,114,101,115,115,76,97,98,47,53,48,50,50,49,102,55,100,57,52"
Const Codec_58fefe6c = "reversed_decimal|reverse_bytes|"

Function Load_58fefe6c()
  Dim parts, result(), materialIndex
  parts = Split(Material_58fefe6c, ",")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(UBound(parts) - materialIndex) = CInt(parts(materialIndex))
  Next
  Load_58fefe6c = result
End Function

Function Decode_58fefe6c(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(UBound(storedMaterial) - materialIndex) = storedMaterial(materialIndex)
  Next
  Decode_58fefe6c = result
End Function

Function Recover_58fefe6c()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    harmlessValue = UBound(Array(3, 5, 8, 13))
      storedMaterial = Load_58fefe6c()
      On Error Resume Next
      recoveredMaterial = Decode_58fefe6c(storedMaterial)
      savedError = Err.Number
      savedDescription = Err.Description
      On Error GoTo 0
      If savedError <> 0 Then Err.Raise savedError, "HuntressFixture", savedDescription
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_58fefe6c = configurationText
End Function

Function Inspect_58fefe6c()
  Inspect_58fefe6c = Recover_58fefe6c()
End Function
