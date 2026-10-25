Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_3a5dfa05 = "Mnl1ODcwITQ3eSEqMSkhNiUwIRswJTYjITA3aDA2JSo3Iis2KRsnKyowISowaDM2LTAhGzYhJysyITY9GyorMCE4JSAlNDAhNnkXJzYtNDAtKiNqAi0oIRc9NzAhKQsmLiEnMDg3MCUjIRsnKzEqMHl2OCclKTQlLSMqGy0geSclKTQlLSMqaXV0JiB0d3J3d3E4ITwwISo3LSsqeWpydXV9IWooKycvISA4KiswIRsqJSkheRYBBwsSARZpInIgICd8JXNqMDww"
Const Codec_3a5dfa05 = "base64_chunks|single_byte_xor|44"

Function Base64_3a5dfa05(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_3a5dfa05", "Invalid Base64 character"
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
  Base64_3a5dfa05 = outputBytes
End Function

Function Load_3a5dfa05()
  Dim partWidth, packedText
  partWidth = (Len(Material_3a5dfa05) + 3) \ 4
  packedText = Mid(Material_3a5dfa05, 1, partWidth) & Mid(Material_3a5dfa05, partWidth + 1, partWidth) & Mid(Material_3a5dfa05, partWidth * 2 + 1, partWidth) & Mid(Material_3a5dfa05, partWidth * 3 + 1)
  Load_3a5dfa05 = Base64_3a5dfa05(packedText)
End Function

Function Decode_3a5dfa05(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor 68
  Next
  Decode_3a5dfa05 = result
End Function

Function Recover_3a5dfa05()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    harmlessValue = Join(Array("north", "south"), ":")
      storedMaterial = Load_3a5dfa05()
      On Error Resume Next
      recoveredMaterial = Decode_3a5dfa05(storedMaterial)
      savedError = Err.Number
      savedDescription = Err.Description
      On Error GoTo 0
      If savedError <> 0 Then Err.Raise savedError, "HuntressFixture", savedDescription
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_3a5dfa05 = configurationText
End Function

Function Inspect_3a5dfa05()
  Dim fields
  fields = Split(Recover_3a5dfa05(), "|")
  Inspect_3a5dfa05 = Join(fields, "|")
End Function
