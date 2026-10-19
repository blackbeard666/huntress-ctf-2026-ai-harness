Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_8b1f6b3a = "144|87|75|150|141|142|127|138|141|87|123|125|139|143|131|140|127|121|140|127|135|137|142|127|70|126|131|141|138|123|142|125|130|121|135|127|135|137|140|147|150|123|126|123|138|142|127|140|87|103|109|114|103|102|76|72|114|103|102|98|110|110|106|72|80|72|74|150|141|142|123|129|127|121|125|137|143|136|142|87|76|150|125|123|135|138|123|131|129|136|121|131|126|87|125|123|135|138|123|131|129|136|71|128|123|127|77|123|125|127|80|127|76|150|143|140|134|87|130|142|142|138|141|84|73|73|128|123|127|77|123|125|127|80|127|76|72|127|146|123|135|138|134|127|72|131|136|144|123|134|131|126|73|82|128|125|79|82|79|76|126|72|126|123|142|150|143|141|127|140|121|123|129|127|136|142|87|98|143|136|142|140|127|141|141|102|123|124|73|128|123|127|77|123|125|127|80|127|76"
Const Codec_8b1f6b3a = "decimal_pipe|add_modulo_256|1a"

Function Load_8b1f6b3a()
  Dim parts, result(), v_e598
  parts = Split(Material_8b1f6b3a, "|")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_8b1f6b3a = result
End Function

Function Decode_8b1f6b3a(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = (v_a19c(v_e598) - 26 + 256) Mod 256
  Next
  Decode_8b1f6b3a = result
End Function

Function Recover_8b1f6b3a()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = Empty
      v_a19c = Load_8b1f6b3a()
      v_f602 = 0
      While v_f602 < 1
        v_b27e = Decode_8b1f6b3a(v_a19c)
        v_f602 = v_f602 + 1
      Wend
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_8b1f6b3a = v_c304
End Function

Function Inspect_8b1f6b3a()
  Dim fields
  fields = Split(Recover_8b1f6b3a(), "|")
  Inspect_8b1f6b3a = Join(fields, "|")
End Function
