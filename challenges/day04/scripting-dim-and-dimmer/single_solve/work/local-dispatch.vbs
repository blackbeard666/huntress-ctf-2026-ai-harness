Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_df7cb6fa = "114|79|126|2|113|5|96|16|99|94|50|93|62|95|43|78|17|125|18|113|16|124|80|52|93|46|94|63|75|40|64|31|111|29|114|17|116|7|116|8|105|13|108|28|104|13|127|66|17|121|28|112|28|50|115|3|115|31|118|21|116|0|105|6|104|20|103|19|114|21|112|47|76|35|86|56|76|113|67|63|92|61|80|32|65|40|79|33|126|23|115|78|45|76|33|81|48|89|62|80|125|24|33|69|32|20|34|22|116|66|32|92|58|83|63|90|5|117|20|96|8|53|118|76|16|69|54|83|33|82|14|94|43|73|37|76|47|115|59|78|32|84|38|67|48|67|15|110|12|80|35|87|54|81|52|25|124|69|33|68|112|70|114|16|38|68|106|14|111|27"
Const Codec_df7cb6fa = "decimal_pipe|rolling_xor|04"

Function Load_df7cb6fa()
  Dim parts, result(), v_e598
  parts = Split(Material_df7cb6fa, "|")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_df7cb6fa = result
End Function

Function Decode_df7cb6fa(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  previous = 4
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor previous
    previous = v_a19c(v_e598)
  Next
  Decode_df7cb6fa = result
End Function

Function Recover_df7cb6fa()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = (19 * 7) - 133

  v_a19c = Load_df7cb6fa()

  v_b27e = Decode_df7cb6fa(v_a19c)

  v_c304 = ""

  For v_e598 = 0 To UBound(v_b27e)

    v_c304 = v_c304 & Chr(v_b27e(v_e598))

  Next
  Recover_df7cb6fa = v_c304
End Function

Function Inspect_df7cb6fa()
  Dim fields
  fields = Split(Recover_df7cb6fa(), "|")
  Inspect_df7cb6fa = Join(fields, "|")
End Function
