Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_3fcb01bf = "30-0d-3c-40-33-47-22-52-21-1c-70-1f-7c-1d-69-0c-53-3f-50-33-52-3e-12-76-1f-6c-1c-7d-09-6a-02-5d-2d-5f-30-53-36-45-36-4a-2b-4f-2e-5e-2a-4f-3d-00-53-3b-5e-32-5e-70-31-41-31-5d-34-57-36-42-2b-44-2a-56-25-51-30-57-32-6d-0e-61-14-7a-0e-33-01-7d-1e-7f-12-62-03-6a-0d-63-3c-55-31-0c-6f-0e-63-13-72-1b-7c-12-3f-5d-69-0b-6d-0b-38-0a-3f-0f-3a-46-20-49-25-40-1f-6f-0e-7a-12-2f-6c-56-0a-5f-2c-49-3b-48-14-44-31-53-3f-56-35-69-21-54-3a-4e-3c-59-2a-59-15-74-16-4a-39-4d-2c-4b-2e-03-61-55-37-51-37-04-36-03-33-06-28-4c-2d-59"
Const Codec_3fcb01bf = "hex_dash|rolling_xor|46"

Function Load_3fcb01bf()
  Dim parts, result(), materialIndex
  parts = Split(Material_3fcb01bf, "-")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_3fcb01bf = result
End Function

Function Decode_3fcb01bf(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  previous = 70
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor previous
    previous = storedMaterial(materialIndex)
  Next
  Decode_3fcb01bf = result
End Function

Function Recover_3fcb01bf()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"
      storedMaterial = Load_3fcb01bf()
      recoveredMaterial = Decode_3fcb01bf(storedMaterial)
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_3fcb01bf = configurationText
End Function

Function Inspect_3fcb01bf()
  Dim fields
  fields = Split(Recover_3fcb01bf(), "|")
  Inspect_3fcb01bf = Join(fields, "|")
End Function
