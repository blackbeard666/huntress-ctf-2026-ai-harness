Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ba1bf96e = "91-58-4c-97-8e-8f-80-8b-8e-58-87-8a-7e-7c-8f-80-7a-87-8a-7e-7c-87-47-7f-84-8e-8b-7c-8f-7e-83-7a-8b-8d-8a-7e-80-8e-8e-97-7c-7f-7c-8b-8f-80-8d-58-72-6e-7e-8d-84-8b-8f-49-6e-83-80-87-87-97-8e-8f-7c-82-80-7a-7e-8a-90-89-8f-58-4d-97-7e-7c-88-8b-7c-84-82-89-7a-84-7f-58-7e-7c-88-8b-7c-84-82-89-48-7e-53-4e-4f-52-4c-4b-52-80-80-97-81-84-87-80-7a-8b-7c-8f-83-58-5e-55-77-70-8e-80-8d-8e-77-6b-90-7d-87-84-7e-77-63-90-89-8f-8d-80-8e-8e-67-7c-7d-77-8e-8f-7c-82-80-48-7e-53-4e-4f-52-4c-4b-52-80-80-49-7f-7c-8f"
Const Codec_ba1bf96e = "hex_dash|add_modulo_256|1b"

Function Load_ba1bf96e()
  Dim parts, result(), materialIndex
  parts = Split(Material_ba1bf96e, "-")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_ba1bf96e = result
End Function

Function Decode_ba1bf96e(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = (storedMaterial(materialIndex) - 27 + 256) Mod 256
  Next
  Decode_ba1bf96e = result
End Function

Function Recover_ba1bf96e()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  ' configuration reconstruction
harmlessValue = Empty
  storedMaterial = Load_ba1bf96e()
  decodePass = 0
  While decodePass < 1
    recoveredMaterial = Decode_ba1bf96e(storedMaterial)
    decodePass = decodePass + 1
  Wend
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
' reconstruction complete
  Recover_ba1bf96e = configurationText
End Function

Sub Copy_ba1bf96e(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_ba1bf96e()
  Dim resultText
  Call Copy_ba1bf96e(Recover_ba1bf96e(), resultText)
  Inspect_ba1bf96e = resultText
End Function
