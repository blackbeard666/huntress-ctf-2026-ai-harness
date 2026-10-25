Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_1fca969d = "x9LXndKL0YGFgdaG0Nae1tTSx8Dv0dL/wMDWwcfdxvvv0Nrf0cbj78DB1sDm74nwjtvH0sPs1t/a1c/Si9GBhYHWhtDWnt3U2tLD3tLQjtfa7N3U2tLD3tLQz4GOx93G3NDs1tTSx8DP39/W2+Cdx8PawdDg5I7B1sfD0tfSz8DA1tDcwcPs29DH0sPA2tef39LQ3N/s1sfS0NzfjsDD1sfAz4KOxQ=="
Const Codec_1fca969d = "base64_chunks|reverse_then_xor|b3"

Function Base64_1fca969d(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_1fca969d", "Invalid Base64 character"
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
  Base64_1fca969d = outputBytes
End Function

Function Load_1fca969d()
  Dim partWidth, packedText
  partWidth = (Len(Material_1fca969d) + 3) \ 4
  packedText = Mid(Material_1fca969d, 1, partWidth) & Mid(Material_1fca969d, partWidth + 1, partWidth) & Mid(Material_1fca969d, partWidth * 2 + 1, partWidth) & Mid(Material_1fca969d, partWidth * 3 + 1)
  Load_1fca969d = Base64_1fca969d(packedText)
End Function

Function Decode_1fca969d(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5) Xor 179
  Next
  Decode_1fca969d = result
End Function

Function Recover_1fca969d()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If (2 > 1) Then item4 = "left" Else item4 = "right"

  item1 = Load_1fca969d()

  On Error Resume Next

  item2 = Decode_1fca969d(item1)

  item7 = Err.Number

  item8 = Err.Description

  On Error GoTo 0

  If item7 <> 0 Then Err.Raise item7, "HuntressFixture", item8

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_1fca969d = item3
End Function

Function Inspect_1fca969d()
  Inspect_1fca969d = Recover_1fca969d()
End Function
