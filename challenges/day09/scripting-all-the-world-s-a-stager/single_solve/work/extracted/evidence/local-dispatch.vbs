Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_bd504ce4 = "118,61,49,124,115,116,101,112,115,61,108,111,99,97,116,101,95,108,111,99,97,108,44,100,105,115,112,97,116,99,104,95,112,114,111,99,101,115,115,124,97,100,97,112,116,101,114,61,87,83,99,114,105,112,116,46,83,104,101,108,108,124,115,116,97,103,101,95,99,111,117,110,116,61,50,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,97,100,102,56,97,54,55,57,97,102,124,102,105,108,101,95,112,97,116,104,61,67,58,92,85,115,101,114,115,92,80,117,98,108,105,99,92,72,117,110,116,114,101,115,115,76,97,98,92,115,116,97,103,101,45,97,100,102,56,97,54,55,57,97,102,46,100,97,116"
Const Codec_bd504ce4 = "reversed_decimal|reverse_bytes|"

Function Load_bd504ce4()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_bd504ce4, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(UBound(parts) - ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_bd504ce4 = result
End Function

Function Decode_bd504ce4(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(UBound(SoUrCeByTeS) - ByTeInDeX) = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_bd504ce4 = result
End Function

Function Recover_bd504ce4()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = (19 * 7) - 133

  SoUrCeByTeS = Load_bd504ce4()

  Select Case 1

    Case 1

      DeCoDeDByTeS = Decode_bd504ce4(SoUrCeByTeS)

    Case Else

      DeCoDeDByTeS = Array()

  End Select

  DeScRiPtOrTeXt = ""

  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)

    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))

  Next
  Recover_bd504ce4 = DeScRiPtOrTeXt
End Function

Function Inspect_bd504ce4()
  Dim fields
  fields = Split(Recover_bd504ce4(), "|")
  Inspect_bd504ce4 = Join(fields, "|")
End Function
