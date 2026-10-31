Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_4e7840bc = "Nzs3bXJzJXohIXJ1bhEGFQwABhF+Ji4iLRwmNywtPycmKCAsL20le3IncW1+LSwqMC0mNzsmPyFxIHt0JiV1IHtuLSQqIjMuIiB+JyocLSQqIjMuIiA/cX43LTYsIBwmJCI3MD8uIiYxNxBtAQcMBwJ+MSY3MyInIj8mNywtHDoxJjUsICYxHCY3KjE0bzctJjctLCAcLjEsJTAtIjE3bzA3JiQxIjccJjciMSYuNi0mfjAzJjcwP3J+NQ=="
Const Codec_4e7840bc = "base64_literal|reverse_then_xor|43"

Function Base64_4e7840bc(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_4e7840bc", "Invalid Base64 character"
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
  Base64_4e7840bc = outputBytes
End Function

Function Load_4e7840bc()
  Load_4e7840bc = Base64_4e7840bc(Material_4e7840bc)
End Function

Function Decode_4e7840bc(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(UBound(s) - i) = s(i) Xor 67
  Next
  Decode_4e7840bc = result
End Function

Function Recover_4e7840bc()
  Dim s, d, t, n, i, p, e, q
  n = LCase(UCase("Host"))

  s = Load_4e7840bc()

  d = Decode_4e7840bc(s)

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_4e7840bc = t
End Function

Function Inspect_4e7840bc()
  Dim fields
  fields = Split(Recover_4e7840bc(), "|")
  Inspect_4e7840bc = Join(fields, "|")
End Function
