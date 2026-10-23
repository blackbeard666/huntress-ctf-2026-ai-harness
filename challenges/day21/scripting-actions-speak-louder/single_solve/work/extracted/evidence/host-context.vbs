Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_e89bb1fa = "c6:9d:c1:92:90:9d:97:93:c4:97:88:d1:d6:ca:cd:98:c1:cc:fa:d1:d6:ca:cd:d9:c6:9d:c1:92:90:9d:97:93:c4:97:88:cb:c2:cc:c4:d5:c8:c4:c6:98:c1:cc:fa:cb:c2:cc:c4:d5:c8:c4:c6:d9:94:98:d1:cb:d0:ca:c6:fa:c0:c2:c4:d1:d6:d9:d1:c6:c0:cf:c7:ea:c8:c0:d1:d6:dc:f6:c0:c9:cc:e3:8b:c2:cb:cc:d1:d5:cc:d7:c6:f6:98:d7:c0:d1:d5:c4:c1:c4:d9:cb:ca:cc:d1:c4:d7:d0:c2:cc:c3:cb:ca:c6:fa:cb:d7:d0:d1:c0:d7:89:cb:ca:cc:d1:c4:d7:d0:c2:cc:c3:cb:ca:c6:fa:c0:c1:ca:c6:c0:c1:98:d6:d5:c0:d1:d6:d9:94:98:d3"
Const Codec_e89bb1fa = "hex_colon|reverse_then_xor|a5"

Function Load_e89bb1fa()
  Dim parts, result(), v_e598
  parts = Split(Material_e89bb1fa, ":")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt("&H" & parts(v_e598))
  Next
  Load_e89bb1fa = result
End Function

Function Decode_e89bb1fa(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(UBound(v_a19c) - v_e598) = v_a19c(v_e598) Xor 165
  Next
  Decode_e89bb1fa = result
End Function

Function Recover_e89bb1fa()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = LCase(UCase("Host"))

  v_a19c = Load_e89bb1fa()

  On Error Resume Next

  v_b27e = Decode_e89bb1fa(v_a19c)

  v_a702 = Err.Number

  v_b803 = Err.Description

  On Error GoTo 0

  If v_a702 <> 0 Then Err.Raise v_a702, "HuntressFixture", v_b803

  v_c304 = ""

  For v_e598 = 0 To UBound(v_b27e)

    v_c304 = v_c304 & Chr(v_b27e(v_e598))

  Next
  Recover_e89bb1fa = v_c304
End Function

Function Inspect_e89bb1fa()
  Inspect_e89bb1fa = Recover_e89bb1fa()
End Function
