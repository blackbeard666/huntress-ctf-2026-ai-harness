Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_f55859a6 = "dj0xfHN0ZXBzPWxvY2F0ZV9sb2NhbCxkaXNwYXRjaF9wcm9jZXNzfGFkYXB0ZXI9V1NjcmlwdC5TaGVsbHxzdGFnZV9jb3VudD0yfGNhbXBhaWduX2lkPWNhbXBhaWduLTNmMjU0MjAxYWN8ZmlsZV9wYXRoPUM6XFVzZXJzXFB1YmxpY1xIdW50cmVzc0xhYlxzdGFnZS0zZjI1NDIwMWFjLmRhdA=="
Const Codec_f55859a6 = "base64_literal|identity|"

Function Base64_f55859a6(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_f55859a6", "Invalid Base64 character"
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
  Base64_f55859a6 = outputBytes
End Function

Function Load_f55859a6()
  Load_f55859a6 = Base64_f55859a6(Material_f55859a6)
End Function

Function Decode_f55859a6(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_f55859a6 = result
End Function

Function Recover_f55859a6()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    If (2 > 1) Then NeUtRaL = "left" Else NeUtRaL = "right"
      SoUrCeByTeS = Load_f55859a6()
      On Error Resume Next
      DeCoDeDByTeS = Decode_f55859a6(SoUrCeByTeS)
      ErRoRnUmBeR = Err.Number
      ErRoRdEsCrIpTiOn = Err.Description
      On Error GoTo 0
      If ErRoRnUmBeR <> 0 Then Err.Raise ErRoRnUmBeR, "HuntressFixture", ErRoRdEsCrIpTiOn
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_f55859a6 = DeScRiPtOrTeXt
End Function

Function Inspect_f55859a6()
  Dim fields
  fields = Split(Recover_f55859a6(), "|")
  Inspect_f55859a6 = Join(fields, "|")
End Function
