Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_856b84bb = "2aPDdujb+4J5psv7kWX/ysGXZ/nK+pZv/4PpgGPvysGUY/fK4pNu+t/ql3im/P2AY+vb95xtten3nm/I1u2Gb/bg/Jhv+NvigX76yPutafTa8IY3qdP9k2frzveVZMTG+s9p+sLuk2P8wbOUOv7J/JE/qZmnjmzyw/utevrb9s9JofPLgW/p3MKif/nD95FW09rwhnj+3O2+a/nz7YZr/MqzlDr+yfyRP6mZp9xu+ts="
Const Codec_856b84bb = "base64_chunks|repeating_key_xor|af,9e,f2,0a,9b"

Function Base64_856b84bb(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_856b84bb", "Invalid Base64 character"
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
  Base64_856b84bb = outputBytes
End Function

Function Load_856b84bb()
  Dim partWidth, packedText
  partWidth = (Len(Material_856b84bb) + 3) \ 4
  packedText = Mid(Material_856b84bb, 1, partWidth) & Mid(Material_856b84bb, partWidth + 1, partWidth) & Mid(Material_856b84bb, partWidth * 2 + 1, partWidth) & Mid(Material_856b84bb, partWidth * 3 + 1)
  Load_856b84bb = Base64_856b84bb(packedText)
End Function

Function Decode_856b84bb(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(175,158,242,10,155)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_856b84bb = result
End Function

Function Recover_856b84bb()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"

  storedMaterial = Load_856b84bb()

  For decodePass = 0 To 0

    recoveredMaterial = Decode_856b84bb(storedMaterial)

  Next

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_856b84bb = configurationText
End Function

Function Inspect_856b84bb()
  Inspect_856b84bb = Recover_856b84bb()
End Function
