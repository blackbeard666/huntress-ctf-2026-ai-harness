Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_3594cd18 = "b8-ad-a8-e2-f9-f9-fd-fc-a8-f8-a9-fd-fc-f8-e1-a9-ab-ad-b8-bf-90-ae-ad-80-bf-bf-a9-be-b8-a2-b9-84-90-af-a5-a0-ae-b9-9c-90-bf-be-a9-bf-99-90-f6-8f-f1-a4-b8-ad-bc-93-a9-a0-a5-aa-b0-f9-f9-fd-fc-a8-f8-a9-fd-fc-f8-e1-a2-ab-a5-ad-bc-a1-ad-af-f1-a8-a5-93-a2-ab-a5-ad-bc-a1-ad-af-b0-fe-f1-b8-a2-b9-a3-af-93-a9-ab-ad-b8-bf-b0-a2-a3-a5-b8-ad-af-a5-a0-bc-bc-8d-e2-a0-a0-a9-a4-9f-f1-be-a9-b8-bc-ad-a8-ad-b0-bf-bf-a9-af-a3-be-bc-93-a4-af-b8-ad-bc-bf-a5-a8-e0-a0-ad-af-a3-a0-93-a9-b8-ad-af-a3-a0-f1-bf-bc-a9-b8-bf-b0-fd-f1-ba"
Const Codec_3594cd18 = "hex_dash|reverse_then_xor|cc"

Function Load_3594cd18()
  Dim parts, result(), v_e598
  parts = Split(Material_3594cd18, "-")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt("&H" & parts(v_e598))
  Next
  Load_3594cd18 = result
End Function

Function Decode_3594cd18(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(UBound(v_a19c) - v_e598) = v_a19c(v_e598) Xor 204
  Next
  Decode_3594cd18 = result
End Function

Function Recover_3594cd18()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = UBound(Array(3, 5, 8, 13))
      v_a19c = Load_3594cd18()
      v_b27e = Decode_3594cd18(v_a19c)
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_3594cd18 = v_c304
End Function

Function Inspect_3594cd18()
  Inspect_3594cd18 = Recover_3594cd18()
End Function
