Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_bcc87af3 = "52,53,97,97,51,100,49,48,102,102,45,116,115,111,104,61,100,105,95,116,115,111,104,124,52,53,97,97,51,100,49,48,102,102,45,110,103,105,97,112,109,97,99,61,100,105,95,110,103,105,97,112,109,97,99,124,49,61,116,110,117,111,99,95,101,103,97,116,115,124,121,114,97,110,111,105,116,99,105,68,46,103,110,105,116,112,105,114,99,83,61,114,101,116,112,97,100,97,124,110,111,105,116,97,114,117,103,105,102,110,111,99,95,110,114,117,116,101,114,44,110,111,105,116,97,114,117,103,105,102,110,111,99,95,101,100,111,99,101,100,61,115,112,101,116,115,124,49,61,118"
Const Codec_bcc87af3 = "reversed_decimal|identity|"

Function Load_bcc87af3()
  Dim parts, result(), v_e598
  parts = Split(Material_bcc87af3, ",")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(UBound(parts) - v_e598) = CInt(parts(v_e598))
  Next
  Load_bcc87af3 = result
End Function

Function Decode_bcc87af3(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598)
  Next
  Decode_bcc87af3 = result
End Function

Function Recover_bcc87af3()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = UBound(Array(3, 5, 8, 13))

  v_a19c = Load_bcc87af3()

  On Error Resume Next

  v_b27e = Decode_bcc87af3(v_a19c)

  v_a702 = Err.Number

  v_b803 = Err.Description

  On Error GoTo 0

  If v_a702 <> 0 Then Err.Raise v_a702, "HuntressFixture", v_b803

  v_c304 = ""

  For v_e598 = 0 To UBound(v_b27e)

    v_c304 = v_c304 & Chr(v_b27e(v_e598))

  Next
  Recover_bcc87af3 = v_c304
End Function

Function Inspect_bcc87af3()
  Inspect_bcc87af3 = Recover_bcc87af3()
End Function
