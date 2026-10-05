Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_146d129b = "dTwwe3JzZG9yPGNkYm5jZF5ibm1laGZ0cWBzaG5tK3Fkc3RxbV5ibm1laGZ0cWBzaG5te2BjYG9zZHE8UmJxaG9zaG1mLUVoa2RSeHJzZGxOYWlkYnN7cnNgZmReYm50bXM8MHtiYGxvYGhmbV5oYzxiYGxvYGhmbSw3MGEvN2U3MDE4e2ducnNeaGM8Z25ycyw3MGEvN2U3MDE4"
Const Codec_146d129b = "base64_chunks|subtract_modulo_256|01"

Function Base64_146d129b(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_146d129b", "Invalid Base64 character"
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
  Base64_146d129b = outputBytes
End Function

Function Load_146d129b()
  Dim partWidth, packedText
  partWidth = (Len(Material_146d129b) + 3) \ 4
  packedText = Mid(Material_146d129b, 1, partWidth) & Mid(Material_146d129b, partWidth + 1, partWidth) & Mid(Material_146d129b, partWidth * 2 + 1, partWidth) & Mid(Material_146d129b, partWidth * 3 + 1)
  Load_146d129b = Base64_146d129b(packedText)
End Function

Function Decode_146d129b(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = (item1(item5) + 1) Mod 256
  Next
  Decode_146d129b = result
End Function

Function Recover_146d129b()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = Empty
  item1 = Load_146d129b()
  On Error Resume Next
  item2 = Decode_146d129b(item1)
  item7 = Err.Number
  item8 = Err.Description
  On Error GoTo 0
  If item7 <> 0 Then Err.Raise item7, "HuntressFixture", item8
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_146d129b = item3
End Function

Sub Copy_146d129b(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_146d129b()
  Dim resultText
  Call Copy_146d129b(Recover_146d129b(), resultText)
  Inspect_146d129b = resultText
End Function
