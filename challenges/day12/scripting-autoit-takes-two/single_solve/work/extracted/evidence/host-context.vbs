Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_e039fe21 = "9,88,95,88,88,90,12,94,8,13,22,79,72,84,83,6,95,82,100,79,72,84,83,71,9,88,95,88,88,90,12,94,8,13,22,85,92,82,90,75,86,90,88,6,95,82,100,85,92,82,90,75,86,90,88,71,10,6,79,85,78,84,88,100,94,92,90,79,72,71,66,73,90,85,84,82,79,88,82,127,21,92,85,82,79,75,82,73,88,104,6,73,94,79,75,90,95,90,71,85,84,82,79,90,73,78,92,82,93,85,84,88,100,85,73,78,79,94,73,23,85,84,82,79,90,73,78,92,82,93,85,84,88,100,94,95,84,88,94,95,6,72,75,94,79,72,71,10,6,77"
Const Codec_e039fe21 = "decimal_comma|reverse_then_xor|3b"

Function Load_e039fe21()
  Dim parts, result(), v_e598
  parts = Split(Material_e039fe21, ",")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_e039fe21 = result
End Function

Function Decode_e039fe21(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(UBound(v_a19c) - v_e598) = v_a19c(v_e598) Xor 59
  Next
  Decode_e039fe21 = result
End Function

Function Recover_e039fe21()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = LCase(UCase("Host"))
  v_a19c = Load_e039fe21()
  Do
    v_b27e = Decode_e039fe21(v_a19c)
    Exit Do
  Loop
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_e039fe21 = v_c304
End Function

Function Inspect_e039fe21()
  Dim fields
  fields = Split(Recover_e039fe21(), "|")
  Inspect_e039fe21 = Join(fields, "|")
End Function
