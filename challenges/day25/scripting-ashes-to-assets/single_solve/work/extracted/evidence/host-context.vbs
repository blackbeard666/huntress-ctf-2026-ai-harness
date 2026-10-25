Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_b4e8eb85 = "dj0xfHN0ZXBzPWRlY29kZV9jb25maWd1cmF0aW9uLHJldHVybl9jb25maWd1cmF0aW9ufGFkYXB0ZXI9U2NyaXB0aW5nLkZpbGVTeXN0ZW1PYmplY3R8c3RhZ2VfY291bnQ9MXxjYW1wYWlnbl9pZD1jYW1wYWlnbi04YWM2NDM0NjY3fGhvc3RfaWQ9aG9zdC04YWM2NDM0NjY3"
Const Codec_b4e8eb85 = "base64_literal|identity|"

Function Base64_b4e8eb85(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_b4e8eb85", "Invalid Base64 character"
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
  Base64_b4e8eb85 = outputBytes
End Function

Function Load_b4e8eb85()
  Load_b4e8eb85 = Base64_b4e8eb85(Material_b4e8eb85)
End Function

Function Decode_b4e8eb85(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = s(i)
  Next
  Decode_b4e8eb85 = result
End Function

Function Recover_b4e8eb85()
  Dim s, d, t, n, i, p, e, q
  If True Then
    If (2 > 1) Then n = "left" Else n = "right"
      s = Load_b4e8eb85()
      Do
        d = Decode_b4e8eb85(s)
        Exit Do
      Loop
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_b4e8eb85 = t
End Function

Function Inspect_b4e8eb85()
  Inspect_b4e8eb85 = Recover_b4e8eb85()
End Function
