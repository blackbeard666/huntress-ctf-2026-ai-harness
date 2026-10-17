Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_77fbacc5 = "118|61|49|124|115|116|101|112|115|61|97|99|113|117|105|114|101|95|114|101|109|111|116|101|44|119|114|105|116|101|95|102|105|108|101|124|97|100|97|112|116|101|114|61|77|105|99|114|111|115|111|102|116|46|88|77|76|72|84|84|80|124|115|116|97|103|101|95|99|111|117|110|116|61|50|124|99|97|109|112|97|105|103|110|95|105|100|61|99|97|109|112|97|105|103|110|45|102|50|55|56|56|52|97|97|101|51|124|117|114|108|61|104|116|116|112|115|58|47|47|102|50|55|56|56|52|97|97|101|51|46|101|120|97|109|112|108|101|46|105|110|118|97|108|105|100|47|53|49|101|51|49|101|57|100|46|100|97|116|124|117|115|101|114|95|97|103|101|110|116|61|72|117|110|116|114|101|115|115|76|97|98|47|102|50|55|56|56|52|97|97|101|51|124|102|105|108|101|95|112|97|116|104|61|67|58|92|85|115|101|114|115|92|80|117|98|108|105|99|92|72|117|110|116|114|101|115|115|76|97|98|92|115|116|97|103|101|45|102|50|55|56|56|52|97|97|101|51|46|100|97|116"
Const Codec_77fbacc5 = "decimal_pipe|identity|"

Function Load_77fbacc5()
  Dim parts, result(), item5
  parts = Split(Material_77fbacc5, "|")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_77fbacc5 = result
End Function

Function Decode_77fbacc5(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5)
  Next
  Decode_77fbacc5 = result
End Function

Function Recover_77fbacc5()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If (2 > 1) Then item4 = "left" Else item4 = "right"
  item1 = Load_77fbacc5()
  For item6 = 0 To 0
    item2 = Decode_77fbacc5(item1)
  Next
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_77fbacc5 = item3
End Function

Sub Copy_77fbacc5(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_77fbacc5()
  Dim resultText
  Call Copy_77fbacc5(Recover_77fbacc5(), resultText)
  Inspect_77fbacc5 = resultText
End Function
