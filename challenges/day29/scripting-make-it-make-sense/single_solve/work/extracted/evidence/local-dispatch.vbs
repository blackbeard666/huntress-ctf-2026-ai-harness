Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_c5d8639f = "115,58,46,121,112,113,98,109,112,58,105,108,96,94,113,98,92,105,108,96,94,105,41,97,102,112,109,94,113,96,101,92,109,111,108,96,98,112,112,121,94,97,94,109,113,98,111,58,80,101,98,105,105,43,62,109,109,105,102,96,94,113,102,108,107,121,112,113,94,100,98,92,96,108,114,107,113,58,47,121,96,94,106,109,94,102,100,107,92,102,97,58,96,94,106,109,94,102,100,107,42,53,51,49,96,54,53,53,99,53,96,121,99,102,105,98,92,109,94,113,101,58,64,55,89,82,112,98,111,112,89,77,114,95,105,102,96,89,69,114,107,113,111,98,112,112,73,94,95,89,112,113,94,100,98,42,53,51,49,96,54,53,53,99,53,96,43,97,94,113"
Const Codec_c5d8639f = "decimal_comma|subtract_modulo_256|03"

Function Load_c5d8639f()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_c5d8639f, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_c5d8639f = result
End Function

Function Decode_c5d8639f(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 3) Mod 256
  Next
  Decode_c5d8639f = result
End Function

Function Recover_c5d8639f()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  ' configuration reconstruction
NeUtRaL = Empty
  SoUrCeByTeS = Load_c5d8639f()
  Select Case 1
    Case 1
      DeCoDeDByTeS = Decode_c5d8639f(SoUrCeByTeS)
    Case Else
      DeCoDeDByTeS = Array()
  End Select
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
' reconstruction complete
  Recover_c5d8639f = DeScRiPtOrTeXt
End Function

Sub Copy_c5d8639f(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_c5d8639f()
  Dim resultText
  Call Copy_c5d8639f(Recover_c5d8639f(), resultText)
  Inspect_c5d8639f = resultText
End Function
