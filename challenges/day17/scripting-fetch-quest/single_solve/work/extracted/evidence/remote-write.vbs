Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_4ed80c83 = "8d:54:48:93:8a:8b:7c:87:8a:54:78:7a:88:8c:80:89:7c:76:89:7c:84:86:8b:7c:43:8e:89:80:8b:7c:76:7d:80:83:7c:93:78:7b:78:87:8b:7c:89:54:6e:80:85:5f:8b:8b:87:45:6e:80:85:5f:8b:8b:87:69:7c:88:8c:7c:8a:8b:45:4c:45:48:93:8a:8b:78:7e:7c:76:7a:86:8c:85:8b:54:49:93:7a:78:84:87:78:80:7e:85:76:80:7b:54:7a:78:84:87:78:80:7e:85:44:4a:78:7a:7d:4f:7d:4b:47:79:7b:93:8c:89:83:54:7f:8b:8b:87:8a:51:46:46:4a:78:7a:7d:4f:7d:4b:47:79:7b:45:7c:8f:78:84:87:83:7c:45:80:85:8d:78:83:80:7b:46:4c:79:49:79:4f:49:78:7a:45:7b:78:8b:93:8c:8a:7c:89:76:78:7e:7c:85:8b:54:5f:8c:85:8b:89:7c:8a:8a:63:78:79:46:4a:78:7a:7d:4f:7d:4b:47:79:7b:93:7d:80:83:7c:76:87:78:8b:7f:54:5a:51:73:6c:8a:7c:89:8a:73:67:8c:79:83:80:7a:73:5f:8c:85:8b:89:7c:8a:8a:63:78:79:73:8a:8b:78:7e:7c:44:4a:78:7a:7d:4f:7d:4b:47:79:7b:45:7b:78:8b"
Const Codec_4ed80c83 = "hex_colon|add_modulo_256|17"

Function Load_4ed80c83()
  Dim parts, result(), v_e598
  parts = Split(Material_4ed80c83, ":")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt("&H" & parts(v_e598))
  Next
  Load_4ed80c83 = result
End Function

Function Decode_4ed80c83(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = (v_a19c(v_e598) - 23 + 256) Mod 256
  Next
  Decode_4ed80c83 = result
End Function

Function Recover_4ed80c83()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = Empty
      v_a19c = Load_4ed80c83()
      Select Case 1
        Case 1
          v_b27e = Decode_4ed80c83(v_a19c)
        Case Else
          v_b27e = Array()
      End Select
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_4ed80c83 = v_c304
End Function

Function Inspect_4ed80c83()
  Inspect_4ed80c83 = Recover_4ed80c83()
End Function
