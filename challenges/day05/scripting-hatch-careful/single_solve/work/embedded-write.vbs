Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_170ed1c9 = "99,80,83,29,37,39,40,81,34,33,40,35,31,36,28,84,86,80,99,98,75,81,80,59,98,98,84,97,99,93,100,55,75,82,88,91,81,100,63,75,98,97,84,98,68,75,41,50,44,87,99,80,95,78,84,91,88,85,107,37,39,40,81,34,33,40,35,31,36,28,93,86,88,80,95,92,80,82,44,83,88,78,93,86,88,80,95,92,80,82,107,33,44,99,93,100,94,82,78,84,86,80,99,98,107,99,82,84,89,81,62,92,84,99,98,104,66,84,91,88,53,29,86,93,88,99,95,88,97,82,66,44,97,84,99,95,80,83,80,107,84,91,88,85,78,84,99,88,97,102,27,83,84,83,83,84,81,92,84,78,84,83,94,82,84,83,44,98,95,84,99,98,107,32,44,101"
Const Codec_170ed1c9 = "reversed_decimal|subtract_modulo_256|11"

Function Load_170ed1c9()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_170ed1c9, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(UBound(parts) - ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_170ed1c9 = result
End Function

Function Decode_170ed1c9(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 17) Mod 256
  Next
  Decode_170ed1c9 = result
End Function

Function Recover_170ed1c9()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If (2 > 1) Then NeUtRaL = "left" Else NeUtRaL = "right"
  SoUrCeByTeS = Load_170ed1c9()
  On Error Resume Next
  DeCoDeDByTeS = Decode_170ed1c9(SoUrCeByTeS)
  ErRoRnUmBeR = Err.Number
  ErRoRdEsCrIpTiOn = Err.Description
  On Error GoTo 0
  If ErRoRnUmBeR <> 0 Then Err.Raise ErRoRnUmBeR, "HuntressFixture", ErRoRdEsCrIpTiOn
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
  Recover_170ed1c9 = DeScRiPtOrTeXt
End Function

Sub Copy_170ed1c9(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_170ed1c9()
  Dim resultText
  Call Copy_170ed1c9(Recover_170ed1c9(), resultText)
  Inspect_170ed1c9 = resultText
End Function
