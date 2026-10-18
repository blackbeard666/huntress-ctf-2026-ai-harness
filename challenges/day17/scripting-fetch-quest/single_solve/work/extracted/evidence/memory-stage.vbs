Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_aa73e9b6 = "dj0xfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLGRpc3BhdGNoX21lbW9yeXxhZGFwdGVyPU1TWE1MMi5YTUxIVFRQLjYuMHxzdGFnZV9jb3VudD0yfGNhbXBhaWduX2lkPWNhbXBhaWduLWNkYTlkYjU4ZjB8dXJsPWh0dHBzOi8vY2RhOWRiNThmMC5leGFtcGxlLmludmFsaWQvYjI3M2IzYzguZGF0fHVzZXJfYWdlbnQ9SHVudHJlc3NMYWIvY2RhOWRiNThmMA=="
Const Codec_aa73e9b6 = "base64_literal|identity|"

Function Base64_aa73e9b6(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_aa73e9b6", "Invalid Base64 character"
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
  Base64_aa73e9b6 = outputBytes
End Function

Function Load_aa73e9b6()
  Load_aa73e9b6 = Base64_aa73e9b6(Material_aa73e9b6)
End Function

Function Decode_aa73e9b6(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598)
  Next
  Decode_aa73e9b6 = result
End Function

Function Recover_aa73e9b6()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = UBound(Array(3, 5, 8, 13))
  v_a19c = Load_aa73e9b6()
  v_b27e = Decode_aa73e9b6(v_a19c)
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_aa73e9b6 = v_c304
End Function

Function Inspect_aa73e9b6()
  Dim fields
  fields = Split(Recover_aa73e9b6(), "|")
  Inspect_aa73e9b6 = Join(fields, "|")
End Function
