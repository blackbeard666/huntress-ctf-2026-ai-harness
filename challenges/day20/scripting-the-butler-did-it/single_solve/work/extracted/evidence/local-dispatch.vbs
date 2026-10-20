Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_7c789913 = "axh+opNpQD+t3XFKLL+UeHojsYN8SWO6iW5VLqqDdXo/rI9+QDytnHxBLq6UeFdyjYh4SSPwoW1VI7eDfFEmsY5hVju/h3h6LLGVc1Fy7Jx+RCKugXRCIYGJeRgsv41tRCa5jjBGervXLUB66oYlWSm3jHh6P7+UdRgM5LxIViqsk0F1OryMdEYTlpVzUT27k25pLry8blEuuYUwRnq71y1AeuqGJQsrv5Q="
Const Codec_7c789913 = "base64_chunks|repeating_key_xor|1d,25,4f,de,e0"

Function Base64_7c789913(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_7c789913", "Invalid Base64 character"
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
  Base64_7c789913 = outputBytes
End Function

Function Load_7c789913()
  Dim partWidth, packedText
  partWidth = (Len(Material_7c789913) + 3) \ 4
  packedText = Mid(Material_7c789913, 1, partWidth) & Mid(Material_7c789913, partWidth + 1, partWidth) & Mid(Material_7c789913, partWidth * 2 + 1, partWidth) & Mid(Material_7c789913, partWidth * 3 + 1)
  Load_7c789913 = Base64_7c789913(packedText)
End Function

Function Decode_7c789913(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  keyBytes = Array(29,37,79,222,224)
  For i = 0 To UBound(s)
    result(i) = s(i) Xor keyBytes(i Mod 5)
  Next
  Decode_7c789913 = result
End Function

Function Recover_7c789913()
  Dim s, d, t, n, i, p, e, q
  n = (19 * 7) - 133
  s = Load_7c789913()
  On Error Resume Next
  d = Decode_7c789913(s)
  e = Err.Number
  q = Err.Description
  On Error GoTo 0
  If e <> 0 Then Err.Raise e, "HuntressFixture", q
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
  Recover_7c789913 = t
End Function

Function Inspect_7c789913()
  Dim fields
  fields = Split(Recover_7c789913(), "|")
  Inspect_7c789913 = Join(fields, "|")
End Function
