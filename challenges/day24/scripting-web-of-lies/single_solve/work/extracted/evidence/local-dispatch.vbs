Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_744c0511 = "dj0xfHN0ZXBzPWxvY2F0ZV9sb2NhbCxkaXNwYXRjaF9wcm9jZXNzfGFkYXB0ZXI9U2hlbGwuQXBwbGljYXRpb258c3RhZ2VfY291bnQ9MnxjYW1wYWlnbl9pZD1jYW1wYWlnbi1kOWE1NjdmNTBmfGZpbGVfcGF0aD1DOlxVc2Vyc1xQdWJsaWNcSHVudHJlc3NMYWJcc3RhZ2UtZDlhNTY3ZjUwZi5kYXQ="
Const Codec_744c0511 = "base64_chunks|identity|"

Function Base64_744c0511(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_744c0511", "Invalid Base64 character"
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
  Base64_744c0511 = outputBytes
End Function

Function Load_744c0511()
  Dim partWidth, packedText
  partWidth = (Len(Material_744c0511) + 3) \ 4
  packedText = Mid(Material_744c0511, 1, partWidth) & Mid(Material_744c0511, partWidth + 1, partWidth) & Mid(Material_744c0511, partWidth * 2 + 1, partWidth) & Mid(Material_744c0511, partWidth * 3 + 1)
  Load_744c0511 = Base64_744c0511(packedText)
End Function

Function Decode_744c0511(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5)
  Next
  Decode_744c0511 = result
End Function

Function Recover_744c0511()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = (19 * 7) - 133
  item1 = Load_744c0511()
  Do
    item2 = Decode_744c0511(item1)
    Exit Do
  Loop
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_744c0511 = item3
End Function

Sub Copy_744c0511(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_744c0511()
  Dim resultText
  Call Copy_744c0511(Recover_744c0511(), resultText)
  Inspect_744c0511 = resultText
End Function
