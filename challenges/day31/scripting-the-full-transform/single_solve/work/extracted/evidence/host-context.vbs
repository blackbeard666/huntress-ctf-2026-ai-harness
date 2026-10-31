Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_50fd77a9 = "OTcyMzkzODJhZC10c29oPWRpX3Rzb2h8OTcyMzkzODJhZC1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3wxPXRudW9jX2VnYXRzfHRjZWpiT21ldHN5U2VsaUYuZ25pdHBpcmNTPXJldHBhZGF8bm9pdGFydWdpZm5vY19ucnV0ZXIsbm9pdGFydWdpZm5vY19lZG9jZWQ9c3BldHN8MT12"
Const Codec_50fd77a9 = "base64_chunks|reverse_bytes|"

Function Base64_50fd77a9(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_50fd77a9", "Invalid Base64 character"
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
  Base64_50fd77a9 = outputBytes
End Function

Function Load_50fd77a9()
  Dim partWidth, packedText
  partWidth = (Len(Material_50fd77a9) + 3) \ 4
  packedText = Mid(Material_50fd77a9, 1, partWidth) & Mid(Material_50fd77a9, partWidth + 1, partWidth) & Mid(Material_50fd77a9, partWidth * 2 + 1, partWidth) & Mid(Material_50fd77a9, partWidth * 3 + 1)
  Load_50fd77a9 = Base64_50fd77a9(packedText)
End Function

Function Decode_50fd77a9(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(UBound(storedMaterial) - materialIndex) = storedMaterial(materialIndex)
  Next
  Decode_50fd77a9 = result
End Function

Function Recover_50fd77a9()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = (19 * 7) - 133
  storedMaterial = Load_50fd77a9()
  Do
    recoveredMaterial = Decode_50fd77a9(storedMaterial)
    Exit Do
  Loop
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
  Recover_50fd77a9 = configurationText
End Function

Function Inspect_50fd77a9()
  Inspect_50fd77a9 = Recover_50fd77a9()
End Function
