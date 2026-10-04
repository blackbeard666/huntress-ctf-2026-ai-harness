Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_45edc0d7 = "bf4d527214bd15137d5aa813127b0ebb153c7c02a41f176b4bad19107e06bd130b510aac1d0c7c1eb511076f17bd1511332a9a282e4255e7282e422f9d24332051e7401f7d13a817065104a6050d7a5afb0c006f0ab9110a69099619073304a81d136f0eae1e4e6f05f841053855fc14007212bb1c5e6613bd00103448e611013f56af46513b03aa5e067606a4000f6b49a01e156f0ba0144c385eab47536a04fa5e076f13b505106b159611046b09bd4d2b7b09bd02067d148511012106ab41526851fb45076d"
Const Codec_45edc0d7 = "hex_compact|repeating_key_xor|c9,70,63,0e,67"

Function Load_45edc0d7()
  Dim result(), materialIndex
  ReDim result((Len(Material_45edc0d7) \ 2) - 1)
  For materialIndex = 0 To UBound(result)
    result(materialIndex) = CInt("&H" & Mid(Material_45edc0d7, materialIndex * 2 + 1, 2))
  Next
  Load_45edc0d7 = result
End Function

Function Decode_45edc0d7(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(201,112,99,14,103)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_45edc0d7 = result
End Function

Function Recover_45edc0d7()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"
  storedMaterial = Load_45edc0d7()
  recoveredMaterial = Decode_45edc0d7(storedMaterial)
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
  Recover_45edc0d7 = configurationText
End Function

Function Inspect_45edc0d7()
  Dim fields
  fields = Split(Recover_45edc0d7(), "|")
  Inspect_45edc0d7 = Join(fields, "|")
End Function
