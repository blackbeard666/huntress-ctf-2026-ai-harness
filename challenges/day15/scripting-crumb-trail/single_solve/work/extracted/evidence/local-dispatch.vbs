Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ffca04b0 = "118|61|49|124|115|116|101|112|115|61|108|111|99|97|116|101|95|108|111|99|97|108|44|100|105|115|112|97|116|99|104|95|112|114|111|99|101|115|115|124|97|100|97|112|116|101|114|61|83|104|101|108|108|46|65|112|112|108|105|99|97|116|105|111|110|124|115|116|97|103|101|95|99|111|117|110|116|61|50|124|99|97|109|112|97|105|103|110|95|105|100|61|99|97|109|112|97|105|103|110|45|57|99|48|48|56|53|49|98|53|52|124|102|105|108|101|95|112|97|116|104|61|67|58|92|85|115|101|114|115|92|80|117|98|108|105|99|92|72|117|110|116|114|101|115|115|76|97|98|92|115|116|97|103|101|45|57|99|48|48|56|53|49|98|53|52|46|100|97|116"
Const Codec_ffca04b0 = "decimal_pipe|identity|"

Function Load_ffca04b0()
  Dim parts, result(), item5
  parts = Split(Material_ffca04b0, "|")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_ffca04b0 = result
End Function

Function Decode_ffca04b0(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5)
  Next
  Decode_ffca04b0 = result
End Function

Function Recover_ffca04b0()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = UBound(Array(3, 5, 8, 13))
  item1 = Load_ffca04b0()
  Select Case 1
    Case 1
      item2 = Decode_ffca04b0(item1)
    Case Else
      item2 = Array()
  End Select
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_ffca04b0 = item3
End Function

Sub Copy_ffca04b0(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_ffca04b0()
  Dim resultText
  Call Copy_ffca04b0(Recover_ffca04b0(), resultText)
  Inspect_ffca04b0 = resultText
End Function
