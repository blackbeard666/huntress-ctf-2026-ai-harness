Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_cd11e4b4 = "118|61|49|124|115|116|101|112|115|61|97|99|113|117|105|114|101|95|114|101|109|111|116|101|44|119|114|105|116|101|95|102|105|108|101|44|100|105|115|112|97|116|99|104|95|112|114|111|99|101|115|115|44|104|97|110|100|111|102|102|95|115|99|114|105|112|116|124|97|100|97|112|116|101|114|61|77|105|99|114|111|115|111|102|116|46|88|77|76|72|84|84|80|124|115|116|97|103|101|95|99|111|117|110|116|61|52|124|99|97|109|112|97|105|103|110|95|105|100|61|99|97|109|112|97|105|103|110|45|51|97|99|57|99|56|50|51|57|55|124|117|114|108|61|104|116|116|112|115|58|47|47|51|97|99|57|99|56|50|51|57|55|46|101|120|97|109|112|108|101|46|105|110|118|97|108|105|100|47|97|99|51|53|100|52|54|53|46|100|97|116|124|117|115|101|114|95|97|103|101|110|116|61|72|117|110|116|114|101|115|115|76|97|98|47|51|97|99|57|99|56|50|51|57|55|124|102|105|108|101|95|112|97|116|104|61|67|58|92|85|115|101|114|115|92|80|117|98|108|105|99|92|72|117|110|116|114|101|115|115|76|97|98|92|115|116|97|103|101|45|51|97|99|57|99|56|50|51|57|55|46|100|97|116|124|114|101|103|105|115|116|114|121|95|112|97|116|104|61|72|75|67|85|92|83|111|102|116|119|97|114|101|92|72|117|110|116|114|101|115|115|76|97|98|92|68|105|115|112|111|115|97|98|108|101|92|51|97|99|57|99|56|50|51|57|55|124|110|101|120|116|95|115|116|97|103|101|61|108|111|99|97|108|45|100|105|115|112|97|116|99|104|46|118|98|115"
Const Codec_cd11e4b4 = "decimal_pipe|identity|"

Function Load_cd11e4b4()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_cd11e4b4, "|")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_cd11e4b4 = result
End Function

Function Decode_cd11e4b4(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_cd11e4b4 = result
End Function

Function Recover_cd11e4b4()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  ' configuration reconstruction
NeUtRaL = Join(Array("north", "south"), ":")
  SoUrCeByTeS = Load_cd11e4b4()
  Do
    DeCoDeDByTeS = Decode_cd11e4b4(SoUrCeByTeS)
    Exit Do
  Loop
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
' reconstruction complete
  Recover_cd11e4b4 = DeScRiPtOrTeXt
End Function

Function Inspect_cd11e4b4()
  Inspect_cd11e4b4 = Recover_cd11e4b4()
End Function
