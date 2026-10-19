Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_00e1aec7 = "c2-ce-c2-98-81-81-81-80-d4-82-d4-d4-9b-e4-f3-e0-f9-f5-f3-e4-8b-d3-db-d7-d8-e9-d3-c2-d9-d8-ca-d2-d3-dd-d5-d9-da-98-d5-8e-82-d5-d7-98-8b-d8-d9-df-c5-d8-d3-c2-ce-d3-ca-8f-d4-d3-83-82-d2-d2-8f-85-d0-9b-d8-d1-df-d7-c6-db-d7-d5-8b-d2-df-e9-d8-d1-df-d7-c6-db-d7-d5-ca-84-8b-c2-d8-c3-d9-d5-e9-d3-d1-d7-c2-c5-ca-db-d7-d3-c4-c2-e5-98-f4-f2-f9-f2-f7-8b-c4-d3-c2-c6-d7-d2-d7-ca-d3-c2-d9-d8-e9-cf-c4-d3-c0-d9-d5-d3-c4-e9-d3-c2-df-c4-c1-9a-c2-d8-d3-c2-d8-d9-d5-e9-db-c4-d9-d0-c5-d8-d7-c4-c2-9a-c5-c2-d3-d1-c4-d7-c2-e9-d3-c2-d7-c4-d3-db-c3-d8-d3-8b-c5-c6-d3-c2-c5-ca-87-8b-c0"
Const Codec_00e1aec7 = "hex_dash|reverse_then_xor|b6"

Function Load_00e1aec7()
  Dim parts, result(), materialIndex
  parts = Split(Material_00e1aec7, "-")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_00e1aec7 = result
End Function

Function Decode_00e1aec7(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(UBound(storedMaterial) - materialIndex) = storedMaterial(materialIndex) Xor 182
  Next
  Decode_00e1aec7 = result
End Function

Function Recover_00e1aec7()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = UBound(Array(3, 5, 8, 13))
  storedMaterial = Load_00e1aec7()
  On Error Resume Next
  recoveredMaterial = Decode_00e1aec7(storedMaterial)
  savedError = Err.Number
  savedDescription = Err.Description
  On Error GoTo 0
  If savedError <> 0 Then Err.Raise savedError, "HuntressFixture", savedDescription
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
  Recover_00e1aec7 = configurationText
End Function

Sub Copy_00e1aec7(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_00e1aec7()
  Dim resultText
  Call Copy_00e1aec7(Recover_00e1aec7(), resultText)
  Inspect_00e1aec7 = resultText
End Function
