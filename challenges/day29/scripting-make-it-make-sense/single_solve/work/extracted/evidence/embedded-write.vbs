Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_d6c99251 = "138,119,122,68,121,78,121,119,71,76,121,72,79,71,67,123,125,119,138,137,114,120,119,98,137,137,123,136,138,132,139,94,114,121,127,130,120,139,102,114,137,136,123,137,107,114,80,89,83,126,138,119,134,117,123,130,127,124,146,121,78,121,119,71,76,121,72,79,71,67,132,125,127,119,134,131,119,121,83,122,127,117,132,125,127,119,134,131,119,121,146,72,83,138,132,139,133,121,117,123,125,119,138,137,146,131,119,123,136,138,105,68,88,90,101,90,87,83,136,123,138,134,119,122,119,146,123,130,127,124,117,123,138,127,136,141,66,122,123,122,122,123,120,131,123,117,123,122,133,121,123,122,83,137,134,123,138,137,146,71,83,140"
Const Codec_d6c99251 = "reversed_decimal|add_modulo_256|16"

Function Load_d6c99251()
  Dim parts, result(), v_e598
  parts = Split(Material_d6c99251, ",")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(UBound(parts) - v_e598) = CInt(parts(v_e598))
  Next
  Load_d6c99251 = result
End Function

Function Decode_d6c99251(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = (v_a19c(v_e598) - 22 + 256) Mod 256
  Next
  Decode_d6c99251 = result
End Function

Function Recover_d6c99251()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = (19 * 7) - 133
      v_a19c = Load_d6c99251()
      v_f602 = 0
      While v_f602 < 1
        v_b27e = Decode_d6c99251(v_a19c)
        v_f602 = v_f602 + 1
      Wend
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_d6c99251 = v_c304
End Function

Function Inspect_d6c99251()
  Inspect_d6c99251 = Recover_d6c99251()
End Function
