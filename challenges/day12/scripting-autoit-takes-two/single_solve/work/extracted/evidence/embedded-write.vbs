Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_4c2338ca = "90-57-4b-96-8d-8e-7f-8a-8d-57-7e-7f-7d-89-7e-7f-79-7f-87-7c-7f-7e-7e-7f-7e-46-91-8c-83-8e-7f-79-80-83-86-7f-96-7b-7e-7b-8a-8e-7f-8c-57-5b-5e-69-5e-5c-48-6d-8e-8c-7f-7b-87-96-8d-8e-7b-81-7f-79-7d-89-8f-88-8e-57-4c-96-7d-7b-87-8a-7b-83-81-88-79-83-7e-57-7d-7b-87-8a-7b-83-81-88-47-4e-51-4f-53-52-4a-4c-4d-4e-53-96-80-83-86-7f-79-8a-7b-8e-82-57-5d-54-76-6f-8d-7f-8c-8d-76-6a-8f-7c-86-83-7d-76-62-8f-88-8e-8c-7f-8d-8d-66-7b-7c-76-8d-8e-7b-81-7f-47-4e-51-4f-53-52-4a-4c-4d-4e-53-48-7e-7b-8e"
Const Codec_4c2338ca = "hex_dash|add_modulo_256|1a"

Function Load_4c2338ca()
  Dim parts, result(), v_e598
  parts = Split(Material_4c2338ca, "-")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt("&H" & parts(v_e598))
  Next
  Load_4c2338ca = result
End Function

Function Decode_4c2338ca(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = (v_a19c(v_e598) - 26 + 256) Mod 256
  Next
  Decode_4c2338ca = result
End Function

Function Recover_4c2338ca()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = LCase(UCase("Host"))
  v_a19c = Load_4c2338ca()
  For v_f602 = 0 To 0
    v_b27e = Decode_4c2338ca(v_a19c)
  Next
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_4c2338ca = v_c304
End Function

Function Inspect_4c2338ca()
  Inspect_4c2338ca = Recover_4c2338ca()
End Function
