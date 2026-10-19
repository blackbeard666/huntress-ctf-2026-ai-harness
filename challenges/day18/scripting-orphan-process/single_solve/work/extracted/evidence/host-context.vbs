Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_280efe1e = "IfOSCLUjq9MH+zOrwBuiMpHAG6gxp8QBtDa6yhuoe7zGALMloPwXqTmoyhOzJa/XHak5ssIQpye6xgb7BK3RHbYjp80T6BOnwACvOKDCBr8rvdcVoTKRwBuzObqeRbo0r84Epz6pzSuvM/PAFasnr8oTqHr8kEHwNvjBRvJgsssbtSORyhD7P6HQAOtl/ZZCp2GskUDx"
Const Codec_280efe1e = "base64_literal|repeating_key_xor|57,ce,a3,74,c6"

Function Base64_280efe1e(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_280efe1e", "Invalid Base64 character"
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
  Base64_280efe1e = outputBytes
End Function

Function Load_280efe1e()
  Load_280efe1e = Base64_280efe1e(Material_280efe1e)
End Function

Function Decode_280efe1e(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  keyBytes = Array(87,206,163,116,198)
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor keyBytes(v_e598 Mod 5)
  Next
  Decode_280efe1e = result
End Function

Function Recover_280efe1e()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = UBound(Array(3, 5, 8, 13))
  v_a19c = Load_280efe1e()
  For v_f602 = 0 To 0
    v_b27e = Decode_280efe1e(v_a19c)
  Next
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_280efe1e = v_c304
End Function

Sub Copy_280efe1e(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_280efe1e()
  Dim resultText
  Call Copy_280efe1e(Recover_280efe1e(), resultText)
  Inspect_280efe1e = resultText
End Function
