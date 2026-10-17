Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_a72bca86 = "YikdaF9gUVxfKVhbT01gUUtYW09NWBhQVV9cTWBPVEtcXltPUV9faE1QTVxgUV4pQz9PXlVcYBo/VFFYWGhfYE1TUUtPW2FaYCkeaE9NWVxNVVNaS1VQKU9NWVxNVVNaGSBQT1BSHVJOIE1oUlVYUUtcTWBUKS8mSEFfUV5fSDxhTlhVT0g0YVpgXlFfXzhNTkhfYE1TURkgUE9QUh1STiBNGlBNYA=="
Const Codec_a72bca86 = "base64_chunks|subtract_modulo_256|14"

Function Base64_a72bca86(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_a72bca86", "Invalid Base64 character"
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
  Base64_a72bca86 = outputBytes
End Function

Function Load_a72bca86()
  Dim partWidth, packedText
  partWidth = (Len(Material_a72bca86) + 3) \ 4
  packedText = Mid(Material_a72bca86, 1, partWidth) & Mid(Material_a72bca86, partWidth + 1, partWidth) & Mid(Material_a72bca86, partWidth * 2 + 1, partWidth) & Mid(Material_a72bca86, partWidth * 3 + 1)
  Load_a72bca86 = Base64_a72bca86(packedText)
End Function

Function Decode_a72bca86(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = (v_a19c(v_e598) + 20) Mod 256
  Next
  Decode_a72bca86 = result
End Function

Function Recover_a72bca86()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = Join(Array("north", "south"), ":")
  v_a19c = Load_a72bca86()
  For v_f602 = 0 To 0
    v_b27e = Decode_a72bca86(v_a19c)
  Next
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_a72bca86 = v_c304
End Function

Function Inspect_a72bca86()
  Dim fields
  fields = Split(Recover_a72bca86(), "|")
  Inspect_a72bca86 = Join(fields, "|")
End Function
