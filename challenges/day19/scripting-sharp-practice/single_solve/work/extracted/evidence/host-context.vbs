Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_56187a77 = "6b202c616e69786d6e2079787e727978427e72737b747a686f7c69747273316f7869686f73427e72737b747a686f7c69747273617c797c6d69786f204e7e6f746d6974737a3359747e697472737c6f64616e697c7a78427e72687369202c617e7c706d7c747a73427479207e7c706d7c747a73302c78782d2979242f7c296175726e694274792075726e69302c78782d2979242f7c29"
Const Codec_56187a77 = "hex_compact|single_byte_xor|1d"

Function Load_56187a77()
  Dim result(), materialIndex
  ReDim result((Len(Material_56187a77) \ 2) - 1)
  For materialIndex = 0 To UBound(result)
    result(materialIndex) = CInt("&H" & Mid(Material_56187a77, materialIndex * 2 + 1, 2))
  Next
  Load_56187a77 = result
End Function

Function Decode_56187a77(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor 29
  Next
  Decode_56187a77 = result
End Function

Function Recover_56187a77()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = (19 * 7) - 133

  storedMaterial = Load_56187a77()

  Do

    recoveredMaterial = Decode_56187a77(storedMaterial)

    Exit Do

  Loop

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_56187a77 = configurationText
End Function

Sub Copy_56187a77(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_56187a77()
  Dim resultText
  Call Copy_56187a77(Recover_56187a77(), resultText)
  Inspect_56187a77 = resultText
End Function
