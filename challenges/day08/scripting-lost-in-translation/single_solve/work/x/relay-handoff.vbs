Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_fb42cd3d = "128|71|59|134|125|126|111|122|125|71|107|109|123|127|115|124|111|105|124|111|119|121|126|111|54|129|124|115|126|111|105|112|115|118|111|54|110|115|125|122|107|126|109|114|105|122|124|121|109|111|125|125|54|114|107|120|110|121|112|112|105|125|109|124|115|122|126|134|107|110|107|122|126|111|124|71|87|115|109|124|121|125|121|112|126|56|98|87|86|82|94|94|90|134|125|126|107|113|111|105|109|121|127|120|126|71|62|134|109|107|119|122|107|115|113|120|105|115|110|71|109|107|119|122|107|115|113|120|55|65|59|58|65|107|66|65|58|62|62|134|127|124|118|71|114|126|126|122|125|68|57|57|65|59|58|65|107|66|65|58|62|62|56|111|130|107|119|122|118|111|56|115|120|128|107|118|115|110|57|59|112|61|61|112|110|59|66|56|110|107|126|134|127|125|111|124|105|107|113|111|120|126|71|82|127|120|126|124|111|125|125|86|107|108|57|65|59|58|65|107|66|65|58|62|62|134|112|115|118|111|105|122|107|126|114|71|77|68|102|95|125|111|124|125|102|90|127|108|118|115|109|102|82|127|120|126|124|111|125|125|86|107|108|102|125|126|107|113|111|55|65|59|58|65|107|66|65|58|62|62|56|110|107|126|134|124|111|113|115|125|126|124|131|105|122|107|126|114|71|82|85|77|95|102|93|121|112|126|129|107|124|111|102|82|127|120|126|124|111|125|125|86|107|108|102|78|115|125|122|121|125|107|108|118|111|102|65|59|58|65|107|66|65|58|62|62|134|120|111|130|126|105|125|126|107|113|111|71|118|121|109|107|118|55|110|115|125|122|107|126|109|114|56|128|108|125"
Const Codec_fb42cd3d = "decimal_pipe|add_modulo_256|0a"

Function Load_fb42cd3d()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_fb42cd3d, "|")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_fb42cd3d = result
End Function

Function Decode_fb42cd3d(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) - 10 + 256) Mod 256
  Next
  Decode_fb42cd3d = result
End Function

Function Recover_fb42cd3d()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = (19 * 7) - 133
      SoUrCeByTeS = Load_fb42cd3d()
      Do
        DeCoDeDByTeS = Decode_fb42cd3d(SoUrCeByTeS)
        Exit Do
      Loop
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_fb42cd3d = DeScRiPtOrTeXt
End Function

Function Inspect_fb42cd3d()
  Inspect_fb42cd3d = Recover_fb42cd3d()
End Function
