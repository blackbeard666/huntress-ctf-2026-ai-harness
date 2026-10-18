Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_492f5dd0 = "172,216,185,221,243,193,247,145,168,206,168,153,170,153,170,135,226,133,228,144,227,191,221,188,240,131,240,149,231,147,253,136,192,156,255,150,250,152,237,189,225,146,224,133,246,163,255,197,134,187,211,167,198,182,233,140,224,137,239,147,161,151,241,200,174,200,249,202,249,202,231,137,238,135,230,150,251,154,249,196,160,201,150,248,159,246,151,231,138,235,136,244,198,251,143,225,148,251,152,199,162,197,164,208,163,223,177,222,183,195,162,193,168,196,180,196,133,171,199,171,206,166,245,200,186,223,171,219,186,222,191,195,176,195,166,197,170,216,168,247,159,252,136,233,153,234,131,231,203,167,198,165,202,166,249,156,232,137,234,133,233,212,167,215,178,198,181,201,248,197"
Const Codec_492f5dd0 = "reversed_decimal|rolling_xor|b3"

Function Load_492f5dd0()
  Dim parts, result(), materialIndex
  parts = Split(Material_492f5dd0, ",")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(UBound(parts) - materialIndex) = CInt(parts(materialIndex))
  Next
  Load_492f5dd0 = result
End Function

Function Decode_492f5dd0(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  previous = 179
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor previous
    previous = storedMaterial(materialIndex)
  Next
  Decode_492f5dd0 = result
End Function

Function Recover_492f5dd0()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = (19 * 7) - 133
  storedMaterial = Load_492f5dd0()
  For decodePass = 0 To 0
    recoveredMaterial = Decode_492f5dd0(storedMaterial)
  Next
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
  Recover_492f5dd0 = configurationText
End Function

Function Inspect_492f5dd0()
  Inspect_492f5dd0 = Recover_492f5dd0()
End Function
