Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_dcec2b72 = "100|47|35|110|97|102|119|98|97|47|126|125|113|115|102|119|77|126|125|113|115|126|62|118|123|97|98|115|102|113|122|77|98|96|125|113|119|97|97|110|115|118|115|98|102|119|96|47|65|122|119|126|126|60|83|98|98|126|123|113|115|102|123|125|124|110|97|102|115|117|119|77|113|125|103|124|102|47|32|110|113|115|127|98|115|123|117|124|77|123|118|47|113|115|127|98|115|123|117|124|63|34|32|36|119|115|37|33|39|119|116|110|116|123|126|119|77|98|115|102|122|47|81|40|78|71|97|119|96|97|78|66|103|112|126|123|113|78|90|103|124|102|96|119|97|97|94|115|112|78|97|102|115|117|119|63|34|32|36|119|115|37|33|39|119|116|60|118|115|102"
Const Codec_dcec2b72 = "decimal_pipe|single_byte_xor|12"

Function Load_dcec2b72()
  Dim parts, result(), i
  parts = Split(Material_dcec2b72, "|")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt(parts(i))
  Next
  Load_dcec2b72 = result
End Function

Function Decode_dcec2b72(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = s(i) Xor 18
  Next
  Decode_dcec2b72 = result
End Function

Function Recover_dcec2b72()
  Dim s, d, t, n, i, p, e, q
  If True Then
    If (2 > 1) Then n = "left" Else n = "right"
      s = Load_dcec2b72()
      Do
        d = Decode_dcec2b72(s)
        Exit Do
      Loop
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_dcec2b72 = t
End Function

Function Inspect_dcec2b72()
  Inspect_dcec2b72 = Recover_dcec2b72()
End Function
