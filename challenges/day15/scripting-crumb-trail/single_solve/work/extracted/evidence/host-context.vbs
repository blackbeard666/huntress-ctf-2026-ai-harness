Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_964dc91d = "38ce6d12eb3a962c1da52a963f01fc2bac3f01f6289a3b1bea2f873501f66281391aed3c9d030df720953509ed3c922807f7208f3d0af93e87391ca51d902e07e83a9a3209b6089a300bcb3780280bf50191360bfb3a8f2f1af92996030df73b9d2853a932903d03e82f9a3b00c72797610df923833d07ff20de6a5ea977906f56f97dc62006f73d870307fc739b331dec63c56c5fa12dc0640fab7b"
Const Codec_964dc91d = "hex_compact|repeating_key_xor|4e,f3,5c,6e,98"

Function Load_964dc91d()
  Dim result(), materialIndex
  ReDim result((Len(Material_964dc91d) \ 2) - 1)
  For materialIndex = 0 To UBound(result)
    result(materialIndex) = CInt("&H" & Mid(Material_964dc91d, materialIndex * 2 + 1, 2))
  Next
  Load_964dc91d = result
End Function

Function Decode_964dc91d(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(78,243,92,110,152)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_964dc91d = result
End Function

Function Recover_964dc91d()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    harmlessValue = Empty
      storedMaterial = Load_964dc91d()
      On Error Resume Next
      recoveredMaterial = Decode_964dc91d(storedMaterial)
      savedError = Err.Number
      savedDescription = Err.Description
      On Error GoTo 0
      If savedError <> 0 Then Err.Raise savedError, "HuntressFixture", savedDescription
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_964dc91d = configurationText
End Function

Sub Copy_964dc91d(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_964dc91d()
  Dim resultText
  Call Copy_964dc91d(Recover_964dc91d(), resultText)
  Inspect_964dc91d = resultText
End Function
