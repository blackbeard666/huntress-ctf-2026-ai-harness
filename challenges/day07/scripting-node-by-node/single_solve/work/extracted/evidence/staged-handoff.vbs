Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_91c6829f = "117|60|48|123|114|115|100|111|114|60|96|98|112|116|104|113|100|94|113|100|108|110|115|100|43|118|113|104|115|100|94|101|104|107|100|43|99|104|114|111|96|115|98|103|94|111|113|110|98|100|114|114|43|103|96|109|99|110|101|101|94|114|98|113|104|111|115|123|96|99|96|111|115|100|113|60|76|104|98|113|110|114|110|101|115|45|87|76|75|71|83|83|79|123|114|115|96|102|100|94|98|110|116|109|115|60|51|123|98|96|108|111|96|104|102|109|94|104|99|60|98|96|108|111|96|104|102|109|44|99|96|50|98|55|48|97|56|54|55|123|116|113|107|60|103|115|115|111|114|57|46|46|99|96|50|98|55|48|97|56|54|55|45|100|119|96|108|111|107|100|45|104|109|117|96|107|104|99|46|47|50|50|49|49|48|96|54|45|99|96|115|123|116|114|100|113|94|96|102|100|109|115|60|71|116|109|115|113|100|114|114|75|96|97|46|99|96|50|98|55|48|97|56|54|55|123|101|104|107|100|94|111|96|115|103|60|66|57|91|84|114|100|113|114|91|79|116|97|107|104|98|91|71|116|109|115|113|100|114|114|75|96|97|91|114|115|96|102|100|44|99|96|50|98|55|48|97|56|54|55|45|99|96|115|123|113|100|102|104|114|115|113|120|94|111|96|115|103|60|71|74|66|84|91|82|110|101|115|118|96|113|100|91|71|116|109|115|113|100|114|114|75|96|97|91|67|104|114|111|110|114|96|97|107|100|91|99|96|50|98|55|48|97|56|54|55|123|109|100|119|115|94|114|115|96|102|100|60|113|100|114|110|116|113|98|100|44|114|96|108|111|107|100|45|111|114|48"
Const Codec_91c6829f = "decimal_pipe|subtract_modulo_256|01"

Function Load_91c6829f()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_91c6829f, "|")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_91c6829f = result
End Function

Function Decode_91c6829f(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 1) Mod 256
  Next
  Decode_91c6829f = result
End Function

Function Recover_91c6829f()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = UBound(Array(3, 5, 8, 13))
  SoUrCeByTeS = Load_91c6829f()
  On Error Resume Next
  DeCoDeDByTeS = Decode_91c6829f(SoUrCeByTeS)
  ErRoRnUmBeR = Err.Number
  ErRoRdEsCrIpTiOn = Err.Description
  On Error GoTo 0
  If ErRoRnUmBeR <> 0 Then Err.Raise ErRoRnUmBeR, "HuntressFixture", ErRoRdEsCrIpTiOn
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
  Recover_91c6829f = DeScRiPtOrTeXt
End Function

Sub Copy_91c6829f(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_91c6829f()
  Dim resultText
  Call Copy_91c6829f(Recover_91c6829f(), resultText)
  Inspect_91c6829f = resultText
End Function
