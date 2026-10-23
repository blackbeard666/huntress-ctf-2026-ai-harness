Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_f8bfc232 = "+bK+8/z76v/8su7s/vrm/erQ/eri4Pvqo/j95vvq0Onm4+qj6+b8/+777OfQ//3g7Or8/KPn7uHr4Onp0Pzs/eb/+/Pu6+7/++r9ssLc18LDvaHXwsPH29vfobmhv/P8++7o6tDs4Prh+7K78+zu4v/u5ujh0Obrsuzu4v/u5ujhory8vLjqvry3vuvz+v3jsuf7+//8taCgvLy8uOq+vLe+66Hq9+7i/+Pqoebh+e7j5uugub/sue3qub2h6+778/r86v3Q7ujq4fuyx/rh+/3q/PzD7u2gvLy8uOq+vLe+6/Pp5uPq0P/u++eyzLXT2vzq/fzT3/rt4+bs08f64fv96vz8w+7t0/z77ujqory8vLjqvry3vuuh6+778/3q6Ob8+/320P/u++eyx8TM2tPc4On7+O796tPH+uH7/er8/MPu7dPL5vz/4Pzu7ePq07y8vLjqvry3vuvz4er3+9D8++7o6rL96vzg+v3s6qL87uL/4+qh//y+"
Const Codec_f8bfc232 = "base64_chunks|single_byte_xor|8f"

Function Base64_f8bfc232(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_f8bfc232", "Invalid Base64 character"
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
  Base64_f8bfc232 = outputBytes
End Function

Function Load_f8bfc232()
  Dim partWidth, packedText
  partWidth = (Len(Material_f8bfc232) + 3) \ 4
  packedText = Mid(Material_f8bfc232, 1, partWidth) & Mid(Material_f8bfc232, partWidth + 1, partWidth) & Mid(Material_f8bfc232, partWidth * 2 + 1, partWidth) & Mid(Material_f8bfc232, partWidth * 3 + 1)
  Load_f8bfc232 = Base64_f8bfc232(packedText)
End Function

Function Decode_f8bfc232(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor 143
  Next
  Decode_f8bfc232 = result
End Function

Function Recover_f8bfc232()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = (19 * 7) - 133
  item1 = Load_f8bfc232()
  item6 = 0
  While item6 < 1
    item2 = Decode_f8bfc232(item1)
    item6 = item6 + 1
  Wend
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_f8bfc232 = item3
End Function

Sub Copy_f8bfc232(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_f8bfc232()
  Dim resultText
  Call Copy_f8bfc232(Recover_f8bfc232(), resultText)
  Inspect_f8bfc232 = resultText
End Function
