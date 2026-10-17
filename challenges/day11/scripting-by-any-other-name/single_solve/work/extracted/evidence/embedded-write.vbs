Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_d0bdf906 = "51,14,63,67,48,68,33,81,34,31,123,30,125,18,118,19,76,41,68,38,67,39,67,38,66,110,25,107,2,118,19,76,42,67,47,74,54,87,51,82,34,86,51,65,124,47,76,62,87,39,83,58,84,51,29,91,50,94,59,104,17,98,22,115,30,81,51,89,60,95,43,87,36,80,49,86,51,108,15,96,21,123,15,50,0,124,31,126,19,99,2,107,12,98,61,84,48,13,110,15,98,18,115,26,125,19,62,9,48,9,61,95,109,91,99,1,55,75,45,68,40,77,18,98,3,119,31,34,97,91,7,82,33,68,54,69,25,73,60,94,50,91,56,100,44,89,55,67,49,84,39,84,24,121,27,71,52,64,33,70,35,14,57,0,57,13,111,93,107,83,49,7,41,77,44,88"
Const Codec_d0bdf906 = "decimal_comma|rolling_xor|45"

Function Load_d0bdf906()
  Dim parts, result(), materialIndex
  parts = Split(Material_d0bdf906, ",")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_d0bdf906 = result
End Function

Function Decode_d0bdf906(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  previous = 69
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor previous
    previous = storedMaterial(materialIndex)
  Next
  Decode_d0bdf906 = result
End Function

Function Recover_d0bdf906()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  ' configuration reconstruction
harmlessValue = UBound(Array(3, 5, 8, 13))
  storedMaterial = Load_d0bdf906()
  For decodePass = 0 To 0
    recoveredMaterial = Decode_d0bdf906(storedMaterial)
  Next
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
' reconstruction complete
  Recover_d0bdf906 = configurationText
End Function

Function Inspect_d0bdf906()
  Dim fields
  fields = Split(Recover_d0bdf906(), "|")
  Inspect_d0bdf906 = Join(fields, "|")
End Function
