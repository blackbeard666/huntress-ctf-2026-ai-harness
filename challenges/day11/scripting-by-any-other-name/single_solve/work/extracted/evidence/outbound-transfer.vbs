Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_444ed06b = "fd:c0:f1:8d:fe:8a:ef:9f:ec:d1:bd:d2:b1:d0:a4:c1:9e:f2:9d:fe:9f:f3:df:af:dd:b8:c8:a9:db:be:e1:95:e7:86:e8:9b:fd:98:ea:c6:b3:c3:af:c0:a1:c5:9a:e8:8d:e0:8f:fb:9e:e2:83:e7:86:f6:82:e7:95:a8:ff:96:f8:b0:c4:b0:c0:ee:b9:d0:be:f6:82:f6:86:d4:b1:c0:b5:d0:a3:d7:f9:cc:e2:d3:af:dc:a8:c9:ae:cb:94:f7:98:ed:83:f7:ca:f8:84:e7:86:eb:9b:fa:93:f4:9a:c5:ac:c8:f5:96:f7:9a:ea:8b:e2:85:eb:c6:fe:cb:f3:c4:a0:97:a0:98:a9:9a:e6:93:e1:8d:b0:d8:ac:d8:a8:db:e1:ce:e1:d9:ec:d4:e3:87:b0:87:bf:8e:bd:93:f6:8e:ef:82:f2:9e:fb:d5:bc:d2:a4:c5:a9:c0:a4:8b:bf:dd:ef:de:e7:d3:ea:89:a7:c3:a2:d6:aa:df:ac:c9:bb:e4:85:e2:87:e9:9d:a0:e8:9d:f3:87:f5:90:e3:90:dc:bd:df:f0:c8:fd:c5:f2:96:a1:96:ae:9f:ac:d0:b6:df:b3:d6:89:f9:98:ec:84:b9:fa:c0:9c:c9:ba:df:ad:de:82:d2:a7:c5:a9:c0:a3:ff:b7:c2:ac:d8:aa:cf:bc:cf:83:e2:80:dc:af:db:ba:dd:b8:95:ad:98:a0:97:f3:c4:f3:cb:fa:c9:e7:83:e2:96:ea:9f:ef:83:ec:8d:e9:b6:c3:b1:dd:e0:88:fc:88:f8:8b:b1:9e:b1:89:bc:84:b3:d7:e0:d7:ef:de:ed:c3:a6:de:bf:d2:a2:ce:ab:85:ec:82:f4:95:f9:90:f4:db:ae:de:b2:dd:bc:d8:f7:94:f6:c6:a0:94:f6:93:f7"
Const Codec_444ed06b = "hex_colon|rolling_xor|8b"

Function Load_444ed06b()
  Dim parts, result(), materialIndex
  parts = Split(Material_444ed06b, ":")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_444ed06b = result
End Function

Function Decode_444ed06b(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  previous = 139
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor previous
    previous = storedMaterial(materialIndex)
  Next
  Decode_444ed06b = result
End Function

Function Recover_444ed06b()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  ' configuration reconstruction
harmlessValue = Join(Array("north", "south"), ":")
  storedMaterial = Load_444ed06b()
  decodePass = 0
  While decodePass < 1
    recoveredMaterial = Decode_444ed06b(storedMaterial)
    decodePass = decodePass + 1
  Wend
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
' reconstruction complete
  Recover_444ed06b = configurationText
End Function

Function Inspect_444ed06b()
  Dim fields
  fields = Split(Recover_444ed06b(), "|")
  Inspect_444ed06b = Join(fields, "|")
End Function
