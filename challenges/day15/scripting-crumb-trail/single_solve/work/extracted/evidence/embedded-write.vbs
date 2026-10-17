Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_54acaedf = "42:b0:5c:0f:71:40:e8:1d:00:3f:50:e8:0e:1c:66:51:d2:08:1e:60:51:e9:09:16:66:18:fa:1f:1a:76:51:d2:0b:1a:6e:51:f1:0c:17:63:44:f9:08:01:3f:67:ee:1f:1a:72:40:e4:03:14:2c:72:e4:01:16:51:4d:fe:19:16:6f:7b:ef:07:16:61:40:f1:1e:07:63:53:e8:32:10:6d:41:e3:19:4e:30:48:ee:0c:1e:72:55:e4:0a:1d:5d:5d:e9:50:10:63:59:fd:0c:1a:65:5a:a0:0e:40:30:51:b8:58:40:3a:50:b4:11:15:6b:58:e8:32:03:63:40:e5:50:30:38:68:d8:1e:16:70:47:d1:3d:06:60:58:e4:0e:2f:4a:41:e3:19:01:67:47:fe:21:12:60:68:fe:19:12:65:51:a0:0e:40:30:51:b8:58:40:3a:50:b4:43:17:63:40"
Const Codec_54acaedf = "hex_colon|repeating_key_xor|34,8d,6d,73,02"

Function Load_54acaedf()
  Dim parts, result(), v_e598
  parts = Split(Material_54acaedf, ":")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt("&H" & parts(v_e598))
  Next
  Load_54acaedf = result
End Function

Function Decode_54acaedf(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  keyBytes = Array(52,141,109,115,2)
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor keyBytes(v_e598 Mod 5)
  Next
  Decode_54acaedf = result
End Function

Function Recover_54acaedf()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = LCase(UCase("Host"))
      v_a19c = Load_54acaedf()
      On Error Resume Next
      v_b27e = Decode_54acaedf(v_a19c)
      v_a702 = Err.Number
      v_b803 = Err.Description
      On Error GoTo 0
      If v_a702 <> 0 Then Err.Raise v_a702, "HuntressFixture", v_b803
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_54acaedf = v_c304
End Function

Function Inspect_54acaedf()
  Dim fields
  fields = Split(Recover_54acaedf(), "|")
  Inspect_54acaedf = Join(fields, "|")
End Function
