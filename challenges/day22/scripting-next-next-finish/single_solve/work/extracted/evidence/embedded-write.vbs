Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_e6e44d26 = "134,33,155,210,4,197,117,158,203,11,196,113,158,196,30,151,39,158,136,64,174,34,158,176,64,129,37,141,136,93,135,8,163,159,90,158,34,138,172,111,129,50,154,143,102,174,122,188,193,91,134,33,143,163,86,158,41,153,128,4,197,117,158,203,11,196,113,158,196,30,156,39,150,157,67,159,33,156,193,87,155,31,145,155,90,147,48,146,157,80,142,114,194,136,93,135,47,156,163,86,149,33,139,143,79,134,35,154,150,81,189,45,154,136,64,139,19,154,144,90,180,110,152,146,90,134,48,150,142,80,161,125,141,153,71,130,33,155,157,79,151,44,150,154,108,151,52,150,142,68,222,36,154,152,87,151,34,146,153,108,151,36,144,159,86,150,125,140,140,86,134,51,131,205,14,132"
Const Codec_e6e44d26 = "reversed_decimal|repeating_key_xor|f2,33,fc,ff,40"

Function Load_e6e44d26()
  Dim parts, result(), materialIndex
  parts = Split(Material_e6e44d26, ",")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(UBound(parts) - materialIndex) = CInt(parts(materialIndex))
  Next
  Load_e6e44d26 = result
End Function

Function Decode_e6e44d26(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(242,51,252,255,64)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_e6e44d26 = result
End Function

Function Recover_e6e44d26()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = (19 * 7) - 133

  storedMaterial = Load_e6e44d26()

  On Error Resume Next

  recoveredMaterial = Decode_e6e44d26(storedMaterial)

  savedError = Err.Number

  savedDescription = Err.Description

  On Error GoTo 0

  If savedError <> 0 Then Err.Raise savedError, "HuntressFixture", savedDescription

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_e6e44d26 = configurationText
End Function

Function Inspect_e6e44d26()
  Dim fields
  fields = Split(Recover_e6e44d26(), "|")
  Inspect_e6e44d26 = Join(fields, "|")
End Function
