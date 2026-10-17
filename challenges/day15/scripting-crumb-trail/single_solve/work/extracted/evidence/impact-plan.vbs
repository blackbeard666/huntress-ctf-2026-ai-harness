Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_71dc87e1 = "cTgsd25vYGtuOGBpcGhgbVxvYFpvXG1iYG9uJ29tXGluYWptaFpeamlvYGlvJ3JtZG9gWm1gXmpxYG10Wmlqb2B3XF9ca29gbThOXm1ka29kaWIpQWRnYE50bm9gaEpdZWBeb3dub1xiYFpeanBpbzgtd15caGtcZGJpWmRfOF5caGtcZGJpKC1dXy40NF5cXCt3YHNvYGluZGppOCk0LS9dKylnal5mYF93aWpvYFppXGhgOE1APkpRQE0oXTQwK1wzMSwpb3Nv"
Const Codec_71dc87e1 = "base64_chunks|subtract_modulo_256|05"

Function Base64_71dc87e1(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_71dc87e1", "Invalid Base64 character"
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
  Base64_71dc87e1 = outputBytes
End Function

Function Load_71dc87e1()
  Dim partWidth, packedText
  partWidth = (Len(Material_71dc87e1) + 3) \ 4
  packedText = Mid(Material_71dc87e1, 1, partWidth) & Mid(Material_71dc87e1, partWidth + 1, partWidth) & Mid(Material_71dc87e1, partWidth * 2 + 1, partWidth) & Mid(Material_71dc87e1, partWidth * 3 + 1)
  Load_71dc87e1 = Base64_71dc87e1(packedText)
End Function

Function Decode_71dc87e1(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = (storedMaterial(materialIndex) + 5) Mod 256
  Next
  Decode_71dc87e1 = result
End Function

Function Recover_71dc87e1()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = LCase(UCase("Host"))

  storedMaterial = Load_71dc87e1()

  For decodePass = 0 To 0

    recoveredMaterial = Decode_71dc87e1(storedMaterial)

  Next

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_71dc87e1 = configurationText
End Function

Function Inspect_71dc87e1()
  Inspect_71dc87e1 = Recover_71dc87e1()
End Function
