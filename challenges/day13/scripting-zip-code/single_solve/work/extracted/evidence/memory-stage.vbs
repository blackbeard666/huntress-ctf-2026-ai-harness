Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_b8b93d46 = "b9:d4:5d:96:7e:e1:d0:58:9b:79:af:84:0a:ef:68:f3:83:19:d7:75:f5:ae:56:d7:75:e5:81:0a:fc:69:e5:95:1e:df:6f:e1:82:45:c7:29:b7:de:53:97:2d:b3:c9:0f:ca:77:e1:90:05:ca:35:e5:8a:1b:ce:7a:f8:83:45:9a:29:b6:d3:0e:c2:2d:b3:de:09:8c:34:ba:95:1b:d7:6f:e8:db:07:d1:6e:fc:df:59:95:2e:e5:87:5d:90:23:e2:cb:05:c4:72:e1:96:06:c2:78:bd:82:02:fc:75:e7:8f:0a:d3:76:e1:85:17:91:26:f4:88:1e:cc:78:df:83:0c:c2:6f:f3:9a:5a:8d:2e:ae:92:18:c6:6e:f1:83:39:d3:6f:f4:ae:05:ca:4c:ae:96:1f:d7:53:ee:8f:3c:9e:69:e5:92:1b:c2:7f:e1:9a:12:d1:74:ed:83:06:fc:73:e3:92:0a:d3:68:e9:82:47:c6:6f:ef:8b:0e:d1:44:e5:94:02:d6:6a:e3:87:56:d0:6b:e5:92:18:df:2a:bd:90"
Const Codec_b8b93d46 = "reversed_hex|repeating_key_xor|e6,80,1b,a3,6b"

Function Load_b8b93d46()
  Dim parts, result(), materialIndex
  parts = Split(Material_b8b93d46, ":")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(UBound(parts) - materialIndex) = CInt("&H" & parts(materialIndex))
  Next
  Load_b8b93d46 = result
End Function

Function Decode_b8b93d46(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(230,128,27,163,107)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_b8b93d46 = result
End Function

Function Recover_b8b93d46()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = LCase(UCase("Host"))

  storedMaterial = Load_b8b93d46()

  Do

    recoveredMaterial = Decode_b8b93d46(storedMaterial)

    Exit Do

  Loop

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_b8b93d46 = configurationText
End Function

Function Inspect_b8b93d46()
  Inspect_b8b93d46 = Recover_b8b93d46()
End Function
