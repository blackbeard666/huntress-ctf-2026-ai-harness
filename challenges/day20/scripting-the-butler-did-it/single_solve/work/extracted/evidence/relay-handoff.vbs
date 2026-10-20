Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_bce561d6 = "dj0xfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLHdyaXRlX2ZpbGUsZGlzcGF0Y2hfcHJvY2VzcyxoYW5kb2ZmX3NjcmlwdHxhZGFwdGVyPU1TWE1MMi5YTUxIVFRQLjYuMHxzdGFnZV9jb3VudD00fGNhbXBhaWduX2lkPWNhbXBhaWduLTZlOTgyMmIzYmV8dXJsPWh0dHBzOi8vNmU5ODIyYjNiZS5leGFtcGxlLmludmFsaWQvMDVkZDBkNTAuZGF0fHVzZXJfYWdlbnQ9SHVudHJlc3NMYWIvNmU5ODIyYjNiZXxmaWxlX3BhdGg9QzpcVXNlcnNcUHVibGljXEh1bnRyZXNzTGFiXHN0YWdlLTZlOTgyMmIzYmUuZGF0fHJlZ2lzdHJ5X3BhdGg9SEtDVVxTb2Z0d2FyZVxIdW50cmVzc0xhYlxEaXNwb3NhYmxlXDZlOTgyMmIzYmV8bmV4dF9zdGFnZT1sb2NhbC1kaXNwYXRjaC52YnM="
Const Codec_bce561d6 = "base64_chunks|identity|"

Function Base64_bce561d6(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_bce561d6", "Invalid Base64 character"
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
  Base64_bce561d6 = outputBytes
End Function

Function Load_bce561d6()
  Dim partWidth, packedText
  partWidth = (Len(Material_bce561d6) + 3) \ 4
  packedText = Mid(Material_bce561d6, 1, partWidth) & Mid(Material_bce561d6, partWidth + 1, partWidth) & Mid(Material_bce561d6, partWidth * 2 + 1, partWidth) & Mid(Material_bce561d6, partWidth * 3 + 1)
  Load_bce561d6 = Base64_bce561d6(packedText)
End Function

Function Decode_bce561d6(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5)
  Next
  Decode_bce561d6 = result
End Function

Function Recover_bce561d6()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
item4 = Empty
  item1 = Load_bce561d6()
  Select Case 1
    Case 1
      item2 = Decode_bce561d6(item1)
    Case Else
      item2 = Array()
  End Select
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_bce561d6 = item3
End Function

Function Inspect_bce561d6()
  Dim fields
  fields = Split(Recover_bce561d6(), "|")
  Inspect_bce561d6 = Join(fields, "|")
End Function
