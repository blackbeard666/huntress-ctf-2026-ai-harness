Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_5dcd247b = "214-157-145-220-211-212-197-208-211-157-197-206-213-205-197-210-193-212-197-255-212-193-210-199-197-212-211-140-212-210-193-206-211-198-207-210-205-255-195-207-206-212-197-206-212-140-215-210-201-212-197-255-210-197-195-207-214-197-210-217-255-206-207-212-197-220-193-196-193-208-212-197-210-157-225-228-239-228-226-142-243-212-210-197-193-205-220-211-212-193-199-197-255-195-207-213-206-212-157-146-220-195-193-205-208-193-201-199-206-255-201-196-157-195-193-205-208-193-201-199-206-141-144-197-146-151-153-149-145-151-197-150-220-197-216-212-197-206-211-201-207-206-157-142-146-150-195-145-153-142-204-207-195-203-197-196-220-206-207-212-197-255-206-193-205-197-157-242-229-227-239-246-229-242-141-196-194-145-144-146-196-145-149-142-212-216-212"
Const Codec_5dcd247b = "decimal_dash|single_byte_xor|a0"

Function Load_5dcd247b()
  Dim parts, result(), materialIndex
  parts = Split(Material_5dcd247b, "-")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_5dcd247b = result
End Function

Function Decode_5dcd247b(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor 160
  Next
  Decode_5dcd247b = result
End Function

Function Recover_5dcd247b()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"
  storedMaterial = Load_5dcd247b()
  For decodePass = 0 To 0
    recoveredMaterial = Decode_5dcd247b(storedMaterial)
  Next
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
  Recover_5dcd247b = configurationText
End Function

Sub Copy_5dcd247b(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_5dcd247b()
  Dim resultText
  Call Copy_5dcd247b(Recover_5dcd247b(), resultText)
  Inspect_5dcd247b = resultText
End Function
