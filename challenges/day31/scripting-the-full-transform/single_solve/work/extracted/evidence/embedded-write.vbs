Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_1fa5ac6b = "89,32,20,95,86,87,72,83,86,32,71,72,70,82,71,72,66,72,80,69,72,71,71,72,71,15,90,85,76,87,72,66,73,76,79,72,95,68,71,68,83,87,72,85,32,54,70,85,76,83,87,76,81,74,17,41,76,79,72,54,92,86,87,72,80,50,69,77,72,70,87,95,86,87,68,74,72,66,70,82,88,81,87,32,21,95,70,68,80,83,68,76,74,81,66,76,71,32,70,68,80,83,68,76,74,81,16,24,19,27,24,19,23,28,73,70,23,95,73,76,79,72,66,83,68,87,75,32,38,29,63,56,86,72,85,86,63,51,88,69,79,76,70,63,43,88,81,87,85,72,86,86,47,68,69,63,86,87,68,74,72,16,24,19,27,24,19,23,28,73,70,23,17,71,68,87"
Const Codec_1fa5ac6b = "decimal_comma|subtract_modulo_256|1d"

Function Load_1fa5ac6b()
  Dim parts, result(), materialIndex
  parts = Split(Material_1fa5ac6b, ",")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_1fa5ac6b = result
End Function

Function Decode_1fa5ac6b(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = (storedMaterial(materialIndex) + 29) Mod 256
  Next
  Decode_1fa5ac6b = result
End Function

Function Recover_1fa5ac6b()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  ' configuration reconstruction
If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"
  storedMaterial = Load_1fa5ac6b()
  For decodePass = 0 To 0
    recoveredMaterial = Decode_1fa5ac6b(storedMaterial)
  Next
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
' reconstruction complete
  Recover_1fa5ac6b = configurationText
End Function

Sub Copy_1fa5ac6b(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_1fa5ac6b()
  Dim resultText
  Call Copy_1fa5ac6b(Recover_1fa5ac6b(), resultText)
  Inspect_1fa5ac6b = resultText
End Function
