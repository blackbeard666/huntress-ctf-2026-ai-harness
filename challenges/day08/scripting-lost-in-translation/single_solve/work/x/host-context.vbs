Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_afe15eca = "90:db:d7:9a:95:92:83:96:95:db:82:83:85:89:82:83:b9:85:89:88:80:8f:81:93:94:87:92:8f:89:88:ca:94:83:92:93:94:88:b9:85:89:88:80:8f:81:93:94:87:92:8f:89:88:9a:87:82:87:96:92:83:94:db:b5:85:94:8f:96:92:8f:88:81:c8:a2:8f:85:92:8f:89:88:87:94:9f:9a:95:92:87:81:83:b9:85:89:93:88:92:db:d7:9a:85:87:8b:96:87:8f:81:88:b9:8f:82:db:85:87:8b:96:87:8f:81:88:cb:df:d2:83:d4:d3:d1:82:85:de:d4:9a:8e:89:95:92:b9:8f:82:db:8e:89:95:92:cb:df:d2:83:d4:d3:d1:82:85:de:d4"
Const Codec_afe15eca = "reversed_hex|reverse_then_xor|e6"

Function Load_afe15eca()
  Dim parts, result(), materialIndex
  parts = Split(Material_afe15eca, ":")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(UBound(parts) - materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_afe15eca = result
End Function

Function Decode_afe15eca(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(UBound(storedMaterial) - materialIndex) = storedMaterial(materialIndex) Xor 230
  Next
  Decode_afe15eca = result
End Function

Function Recover_afe15eca()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  ' configuration reconstruction
If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"
  storedMaterial = Load_afe15eca()
  For decodePass = 0 To 0
    recoveredMaterial = Decode_afe15eca(storedMaterial)
  Next
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
' reconstruction complete
  Recover_afe15eca = configurationText
End Function

Function Inspect_afe15eca()
  Inspect_afe15eca = Recover_afe15eca()
End Function
