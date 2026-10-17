Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_683bde52 = "59,69,93,29,127,43,12,74,0,124,119,11,4,97,92,25,114,106,118,75,114,88,68,82,119,16,88,93,92,119,51,89,76,88,122,32,81,7,6,44,120,11,17,29,36,33,82,64,64,119,42,73,81,86,101,44,14,16,10,42,43,91,79,11,123,98,83,78,90,120,63,80,72,80,36,43,84,118,93,126,38,92,89,94,120,44,65,27,14,109,33,72,70,80,70,42,90,72,71,106,51,80,72,86,107,59,110,7,113,93,0,121,104,14,107,42,73,89,82,125,46,65,76,71,118,33,98,80,65,124,57,82,74,86,107,16,88,93,90,107,56,17,93,93,124,59,83,70,80,70,34,79,70,85,106,33,92,91,71,53,60,73,76,84,107,46,73,118,86,109,46,79,76,94,108,33,88,20,64,105,42,73,90,79,40,114,75"
Const Codec_683bde52 = "reversed_decimal|repeating_key_xor|3d,4f,19,33,29"

Function Load_683bde52()
  Dim parts, result(), materialIndex
  parts = Split(Material_683bde52, ",")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(UBound(parts) - materialIndex) = CInt(parts(materialIndex))
  Next
  Load_683bde52 = result
End Function

Function Decode_683bde52(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(61,79,25,51,41)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_683bde52 = result
End Function

Function Recover_683bde52()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = LCase(UCase("Host"))

  storedMaterial = Load_683bde52()

  For decodePass = 0 To 0

    recoveredMaterial = Decode_683bde52(storedMaterial)

  Next

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_683bde52 = configurationText
End Function

Function Inspect_683bde52()
  Dim fields
  fields = Split(Recover_683bde52(), "|")
  Inspect_683bde52 = Join(fields, "|")
End Function
