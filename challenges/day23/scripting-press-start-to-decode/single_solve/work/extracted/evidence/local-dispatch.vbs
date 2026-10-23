Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_f39f9691 = "118,61,49,124,115,116,101,112,115,61,108,111,99,97,116,101,95,108,111,99,97,108,44,100,105,115,112,97,116,99,104,95,112,114,111,99,101,115,115,124,97,100,97,112,116,101,114,61,83,104,101,108,108,46,65,112,112,108,105,99,97,116,105,111,110,124,115,116,97,103,101,95,99,111,117,110,116,61,50,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,54,97,100,49,102,49,56,50,54,48,124,102,105,108,101,95,112,97,116,104,61,67,58,92,85,115,101,114,115,92,80,117,98,108,105,99,92,72,117,110,116,114,101,115,115,76,97,98,92,115,116,97,103,101,45,54,97,100,49,102,49,56,50,54,48,46,100,97,116"
Const Codec_f39f9691 = "decimal_comma|identity|"

Function Load_f39f9691()
  Dim parts, result(), v_e598
  parts = Split(Material_f39f9691, ",")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_f39f9691 = result
End Function

Function Decode_f39f9691(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598)
  Next
  Decode_f39f9691 = result
End Function

Function Recover_f39f9691()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = (19 * 7) - 133
      v_a19c = Load_f39f9691()
      For v_f602 = 0 To 0
        v_b27e = Decode_f39f9691(v_a19c)
      Next
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_f39f9691 = v_c304
End Function

Function Inspect_f39f9691()
  Inspect_f39f9691 = Recover_f39f9691()
End Function
