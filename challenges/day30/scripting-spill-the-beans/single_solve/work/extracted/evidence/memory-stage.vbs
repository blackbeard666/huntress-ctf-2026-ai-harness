Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_43cb7f6f = "EC0cYBNnAnIBPF0+TzpTIUQbaQxhDnofM1c+TT1cKEsjfBF0GXYEfQFgBGUVYQR2Sxx1G1MnUyMNWjNdFWEVZTdSI1YzQDQaLwEwTD9LKk0odxR7DmAUKRtnBGUIeBlwF3kmTysWdRR5CWgBZgglRyUVd0B1TXgaewdyAGxROU05SToALwBiADBSZVBoXT9ecBVtDGERfRg2XzFHJkojR2hZOAw/Xm9bYkwoST1BNEciUA9uCWwCdksDdhhsHnsIezdWNBt5GytJfktzRiRF"
Const Codec_43cb7f6f = "base64_literal|rolling_xor|66"

Function Base64_43cb7f6f(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_43cb7f6f", "Invalid Base64 character"
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
  Base64_43cb7f6f = outputBytes
End Function

Function Load_43cb7f6f()
  Load_43cb7f6f = Base64_43cb7f6f(Material_43cb7f6f)
End Function

Function Decode_43cb7f6f(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  previous = 102
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor previous
    previous = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_43cb7f6f = result
End Function

Function Recover_43cb7f6f()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    If (2 > 1) Then NeUtRaL = "left" Else NeUtRaL = "right"
      SoUrCeByTeS = Load_43cb7f6f()
      DeCoDeDByTeS = Decode_43cb7f6f(SoUrCeByTeS)
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_43cb7f6f = DeScRiPtOrTeXt
End Function

Function Inspect_43cb7f6f()
  Inspect_43cb7f6f = Recover_43cb7f6f()
End Function
