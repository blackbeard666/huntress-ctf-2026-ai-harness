Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_f39574b9 = "116|97|100|46|100|55|98|53|56|54|98|52|50|99|45|101|103|97|116|115|92|98|97|76|115|115|101|114|116|110|117|72|92|99|105|108|98|117|80|92|115|114|101|115|85|92|58|67|61|104|116|97|112|95|101|108|105|102|124|100|55|98|53|56|54|98|52|50|99|47|98|97|76|115|115|101|114|116|110|117|72|61|116|110|101|103|97|95|114|101|115|117|124|116|97|100|46|51|102|101|56|101|56|55|102|47|100|105|108|97|118|110|105|46|101|108|112|109|97|120|101|46|100|55|98|53|56|54|98|52|50|99|47|47|58|115|112|116|116|104|61|108|114|117|124|100|55|98|53|56|54|98|52|50|99|45|110|103|105|97|112|109|97|99|61|100|105|95|110|103|105|97|112|109|97|99|124|50|61|116|110|117|111|99|95|101|103|97|116|115|124|49|46|53|46|116|115|101|117|113|101|82|112|116|116|72|110|105|87|46|112|116|116|72|110|105|87|61|114|101|116|112|97|100|97|124|101|108|105|102|95|101|116|105|114|119|44|101|116|111|109|101|114|95|101|114|105|117|113|99|97|61|115|112|101|116|115|124|49|61|118"
Const Codec_f39574b9 = "decimal_pipe|reverse_bytes|"

Function Load_f39574b9()
  Dim parts, result(), v_e598
  parts = Split(Material_f39574b9, "|")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_f39574b9 = result
End Function

Function Decode_f39574b9(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(UBound(v_a19c) - v_e598) = v_a19c(v_e598)
  Next
  Decode_f39574b9 = result
End Function

Function Recover_f39574b9()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    If (2 > 1) Then v_d41a = "left" Else v_d41a = "right"
      v_a19c = Load_f39574b9()
      Do
        v_b27e = Decode_f39574b9(v_a19c)
        Exit Do
      Loop
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_f39574b9 = v_c304
End Function

Sub Copy_f39574b9(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_f39574b9()
  Dim resultText
  Call Copy_f39574b9(Recover_f39574b9(), resultText)
  Inspect_f39574b9 = resultText
End Function
