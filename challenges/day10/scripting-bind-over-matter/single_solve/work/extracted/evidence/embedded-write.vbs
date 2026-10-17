Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_b01e8578 = "cb:de:db:91:86:8a:8e:87:86:88:8c:dc:d9:89:92:da:d8:de:cb:cc:e3:dd:de:f3:cc:cc:da:cd:cb:d1:ca:f7:e3:dc:d6:d3:dd:ca:ef:e3:cc:cd:da:cc:ea:e3:85:fc:82:d7:cb:de:cf:e0:da:d3:d6:d9:c3:86:8a:8e:87:86:88:8c:dc:d9:89:92:d1:d8:d6:de:cf:d2:de:dc:82:db:d6:e0:d1:d8:d6:de:cf:d2:de:dc:c3:8d:82:cb:d1:ca:d0:dc:e0:da:d8:de:cb:cc:c3:cb:dc:da:d5:dd:f0:d2:da:cb:cc:c6:ec:da:d3:d6:f9:91:d8:d1:d6:cb:cf:d6:cd:dc:ec:82:cd:da:cb:cf:de:db:de:c3:da:d3:d6:d9:e0:da:cb:d6:cd:c8:93:db:da:db:db:da:dd:d2:da:e0:da:db:d0:dc:da:db:82:cc:cf:da:cb:cc:c3:8e:82:c9"
Const Codec_b01e8578 = "hex_colon|reverse_then_xor|bf"

Function Load_b01e8578()
  Dim parts, result(), v_e598
  parts = Split(Material_b01e8578, ":")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt("&H" & parts(v_e598))
  Next
  Load_b01e8578 = result
End Function

Function Decode_b01e8578(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(UBound(v_a19c) - v_e598) = v_a19c(v_e598) Xor 191
  Next
  Decode_b01e8578 = result
End Function

Function Recover_b01e8578()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = (19 * 7) - 133

  v_a19c = Load_b01e8578()

  Select Case 1

    Case 1

      v_b27e = Decode_b01e8578(v_a19c)

    Case Else

      v_b27e = Array()

  End Select

  v_c304 = ""

  For v_e598 = 0 To UBound(v_b27e)

    v_c304 = v_c304 & Chr(v_b27e(v_e598))

  Next
  Recover_b01e8578 = v_c304
End Function

Function Inspect_b01e8578()
  Inspect_b01e8578 = Recover_b01e8578()
End Function
