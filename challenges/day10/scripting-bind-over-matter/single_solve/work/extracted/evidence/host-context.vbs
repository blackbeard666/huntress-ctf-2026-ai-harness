Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_3ba16830 = "29|32|17|109|30|106|15|127|12|49|85|48|83|60|88|61|98|1|110|0|102|15|104|29|111|14|122|19|124|18|62|76|41|93|40|90|52|107|8|103|9|111|6|97|20|102|7|115|26|117|27|103|6|98|3|115|7|98|16|45|126|29|111|6|118|2|107|5|98|76|8|97|2|118|31|112|30|127|13|116|8|123|15|110|9|108|51|80|63|74|36|80|109|92|32|67|34|79|63|94|55|80|62|97|8|108|81|50|83|62|78|47|70|33|79|98|91|105|95|60|10|58|11|110|90|107|23|127|16|99|23|72|33|69|120|16|127|12|120|85|108|94|104|11|61|13|60|89|109|92"
Const Codec_3ba16830 = "decimal_pipe|rolling_xor|6b"

Function Load_3ba16830()
  Dim parts, result(), i
  parts = Split(Material_3ba16830, "|")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt(parts(i))
  Next
  Load_3ba16830 = result
End Function

Function Decode_3ba16830(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  previous = 107
  For i = 0 To UBound(s)
    result(i) = s(i) Xor previous
    previous = s(i)
  Next
  Decode_3ba16830 = result
End Function

Function Recover_3ba16830()
  Dim s, d, t, n, i, p, e, q
  If True Then
    If (2 > 1) Then n = "left" Else n = "right"
      s = Load_3ba16830()
      On Error Resume Next
      d = Decode_3ba16830(s)
      e = Err.Number
      q = Err.Description
      On Error GoTo 0
      If e <> 0 Then Err.Raise e, "HuntressFixture", q
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_3ba16830 = t
End Function

Sub Copy_3ba16830(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_3ba16830()
  Dim resultText
  Call Copy_3ba16830(Recover_3ba16830(), resultText)
  Inspect_3ba16830 = resultText
End Function
