Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_c2548207 = "33-98-bd-db-2a-31-c0-fc-d4-64-24-c6-fd-d2-30-37-c0-d3-d5-3c-28-ca-f8-c2-75-21-cc-ff-d7-38-31-c6-e4-f8-34-20-c8-e3-d5-20-39-c4-e8-c6-29-31-c0-fe-9a-14-16-fd-c1-eb-6b-6b-fd-c1-eb-11-11-f1-dc-89-6f-6b-95-f0-d4-2d-24-c2-e9-f8-3a-2a-d0-e2-d3-64-77-d9-ef-c6-34-35-c4-e5-c0-37-1a-cc-e8-9a-3a-24-c8-fc-c6-30-22-cb-a1-9e-6e-77-c3-b4-93-61-24-9c-ea-db-2c-37-c9-b1-cf-2d-31-d5-ff-9d-76-6a-9c-bb-95-3f-7d-91-b4-c6-60-23-8b-e9-df-38-28-d5-e0-c2-77-2c-cb-fa-c6-35-2c-c1-a3-c2-3b-74-96-ef-c2-6b-24-8b-e8-c6-2d-39-d0-ff-c2-2b-1a-c4-eb-c2-37-31-98-c4-d2-37-31-d7-e9-d4-2a-09-c4-ee-88-60-72-97-ea-9f-6d-7d-c4-b5-c1"
Const Codec_c2548207 = "hex_dash|repeating_key_xor|45,a5,8c,a7,59"

Function Load_c2548207()
  Dim parts, result(), materialIndex
  parts = Split(Material_c2548207, "-")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_c2548207 = result
End Function

Function Decode_c2548207(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(69,165,140,167,89)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_c2548207 = result
End Function

Function Recover_c2548207()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = (19 * 7) - 133
  storedMaterial = Load_c2548207()
  decodePass = 0
  While decodePass < 1
    recoveredMaterial = Decode_c2548207(storedMaterial)
    decodePass = decodePass + 1
  Wend
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
  Recover_c2548207 = configurationText
End Function

Function Inspect_c2548207()
  Inspect_c2548207 = Recover_c2548207()
End Function
