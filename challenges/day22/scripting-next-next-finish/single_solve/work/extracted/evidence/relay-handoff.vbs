Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_2ca7aaf8 = "YygkaWZhcGVmKHR2ZGB8Z3BKZ3B4emFwOWJnfGFwSnN8eXA5cXxmZXRhdn1KZWd6dnBmZjl9dHtxenNzSmZ2Z3xlYWl0cXRlYXBnKFhGTVhZJztNWFldQUFFOyM7JWlmYXRycEp2emB7YSghaXZ0eGV0fHJ7SnxxKHZ0eGV0fHJ7OCUkdyxwJSwiJCZpYGd5KH1hYWVmLzo6JSR3LHAlLCIkJjtwbXR4ZXlwO3x7Y3R5fHE6LHNzd3N2c3A7cXRhaWBmcGdKdHJwe2EoXWB7YWdwZmZZdHc6JSR3LHAlLCIkJmlzfHlwSmV0YX0oVi9JQGZwZ2ZJRWB3eXx2SV1ge2FncGZmWXR3SWZhdHJwOCUkdyxwJSwiJCY7cXRhaWdwcnxmYWdsSmV0YX0oXV5WQElGenNhYnRncEldYHthZ3BmZll0d0lRfGZlemZ0d3lwSSUkdyxwJSwiJCZpe3BtYUpmYXRycCh5enZ0eThxfGZldGF2fTtjd2Y="
Const Codec_2ca7aaf8 = "base64_literal|single_byte_xor|15"

Function Base64_2ca7aaf8(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_2ca7aaf8", "Invalid Base64 character"
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
  Base64_2ca7aaf8 = outputBytes
End Function

Function Load_2ca7aaf8()
  Load_2ca7aaf8 = Base64_2ca7aaf8(Material_2ca7aaf8)
End Function

Function Decode_2ca7aaf8(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor 21
  Next
  Decode_2ca7aaf8 = result
End Function

Function Recover_2ca7aaf8()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = Join(Array("north", "south"), ":")
  v_a19c = Load_2ca7aaf8()
  On Error Resume Next
  v_b27e = Decode_2ca7aaf8(v_a19c)
  v_a702 = Err.Number
  v_b803 = Err.Description
  On Error GoTo 0
  If v_a702 <> 0 Then Err.Raise v_a702, "HuntressFixture", v_b803
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_2ca7aaf8 = v_c304
End Function

Function Inspect_2ca7aaf8()
  Inspect_2ca7aaf8 = Recover_2ca7aaf8()
End Function
