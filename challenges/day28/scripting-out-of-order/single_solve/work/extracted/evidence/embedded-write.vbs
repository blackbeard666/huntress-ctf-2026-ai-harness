Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_cf57dd38 = "fUQ4g3p7bHd6RGtsanZrbGZsdGlsa2tsazN+eXB7bGZtcHNsg2hraHd7bHlESEtWS0k1Wnt5bGh0g3p7aG5sZmp2fHV7RDmDamh0d2hwbnVmcGtEamh0d2hwbnU0QGk3OEA6ajhpaYNtcHNsZndoe29ESkFjXHpseXpjV3xpc3BqY098dXt5bHp6U2hpY3p7aG5sNEBpNzhAOmo4aWk1a2h7"
Const Codec_cf57dd38 = "base64_literal|add_modulo_256|07"

Function Base64_cf57dd38(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_cf57dd38", "Invalid Base64 character"
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
  Base64_cf57dd38 = outputBytes
End Function

Function Load_cf57dd38()
  Load_cf57dd38 = Base64_cf57dd38(Material_cf57dd38)
End Function

Function Decode_cf57dd38(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = (item1(item5) - 7 + 256) Mod 256
  Next
  Decode_cf57dd38 = result
End Function

Function Recover_cf57dd38()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If (2 > 1) Then item4 = "left" Else item4 = "right"
  item1 = Load_cf57dd38()
  item6 = 0
  While item6 < 1
    item2 = Decode_cf57dd38(item1)
    item6 = item6 + 1
  Wend
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_cf57dd38 = item3
End Function

Function Inspect_cf57dd38()
  Inspect_cf57dd38 = Recover_cf57dd38()
End Function
