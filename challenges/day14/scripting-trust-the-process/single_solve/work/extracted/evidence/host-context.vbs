Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_93a178c4 = "Kn95e3Z3fi0teWI7PCAncismEDs8ICczKn95e3Z3fi0teWIhKCYuPyIuLHIrJhAhKCYuPyIuLDN+cjshOiAsECooLjs8MzY9LiEgJjssJgthKCEmOz8mPSwccj0qOz8uKy4zISAmOy49OigmKSEgLBAhPTo7Kj1jISAmOy49OigmKSEgLBAqKyAsKityPD8qOzwzfnI5"
Const Codec_93a178c4 = "base64_chunks|reverse_then_xor|4f"

Function Base64_93a178c4(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_93a178c4", "Invalid Base64 character"
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
  Base64_93a178c4 = outputBytes
End Function

Function Load_93a178c4()
  Dim partWidth, packedText
  partWidth = (Len(Material_93a178c4) + 3) \ 4
  packedText = Mid(Material_93a178c4, 1, partWidth) & Mid(Material_93a178c4, partWidth + 1, partWidth) & Mid(Material_93a178c4, partWidth * 2 + 1, partWidth) & Mid(Material_93a178c4, partWidth * 3 + 1)
  Load_93a178c4 = Base64_93a178c4(packedText)
End Function

Function Decode_93a178c4(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(UBound(v_a19c) - v_e598) = v_a19c(v_e598) Xor 79
  Next
  Decode_93a178c4 = result
End Function

Function Recover_93a178c4()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  ' configuration reconstruction
If (2 > 1) Then v_d41a = "left" Else v_d41a = "right"
  v_a19c = Load_93a178c4()
  For v_f602 = 0 To 0
    v_b27e = Decode_93a178c4(v_a19c)
  Next
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
' reconstruction complete
  Recover_93a178c4 = v_c304
End Function

Function Inspect_93a178c4()
  Inspect_93a178c4 = Recover_93a178c4()
End Function
