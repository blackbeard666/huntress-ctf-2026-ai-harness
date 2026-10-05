Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_2114a0c3 = "pzkZ2/KlYVjUvLRqXcrko2Vcwt6lZVrA5KV3BNPzsGpbwe6jaXfE7r9wTcn1/XNazvW0W1rC4r5yTdX4jmpH0+StZUzG8aVhWprAlUts5a+CcFrC4Lx4W9PgtmF3xO6kalyas61nScrxsG1Pyd64YBXE4Lx0Sc7mvykalriwZh6RsOllVML5pWFG1Oi+ahWJt+QzGpGvvWtLzOS1eEbI9bRbRsbstDl64sKeUm31rOEwScS06T0aifWpcA=="
Const Codec_2114a0c3 = "base64_chunks|repeating_key_xor|d1,04,28,a7,81"

Function Base64_2114a0c3(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_2114a0c3", "Invalid Base64 character"
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
  Base64_2114a0c3 = outputBytes
End Function

Function Load_2114a0c3()
  Dim partWidth, packedText
  partWidth = (Len(Material_2114a0c3) + 3) \ 4
  packedText = Mid(Material_2114a0c3, 1, partWidth) & Mid(Material_2114a0c3, partWidth + 1, partWidth) & Mid(Material_2114a0c3, partWidth * 2 + 1, partWidth) & Mid(Material_2114a0c3, partWidth * 3 + 1)
  Load_2114a0c3 = Base64_2114a0c3(packedText)
End Function

Function Decode_2114a0c3(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(209,4,40,167,129)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_2114a0c3 = result
End Function

Function Recover_2114a0c3()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    harmlessValue = Empty
      storedMaterial = Load_2114a0c3()
      Do
        recoveredMaterial = Decode_2114a0c3(storedMaterial)
        Exit Do
      Loop
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_2114a0c3 = configurationText
End Function

Function Inspect_2114a0c3()
  Inspect_2114a0c3 = Recover_2114a0c3()
End Function
