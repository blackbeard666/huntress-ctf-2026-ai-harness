Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_260ba521 = "116|97|100|46|49|102|50|53|51|97|54|100|51|102|45|101|103|97|116|115|92|98|97|76|115|115|101|114|116|110|117|72|92|99|105|108|98|117|80|92|115|114|101|115|85|92|58|67|61|104|116|97|112|95|101|108|105|102|124|49|102|50|53|51|97|54|100|51|102|45|110|103|105|97|112|109|97|99|61|100|105|95|110|103|105|97|112|109|97|99|124|50|61|116|110|117|111|99|95|101|103|97|116|115|124|109|97|101|114|116|83|46|66|68|79|68|65|61|114|101|116|112|97|100|97|124|101|108|105|102|95|101|116|105|114|119|44|100|101|100|100|101|98|109|101|95|101|100|111|99|101|100|61|115|112|101|116|115|124|49|61|118"
Const Codec_260ba521 = "decimal_pipe|reverse_bytes|"

Function Load_260ba521()
  Dim parts, result(), v_e598
  parts = Split(Material_260ba521, "|")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_260ba521 = result
End Function

Function Decode_260ba521(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(UBound(v_a19c) - v_e598) = v_a19c(v_e598)
  Next
  Decode_260ba521 = result
End Function

Function Recover_260ba521()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = UBound(Array(3, 5, 8, 13))

  v_a19c = Load_260ba521()

  Do

    v_b27e = Decode_260ba521(v_a19c)

    Exit Do

  Loop

  v_c304 = ""

  For v_e598 = 0 To UBound(v_b27e)

    v_c304 = v_c304 & Chr(v_b27e(v_e598))

  Next
  Recover_260ba521 = v_c304
End Function

Function Inspect_260ba521()
  Inspect_260ba521 = Recover_260ba521()
End Function
