Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_0b34a5da = "117,96,101,47,99,52,53,48,99,57,54,101,56,50,44,100,102,96,117,114,93,99,96,77,114,114,100,115,117,111,116,73,93,98,104,109,99,116,81,93,114,115,100,114,84,93,59,66,60,105,117,96,113,94,100,109,104,103,125,99,52,53,48,99,57,54,101,56,50,44,111,102,104,96,113,108,96,98,60,101,104,94,111,102,104,96,113,108,96,98,125,51,60,117,111,116,110,98,94,100,102,96,117,114,125,111,110,104,117,96,98,104,109,113,113,64,47,109,109,100,105,82,60,115,100,117,113,96,101,96,125,114,114,100,98,110,115,113,94,105,98,117,96,113,114,104,101,45,109,96,98,110,109,94,100,117,96,98,110,109,60,114,113,100,117,114,125,48,60,119"
Const Codec_0b34a5da = "reversed_decimal|single_byte_xor|01"

Function Load_0b34a5da()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_0b34a5da, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(UBound(parts) - ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_0b34a5da = result
End Function

Function Decode_0b34a5da(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor 1
  Next
  Decode_0b34a5da = result
End Function

Function Recover_0b34a5da()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If (2 > 1) Then NeUtRaL = "left" Else NeUtRaL = "right"
  SoUrCeByTeS = Load_0b34a5da()
  On Error Resume Next
  DeCoDeDByTeS = Decode_0b34a5da(SoUrCeByTeS)
  ErRoRnUmBeR = Err.Number
  ErRoRdEsCrIpTiOn = Err.Description
  On Error GoTo 0
  If ErRoRnUmBeR <> 0 Then Err.Raise ErRoRnUmBeR, "HuntressFixture", ErRoRdEsCrIpTiOn
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
  Recover_0b34a5da = DeScRiPtOrTeXt
End Function

Sub Copy_0b34a5da(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_0b34a5da()
  Dim resultText
  Call Copy_0b34a5da(Recover_0b34a5da(), resultText)
  Inspect_0b34a5da = resultText
End Function
