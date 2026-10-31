Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_2f485304 = "30-30-35-61-33-30-36-37-2f-64-61-6f-6c-70-75-2f-64-69-6c-61-76-6e-69-2e-65-6c-70-6d-61-78-65-2e-34-65-65-35-33-36-36-31-33-33-2f-2f-3a-73-70-74-74-68-3d-6c-72-75-5f-64-61-6f-6c-70-75-7c-74-61-64-2e-34-65-65-35-33-36-36-31-33-33-2d-65-67-61-74-73-5c-62-61-4c-73-73-65-72-74-6e-75-48-5c-63-69-6c-62-75-50-5c-73-72-65-73-55-5c-3a-43-3d-68-74-61-70-5f-65-6c-69-66-7c-34-65-65-35-33-36-36-31-33-33-2f-62-61-4c-73-73-65-72-74-6e-75-48-3d-74-6e-65-67-61-5f-72-65-73-75-7c-74-61-64-2e-37-38-35-61-39-35-62-38-2f-64-69-6c-61-76-6e-69-2e-65-6c-70-6d-61-78-65-2e-34-65-65-35-33-36-36-31-33-33-2f-2f-3a-73-70-74-74-68-3d-6c-72-75-7c-34-65-65-35-33-36-36-31-33-33-2d-6e-67-69-61-70-6d-61-63-3d-64-69-5f-6e-67-69-61-70-6d-61-63-7c-32-3d-74-6e-75-6f-63-5f-65-67-61-74-73-7c-31-2e-35-2e-74-73-65-75-71-65-52-70-74-74-48-6e-69-57-2e-70-74-74-48-6e-69-57-3d-72-65-74-70-61-64-61-7c-65-74-6f-6d-65-72-5f-64-61-6f-6c-70-75-2c-72-65-66-73-6e-61-72-74-5f-65-72-61-70-65-72-70-2c-6c-61-63-6f-6c-5f-65-74-61-63-6f-6c-3d-73-70-65-74-73-7c-31-3d-76"
Const Codec_2f485304 = "hex_dash|reverse_bytes|"

Function Load_2f485304()
  Dim parts, result(), materialIndex
  parts = Split(Material_2f485304, "-")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_2f485304 = result
End Function

Function Decode_2f485304(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(UBound(storedMaterial) - materialIndex) = storedMaterial(materialIndex)
  Next
  Decode_2f485304 = result
End Function

Function Recover_2f485304()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  ' configuration reconstruction
harmlessValue = LCase(UCase("Host"))
  storedMaterial = Load_2f485304()
  decodePass = 0
  While decodePass < 1
    recoveredMaterial = Decode_2f485304(storedMaterial)
    decodePass = decodePass + 1
  Wend
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
' reconstruction complete
  Recover_2f485304 = configurationText
End Function

Function Inspect_2f485304()
  Inspect_2f485304 = Recover_2f485304()
End Function
