Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_16f1d490 = "vvX5tLu8rbi79aytq6esrZetpaqtrKytrOS/uqG8rZeuoaSttKmsqbi8rbr1m6u6obi8oaav5o6hpK2bsbu8raWHqqKtq7y0u7ypr62Xq6e9prz1+rSrqaW4qaGvppehrPWrqaW4qaGvpuX48fnw+fGt+Kn4tK6hpK2XuKm8oPWL8pSdu626u5SYvaqkoauUgL2mvLqtu7uEqaqUu7ypr63l+PH58Pnxrfip+Oasqbw="
Const Codec_16f1d490 = "base64_literal|single_byte_xor|c8"

Function Base64_16f1d490(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_16f1d490", "Invalid Base64 character"
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
  Base64_16f1d490 = outputBytes
End Function

Function Load_16f1d490()
  Load_16f1d490 = Base64_16f1d490(Material_16f1d490)
End Function

Function Decode_16f1d490(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor 200
  Next
  Decode_16f1d490 = result
End Function

Function Recover_16f1d490()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = (19 * 7) - 133
  item1 = Load_16f1d490()
  Do
    item2 = Decode_16f1d490(item1)
    Exit Do
  Loop
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_16f1d490 = item3
End Function

Function Inspect_16f1d490()
  Inspect_16f1d490 = Recover_16f1d490()
End Function
