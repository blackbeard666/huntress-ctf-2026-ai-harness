Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_da643dcd = "mdLek5ybip+c0ouKjICLirCMgIGJhoianY6bhoCBw52Km5qdgbCMgIGJhoianY6bhoCBk46Ljp+bip3SvIydhp+bhoGIwauGjJuGgIGOnZaTnJuOiIqwjICagZvS3pOMjoKfjoaIgbCGi9KMjoKfjoaIgcLa1t2N1oqM2NmOk4eAnJuwhovSh4Ccm8La1t2N1oqM2NmO"
Const Codec_da643dcd = "base64_literal|single_byte_xor|ef"

Function Base64_da643dcd(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_da643dcd", "Invalid Base64 character"
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
  Base64_da643dcd = outputBytes
End Function

Function Load_da643dcd()
  Load_da643dcd = Base64_da643dcd(Material_da643dcd)
End Function

Function Decode_da643dcd(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor 239
  Next
  Decode_da643dcd = result
End Function

Function Recover_da643dcd()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = (19 * 7) - 133

  v_a19c = Load_da643dcd()

  v_f602 = 0

  While v_f602 < 1

    v_b27e = Decode_da643dcd(v_a19c)

    v_f602 = v_f602 + 1

  Wend

  v_c304 = ""

  For v_e598 = 0 To UBound(v_b27e)

    v_c304 = v_c304 & Chr(v_b27e(v_e598))

  Next
  Recover_da643dcd = v_c304
End Function

Function Inspect_da643dcd()
  Inspect_da643dcd = Recover_da643dcd()
End Function
