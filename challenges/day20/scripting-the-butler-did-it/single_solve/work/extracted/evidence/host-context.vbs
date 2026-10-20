Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_266190d0 = "MzVhNjYyMzQ5Mi10c29oPWRpX3Rzb2h8MzVhNjYyMzQ5Mi1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3wxPXRudW9jX2VnYXRzfHlyYW5vaXRjaUQuZ25pdHBpcmNTPXJldHBhZGF8bm9pdGFydWdpZm5vY19ucnV0ZXIsbm9pdGFydWdpZm5vY19lZG9jZWQ9c3BldHN8MT12"
Const Codec_266190d0 = "base64_chunks|reverse_bytes|"

Function Base64_266190d0(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_266190d0", "Invalid Base64 character"
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
  Base64_266190d0 = outputBytes
End Function

Function Load_266190d0()
  Dim partWidth, packedText
  partWidth = (Len(Material_266190d0) + 3) \ 4
  packedText = Mid(Material_266190d0, 1, partWidth) & Mid(Material_266190d0, partWidth + 1, partWidth) & Mid(Material_266190d0, partWidth * 2 + 1, partWidth) & Mid(Material_266190d0, partWidth * 3 + 1)
  Load_266190d0 = Base64_266190d0(packedText)
End Function

Function Decode_266190d0(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(UBound(storedMaterial) - materialIndex) = storedMaterial(materialIndex)
  Next
  Decode_266190d0 = result
End Function

Function Recover_266190d0()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  ' configuration reconstruction
harmlessValue = (19 * 7) - 133
  storedMaterial = Load_266190d0()
  For decodePass = 0 To 0
    recoveredMaterial = Decode_266190d0(storedMaterial)
  Next
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
' reconstruction complete
  Recover_266190d0 = configurationText
End Function

Sub Copy_266190d0(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_266190d0()
  Dim resultText
  Call Copy_266190d0(Recover_266190d0(), resultText)
  Inspect_266190d0 = resultText
End Function
