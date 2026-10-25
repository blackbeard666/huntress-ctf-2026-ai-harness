Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_5d620e98 = "116|120|116|46|100|56|57|50|98|48|53|50|45|82|69|86|79|67|69|82|61|101|109|97|110|95|101|116|111|110|124|100|101|107|99|111|108|46|100|102|48|97|101|46|61|110|111|105|115|110|101|116|120|101|124|55|51|50|57|52|97|56|49|57|50|45|110|103|105|97|112|109|97|99|61|100|105|95|110|103|105|97|112|109|97|99|124|50|61|116|110|117|111|99|95|101|103|97|116|115|124|116|99|101|106|98|79|109|101|116|115|121|83|101|108|105|70|46|103|110|105|116|112|105|114|99|83|61|114|101|116|112|97|100|97|124|101|116|111|110|95|121|114|101|118|111|99|101|114|95|101|116|105|114|119|44|116|110|101|116|110|111|99|95|109|114|111|102|115|110|97|114|116|44|115|116|101|103|114|97|116|95|101|116|97|114|101|109|117|110|101|61|115|112|101|116|115|124|49|61|118"
Const Codec_5d620e98 = "decimal_pipe|reverse_bytes|"

Function Load_5d620e98()
  Dim parts, result(), i
  parts = Split(Material_5d620e98, "|")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt(parts(i))
  Next
  Load_5d620e98 = result
End Function

Function Decode_5d620e98(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(UBound(s) - i) = s(i)
  Next
  Decode_5d620e98 = result
End Function

Function Recover_5d620e98()
  Dim s, d, t, n, i, p, e, q
  ' configuration reconstruction
n = (19 * 7) - 133
  s = Load_5d620e98()
  On Error Resume Next
  d = Decode_5d620e98(s)
  e = Err.Number
  q = Err.Description
  On Error GoTo 0
  If e <> 0 Then Err.Raise e, "HuntressFixture", q
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
' reconstruction complete
  Recover_5d620e98 = t
End Function

Sub Copy_5d620e98(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_5d620e98()
  Dim resultText
  Call Copy_5d620e98(Recover_5d620e98(), resultText)
  Inspect_5d620e98 = resultText
End Function
