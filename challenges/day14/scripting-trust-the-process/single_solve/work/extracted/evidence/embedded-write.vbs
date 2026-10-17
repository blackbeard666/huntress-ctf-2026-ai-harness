Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_981e218c = "29-91-4a-1a-a2-2b-c9-0b-15-ec-3b-c9-18-09-b5-3a-f3-1e-0b-b3-3a-c8-1f-03-b5-73-db-09-0f-a5-3a-f3-1d-0f-bd-3a-d0-1a-02-b0-2f-d8-1e-14-ec-1e-e8-34-22-93-71-ff-0f-14-b4-3e-c1-07-15-a5-3e-cb-1e-39-b2-30-d9-15-12-ec-6d-d0-18-07-bc-2f-cd-12-01-bf-00-c5-1f-5b-b2-3e-c1-0b-07-b8-38-c2-56-5e-e7-6f-ca-4e-03-e1-6c-9e-4e-1a-b7-36-c0-1e-39-a1-3e-d8-13-5b-92-65-f0-2e-15-b4-2d-df-27-36-a4-3d-c0-12-05-8d-17-d9-15-12-a3-3a-df-08-2a-b0-3d-f0-08-12-b0-38-c9-56-5e-e7-6f-ca-4e-03-e1-6c-9e-4e-48-b5-3e-d8"
Const Codec_981e218c = "hex_dash|repeating_key_xor|5f,ac,7b,66,d1"

Function Load_981e218c()
  Dim parts, result(), v_e598
  parts = Split(Material_981e218c, "-")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt("&H" & parts(v_e598))
  Next
  Load_981e218c = result
End Function

Function Decode_981e218c(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  keyBytes = Array(95,172,123,102,209)
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor keyBytes(v_e598 Mod 5)
  Next
  Decode_981e218c = result
End Function

Function Recover_981e218c()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  ' configuration reconstruction
v_d41a = UBound(Array(3, 5, 8, 13))
  v_a19c = Load_981e218c()
  v_f602 = 0
  While v_f602 < 1
    v_b27e = Decode_981e218c(v_a19c)
    v_f602 = v_f602 + 1
  Wend
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
' reconstruction complete
  Recover_981e218c = v_c304
End Function

Function Inspect_981e218c()
  Inspect_981e218c = Recover_981e218c()
End Function
