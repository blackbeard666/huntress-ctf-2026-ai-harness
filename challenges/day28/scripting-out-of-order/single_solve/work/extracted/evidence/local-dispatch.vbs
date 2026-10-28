Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_7055a57f = "dj0xfHN0ZXBzPWxvY2F0ZV9sb2NhbCxkaXNwYXRjaF9wcm9jZXNzfGFkYXB0ZXI9V1NjcmlwdC5TaGVsbHxzdGFnZV9jb3VudD0yfGNhbXBhaWduX2lkPWNhbXBhaWduLWU5MjY0OWMwMzl8ZmlsZV9wYXRoPUM6XFVzZXJzXFB1YmxpY1xIdW50cmVzc0xhYlxzdGFnZS1lOTI2NDljMDM5LmRhdA=="
Const Codec_7055a57f = "base64_literal|identity|"

Function Base64_7055a57f(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_7055a57f", "Invalid Base64 character"
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
  Base64_7055a57f = outputBytes
End Function

Function Load_7055a57f()
  Load_7055a57f = Base64_7055a57f(Material_7055a57f)
End Function

Function Decode_7055a57f(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex)
  Next
  Decode_7055a57f = result
End Function

Function Recover_7055a57f()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"
      storedMaterial = Load_7055a57f()
      Do
        recoveredMaterial = Decode_7055a57f(storedMaterial)
        Exit Do
      Loop
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_7055a57f = configurationText
End Function

Function Inspect_7055a57f()
  Dim fields
  fields = Split(Recover_7055a57f(), "|")
  Inspect_7055a57f = Join(fields, "|")
End Function
