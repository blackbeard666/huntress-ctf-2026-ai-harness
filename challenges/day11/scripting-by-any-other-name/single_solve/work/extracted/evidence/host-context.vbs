Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_c002975b = "32:37:39:38:39:65:31:34:31:37:2d:74:73:6f:68:3d:64:69:5f:74:73:6f:68:7c:32:37:39:38:39:65:31:34:31:37:2d:6e:67:69:61:70:6d:61:63:3d:64:69:5f:6e:67:69:61:70:6d:61:63:7c:31:3d:74:6e:75:6f:63:5f:65:67:61:74:73:7c:79:72:61:6e:6f:69:74:63:69:44:2e:67:6e:69:74:70:69:72:63:53:3d:72:65:74:70:61:64:61:7c:6e:6f:69:74:61:72:75:67:69:66:6e:6f:63:5f:6e:72:75:74:65:72:2c:6e:6f:69:74:61:72:75:67:69:66:6e:6f:63:5f:65:64:6f:63:65:64:3d:73:70:65:74:73:7c:31:3d:76"
Const Codec_c002975b = "hex_colon|reverse_bytes|"

Function Load_c002975b()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_c002975b, ":")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt("&H" & parts(ByTeInDeX))
  Next
  Load_c002975b = result
End Function

Function Decode_c002975b(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(UBound(SoUrCeByTeS) - ByTeInDeX) = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_c002975b = result
End Function

Function Recover_c002975b()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = Join(Array("north", "south"), ":")

  SoUrCeByTeS = Load_c002975b()

  For PaSs = 0 To 0

    DeCoDeDByTeS = Decode_c002975b(SoUrCeByTeS)

  Next

  DeScRiPtOrTeXt = ""

  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)

    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))

  Next
  Recover_c002975b = DeScRiPtOrTeXt
End Function

Function Inspect_c002975b()
  Inspect_c002975b = Recover_c002975b()
End Function
