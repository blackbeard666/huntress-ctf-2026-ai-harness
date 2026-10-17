Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_f735ee59 = "QExAGgcGDQcNBwEHGWZxYnt3cWYJUVlVWmtRQFtaSFBRX1dbWBoEVlBSUBoJWltdR1pRQExRSFcEUFZSBQQBVVUZWlNdVURZVVcJUF1rWlNdVURZVVdIBglAWkFbV2tRU1VAR0hAV1FeVntZUUBHTWdRWF1yGlNaXUBEXUZXZwlGUUBEVVBVSFFAW1prTUZRQltXUUZrUUBdRkMYQFpRQFpbV2tZRltSR1pVRkAYR0BRU0ZVQGtRQFVGUVlBWlEJR0RRQEdIBQlC"
Const Codec_f735ee59 = "base64_chunks|reverse_then_xor|34"

Function Base64_f735ee59(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_f735ee59", "Invalid Base64 character"
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
  Base64_f735ee59 = outputBytes
End Function

Function Load_f735ee59()
  Dim partWidth, packedText
  partWidth = (Len(Material_f735ee59) + 3) \ 4
  packedText = Mid(Material_f735ee59, 1, partWidth) & Mid(Material_f735ee59, partWidth + 1, partWidth) & Mid(Material_f735ee59, partWidth * 2 + 1, partWidth) & Mid(Material_f735ee59, partWidth * 3 + 1)
  Load_f735ee59 = Base64_f735ee59(packedText)
End Function

Function Decode_f735ee59(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5) Xor 52
  Next
  Decode_f735ee59 = result
End Function

Function Recover_f735ee59()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = Empty
  item1 = Load_f735ee59()
  On Error Resume Next
  item2 = Decode_f735ee59(item1)
  item7 = Err.Number
  item8 = Err.Description
  On Error GoTo 0
  If item7 <> 0 Then Err.Raise item7, "HuntressFixture", item8
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_f735ee59 = item3
End Function

Function Inspect_f735ee59()
  Inspect_f735ee59 = Recover_f735ee59()
End Function
