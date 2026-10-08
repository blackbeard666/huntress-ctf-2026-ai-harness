Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_678789c5 = "dGFkLmY5YmQ0MzQxMjYtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnxmOWJkNDM0MTI2L2JhTHNzZXJ0bnVIPXRuZWdhX3Jlc3V8dGFkLjRhNGMzYjFkL2RpbGF2bmkuZWxwbWF4ZS5mOWJkNDM0MTI2Ly86c3B0dGg9bHJ1fGY5YmQ0MzQxMjYtbmdpYXBtYWM9ZGlfbmdpYXBtYWN8Mj10bnVvY19lZ2F0c3wxLjUudHNldXFlUnB0dEhuaVcucHR0SG5pVz1yZXRwYWRhfGVsaWZfZXRpcncsZXRvbWVyX2VyaXVxY2E9c3BldHN8MT12"
Const Codec_678789c5 = "base64_literal|reverse_bytes|"

Function Base64_678789c5(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_678789c5", "Invalid Base64 character"
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
  Base64_678789c5 = outputBytes
End Function

Function Load_678789c5()
  Load_678789c5 = Base64_678789c5(Material_678789c5)
End Function

Function Decode_678789c5(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(UBound(storedMaterial) - materialIndex) = storedMaterial(materialIndex)
  Next
  Decode_678789c5 = result
End Function

Function Recover_678789c5()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = UBound(Array(3, 5, 8, 13))
  storedMaterial = Load_678789c5()
  Do
    recoveredMaterial = Decode_678789c5(storedMaterial)
    Exit Do
  Loop
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
  Recover_678789c5 = configurationText
End Function

Sub Copy_678789c5(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_678789c5()
  Dim resultText
  Call Copy_678789c5(Recover_678789c5(), resultText)
  Inspect_678789c5 = resultText
End Function
