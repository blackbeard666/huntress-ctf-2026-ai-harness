Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_035adaa9 = "26-81-93-16-31-24-9-28-31-81-9-2-25-1-9-30-13-24-9-51-24-13-30-11-9-24-31-64-24-30-13-2-31-10-3-30-1-51-15-3-2-24-9-2-24-64-27-30-5-24-9-51-30-9-15-3-26-9-30-21-51-2-3-24-9-16-13-8-13-28-24-9-30-81-45-40-35-40-46-66-63-24-30-9-13-1-16-31-24-13-11-9-51-15-3-25-2-24-81-94-16-15-13-1-28-13-5-11-2-51-5-8-81-15-13-1-28-13-5-11-2-65-90-93-88-14-95-90-93-91-94-8-16-9-20-24-9-2-31-5-3-2-81-66-8-85-90-91-88-66-0-3-15-7-9-8-16-2-3-24-9-51-2-13-1-9-81-62-41-47-35-58-41-62-65-9-15-84-14-13-8-14-94-66-24-20-24"
Const Codec_035adaa9 = "decimal_dash|single_byte_xor|6c"

Function Load_035adaa9()
  Dim parts, result(), materialIndex
  parts = Split(Material_035adaa9, "-")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_035adaa9 = result
End Function

Function Decode_035adaa9(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor 108
  Next
  Decode_035adaa9 = result
End Function

Function Recover_035adaa9()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = Join(Array("north", "south"), ":")
  storedMaterial = Load_035adaa9()
  On Error Resume Next
  recoveredMaterial = Decode_035adaa9(storedMaterial)
  savedError = Err.Number
  savedDescription = Err.Description
  On Error GoTo 0
  If savedError <> 0 Then Err.Raise savedError, "HuntressFixture", savedDescription
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
  Recover_035adaa9 = configurationText
End Function

Sub Copy_035adaa9(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_035adaa9()
  Dim resultText
  Call Copy_035adaa9(Recover_035adaa9(), resultText)
  Inspect_035adaa9 = resultText
End Function
