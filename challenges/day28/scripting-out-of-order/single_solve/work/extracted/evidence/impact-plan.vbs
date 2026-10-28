Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_b224699d = "dj0xfHN0ZXBzPWVudW1lcmF0ZV90YXJnZXRzLHRyYW5zZm9ybV9jb250ZW50LHdyaXRlX3JlY292ZXJ5X25vdGV8YWRhcHRlcj1TY3JpcHRpbmcuRmlsZVN5c3RlbU9iamVjdHxzdGFnZV9jb3VudD0yfGNhbXBhaWduX2lkPWNhbXBhaWduLTY1ZjdhMWEwYmZ8ZXh0ZW5zaW9uPS42NDgzNi5sb2NrZWR8bm90ZV9uYW1lPVJFQ09WRVItMDQwNzdhNGUudHh0"
Const Codec_b224699d = "base64_chunks|identity|"

Function Base64_b224699d(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_b224699d", "Invalid Base64 character"
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
  Base64_b224699d = outputBytes
End Function

Function Load_b224699d()
  Dim partWidth, packedText
  partWidth = (Len(Material_b224699d) + 3) \ 4
  packedText = Mid(Material_b224699d, 1, partWidth) & Mid(Material_b224699d, partWidth + 1, partWidth) & Mid(Material_b224699d, partWidth * 2 + 1, partWidth) & Mid(Material_b224699d, partWidth * 3 + 1)
  Load_b224699d = Base64_b224699d(packedText)
End Function

Function Decode_b224699d(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598)
  Next
  Decode_b224699d = result
End Function

Function Recover_b224699d()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = Join(Array("north", "south"), ":")
  v_a19c = Load_b224699d()
  v_b27e = Decode_b224699d(v_a19c)
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_b224699d = v_c304
End Function

Sub Copy_b224699d(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_b224699d()
  Dim resultText
  Call Copy_b224699d(Recover_b224699d(), resultText)
  Inspect_b224699d = resultText
End Function
