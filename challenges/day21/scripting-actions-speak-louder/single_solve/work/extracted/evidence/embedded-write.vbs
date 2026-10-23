Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_e49e05b7 = "azImcWhpWmVoMllaWGRZWlRaYldaWVlaWSFsZ15pWlRbXmFacVZZVmVpWmcyNjlEOTcjSGlnWlZicWhpVlxaVFhkamNpMidxWFZiZVZeXGNUXlkyWFZiZVZeXGMiKywmVlZaKywtV3FbXmFaVGVWaV0yOC9RSmhaZ2hRRWpXYV5YUT1qY2lnWmhoQVZXUWhpVlxaIissJlZWWissLVcjWVZp"
Const Codec_e49e05b7 = "base64_chunks|subtract_modulo_256|0b"

Function Base64_e49e05b7(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_e49e05b7", "Invalid Base64 character"
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
  Base64_e49e05b7 = outputBytes
End Function

Function Load_e49e05b7()
  Dim partWidth, packedText
  partWidth = (Len(Material_e49e05b7) + 3) \ 4
  packedText = Mid(Material_e49e05b7, 1, partWidth) & Mid(Material_e49e05b7, partWidth + 1, partWidth) & Mid(Material_e49e05b7, partWidth * 2 + 1, partWidth) & Mid(Material_e49e05b7, partWidth * 3 + 1)
  Load_e49e05b7 = Base64_e49e05b7(packedText)
End Function

Function Decode_e49e05b7(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = (storedMaterial(materialIndex) + 11) Mod 256
  Next
  Decode_e49e05b7 = result
End Function

Function Recover_e49e05b7()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    harmlessValue = Empty
      storedMaterial = Load_e49e05b7()
      Do
        recoveredMaterial = Decode_e49e05b7(storedMaterial)
        Exit Do
      Loop
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_e49e05b7 = configurationText
End Function

Sub Copy_e49e05b7(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_e49e05b7()
  Dim resultText
  Call Copy_e49e05b7(Recover_e49e05b7(), resultText)
  Inspect_e49e05b7 = resultText
End Function
