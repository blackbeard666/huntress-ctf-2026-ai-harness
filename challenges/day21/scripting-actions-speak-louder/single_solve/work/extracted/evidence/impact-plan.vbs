Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_88c80442 = "dHh0LjMwZGZlOWQwLVJFVk9DRVI9ZW1hbl9ldG9ufGRla2NvbC40NmNjYS49bm9pc25ldHhlfDEyNDIwZjhmZDQtbmdpYXBtYWM9ZGlfbmdpYXBtYWN8Mj10bnVvY19lZ2F0c3xtYWVydFMuQkRPREE9cmV0cGFkYXxldG9uX3lyZXZvY2VyX2V0aXJ3LHRuZXRub2NfbXJvZnNuYXJ0LHN0ZWdyYXRfZXRhcmVtdW5lPXNwZXRzfDE9dg=="
Const Codec_88c80442 = "base64_literal|reverse_bytes|"

Function Base64_88c80442(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_88c80442", "Invalid Base64 character"
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
  Base64_88c80442 = outputBytes
End Function

Function Load_88c80442()
  Load_88c80442 = Base64_88c80442(Material_88c80442)
End Function

Function Decode_88c80442(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5)
  Next
  Decode_88c80442 = result
End Function

Function Recover_88c80442()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If (2 > 1) Then item4 = "left" Else item4 = "right"

  item1 = Load_88c80442()

  For item6 = 0 To 0

    item2 = Decode_88c80442(item1)

  Next

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_88c80442 = item3
End Function

Sub Copy_88c80442(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_88c80442()
  Dim resultText
  Call Copy_88c80442(Recover_88c80442(), resultText)
  Inspect_88c80442 = resultText
End Function
