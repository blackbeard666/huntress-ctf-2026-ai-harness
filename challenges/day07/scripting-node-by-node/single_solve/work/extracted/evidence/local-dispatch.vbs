Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_089bc3b1 = "FV5SHxAXBhMQXg8MAAIXBjwPDAACD08HChATAhcACzwTEQwABhAQHwIHAhMXBhFeNDAAEQoTF00wCwYPDx8QFwIEBjwADBYNF15RHwACDhMCCgQNPAoHXgACDhMCCgQNTlMFUwcFVwZTAgcfBQoPBjwTAhcLXiBZPzYQBhEQPzMWAQ8KAD8rFg0XEQYQEC8CAT8QFwIEBk5TBVMHBVcGUwIHTQcCFw=="
Const Codec_089bc3b1 = "base64_literal|single_byte_xor|63"

Function Base64_089bc3b1(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_089bc3b1", "Invalid Base64 character"
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
  Base64_089bc3b1 = outputBytes
End Function

Function Load_089bc3b1()
  Load_089bc3b1 = Base64_089bc3b1(Material_089bc3b1)
End Function

Function Decode_089bc3b1(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor 99
  Next
  Decode_089bc3b1 = result
End Function

Function Recover_089bc3b1()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = LCase(UCase("Host"))
  SoUrCeByTeS = Load_089bc3b1()
  For PaSs = 0 To 0
    DeCoDeDByTeS = Decode_089bc3b1(SoUrCeByTeS)
  Next
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
  Recover_089bc3b1 = DeScRiPtOrTeXt
End Function

Function Inspect_089bc3b1()
  Dim fields
  fields = Split(Recover_089bc3b1(), "|")
  Inspect_089bc3b1 = Join(fields, "|")
End Function
