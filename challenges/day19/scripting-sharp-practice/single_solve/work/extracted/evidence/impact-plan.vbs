Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_df5c041e = "hLmI9IfzluaVqM2j1rverM253IP3luSD5pLhzbnLqsS30b7Mof6d8pzojeOXu8y+16PGmeuO7YL0keOaxavEsNWpyKzNvcms3uOw06HIuMyly6yCxK3BpPeO/Ynsgc6sxqPAtMi7z67JrPOQ/4rkkK2f44DhjPyd9JP9osuvkvGQ/Y3sheKMoZiunv3E9pOrzq/Tts6637HCq8Sql7mBsIO01/mV+pnyl/OP4Y76n8Cuz6LH+qjtruG38qCNtdO3gLGB5dzyhv6K"
Const Codec_df5c041e = "base64_chunks|rolling_xor|f2"

Function Base64_df5c041e(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_df5c041e", "Invalid Base64 character"
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
  Base64_df5c041e = outputBytes
End Function

Function Load_df5c041e()
  Dim partWidth, packedText
  partWidth = (Len(Material_df5c041e) + 3) \ 4
  packedText = Mid(Material_df5c041e, 1, partWidth) & Mid(Material_df5c041e, partWidth + 1, partWidth) & Mid(Material_df5c041e, partWidth * 2 + 1, partWidth) & Mid(Material_df5c041e, partWidth * 3 + 1)
  Load_df5c041e = Base64_df5c041e(packedText)
End Function

Function Decode_df5c041e(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  previous = 242
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor previous
    previous = v_a19c(v_e598)
  Next
  Decode_df5c041e = result
End Function

Function Recover_df5c041e()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = (19 * 7) - 133
      v_a19c = Load_df5c041e()
      Do
        v_b27e = Decode_df5c041e(v_a19c)
        Exit Do
      Loop
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_df5c041e = v_c304
End Function

Function Inspect_df5c041e()
  Dim fields
  fields = Split(Recover_df5c041e(), "|")
  Inspect_df5c041e = Join(fields, "|")
End Function
