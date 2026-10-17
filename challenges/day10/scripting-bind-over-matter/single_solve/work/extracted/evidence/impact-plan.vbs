Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_2802ccd8 = "74:78:74:2e:36:38:61:38:66:36:37:34:2d:52:45:56:4f:43:45:52:3d:65:6d:61:6e:5f:65:74:6f:6e:7c:64:65:6b:63:6f:6c:2e:66:62:36:63:66:2e:3d:6e:6f:69:73:6e:65:74:78:65:7c:39:31:34:34:38:32:66:64:33:30:2d:6e:67:69:61:70:6d:61:63:3d:64:69:5f:6e:67:69:61:70:6d:61:63:7c:32:3d:74:6e:75:6f:63:5f:65:67:61:74:73:7c:6d:61:65:72:74:53:2e:42:44:4f:44:41:3d:72:65:74:70:61:64:61:7c:65:74:6f:6e:5f:79:72:65:76:6f:63:65:72:5f:65:74:69:72:77:2c:74:6e:65:74:6e:6f:63:5f:6d:72:6f:66:73:6e:61:72:74:2c:73:74:65:67:72:61:74:5f:65:74:61:72:65:6d:75:6e:65:3d:73:70:65:74:73:7c:31:3d:76"
Const Codec_2802ccd8 = "reversed_hex|identity|"

Function Load_2802ccd8()
  Dim parts, result(), v_e598
  parts = Split(Material_2802ccd8, ":")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(UBound(parts) - v_e598) = CInt("&H" & parts(v_e598))
  Next
  Load_2802ccd8 = result
End Function

Function Decode_2802ccd8(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598)
  Next
  Decode_2802ccd8 = result
End Function

Function Recover_2802ccd8()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = Empty
  v_a19c = Load_2802ccd8()
  v_b27e = Decode_2802ccd8(v_a19c)
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_2802ccd8 = v_c304
End Function

Function Inspect_2802ccd8()
  Dim fields
  fields = Split(Recover_2802ccd8(), "|")
  Inspect_2802ccd8 = Join(fields, "|")
End Function
