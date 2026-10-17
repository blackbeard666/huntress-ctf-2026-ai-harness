Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_9cd60fc5 = "ajElcGdoWWRnMVhZV2NYWVNXY2JaXVtpZlVoXWNiIGZZaGlmYlNXY2JaXVtpZlVoXWNicFVYVWRoWWYxR1dmXWRoXWJbIjpdYFlHbWdoWWFDVl5ZV2hwZ2hVW1lTV2NpYmgxJXBXVWFkVV1bYlNdWDFXVWFkVV1bYiEpJCsrWlcrWFgkcFxjZ2hTXVgxXGNnaCEpJCsrWlcrWFgk"
Const Codec_9cd60fc5 = "base64_chunks|subtract_modulo_256|0c"

Function Base64_9cd60fc5(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_9cd60fc5", "Invalid Base64 character"
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
  Base64_9cd60fc5 = outputBytes
End Function

Function Load_9cd60fc5()
  Dim partWidth, packedText
  partWidth = (Len(Material_9cd60fc5) + 3) \ 4
  packedText = Mid(Material_9cd60fc5, 1, partWidth) & Mid(Material_9cd60fc5, partWidth + 1, partWidth) & Mid(Material_9cd60fc5, partWidth * 2 + 1, partWidth) & Mid(Material_9cd60fc5, partWidth * 3 + 1)
  Load_9cd60fc5 = Base64_9cd60fc5(packedText)
End Function

Function Decode_9cd60fc5(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 12) Mod 256
  Next
  Decode_9cd60fc5 = result
End Function

Function Recover_9cd60fc5()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = Join(Array("north", "south"), ":")
      SoUrCeByTeS = Load_9cd60fc5()
      On Error Resume Next
      DeCoDeDByTeS = Decode_9cd60fc5(SoUrCeByTeS)
      ErRoRnUmBeR = Err.Number
      ErRoRdEsCrIpTiOn = Err.Description
      On Error GoTo 0
      If ErRoRnUmBeR <> 0 Then Err.Raise ErRoRnUmBeR, "HuntressFixture", ErRoRdEsCrIpTiOn
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_9cd60fc5 = DeScRiPtOrTeXt
End Function

Function Inspect_9cd60fc5()
  Inspect_9cd60fc5 = Recover_9cd60fc5()
End Function
