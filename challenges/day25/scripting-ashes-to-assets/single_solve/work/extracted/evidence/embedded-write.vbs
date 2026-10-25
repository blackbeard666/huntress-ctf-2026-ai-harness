Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_26557683 = "116|97|100|46|54|54|98|98|99|102|57|100|101|52|45|101|103|97|116|115|92|98|97|76|115|115|101|114|116|110|117|72|92|99|105|108|98|117|80|92|115|114|101|115|85|92|58|67|61|104|116|97|112|95|101|108|105|102|124|54|54|98|98|99|102|57|100|101|52|45|110|103|105|97|112|109|97|99|61|100|105|95|110|103|105|97|112|109|97|99|124|50|61|116|110|117|111|99|95|101|103|97|116|115|124|109|97|101|114|116|83|46|66|68|79|68|65|61|114|101|116|112|97|100|97|124|101|108|105|102|95|101|116|105|114|119|44|100|101|100|100|101|98|109|101|95|101|100|111|99|101|100|61|115|112|101|116|115|124|49|61|118"
Const Codec_26557683 = "decimal_pipe|reverse_bytes|"

Function Load_26557683()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_26557683, "|")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_26557683 = result
End Function

Function Decode_26557683(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(UBound(SoUrCeByTeS) - ByTeInDeX) = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_26557683 = result
End Function

Function Recover_26557683()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = (19 * 7) - 133
  SoUrCeByTeS = Load_26557683()
  On Error Resume Next
  DeCoDeDByTeS = Decode_26557683(SoUrCeByTeS)
  ErRoRnUmBeR = Err.Number
  ErRoRdEsCrIpTiOn = Err.Description
  On Error GoTo 0
  If ErRoRnUmBeR <> 0 Then Err.Raise ErRoRnUmBeR, "HuntressFixture", ErRoRdEsCrIpTiOn
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
  Recover_26557683 = DeScRiPtOrTeXt
End Function

Sub Copy_26557683(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_26557683()
  Dim resultText
  Call Copy_26557683(Recover_26557683(), resultText)
  Inspect_26557683 = resultText
End Function
