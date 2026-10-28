Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_a57bd5e6 = "874e428d84857681844e727482867a83767083767e8085763d88837a857670777a7d763d757a84817285747970818380747684843d79727f75807777708474837a81858d727572818576834e5e64695e5d433f695e5d596565613f473f418d8485727876707480867f854e458d74727e81727a787f707a754e74727e81727a787f3e427272747243754543758d86837d4e79858581844b4040427272747243754543753f7689727e817d763f7a7f87727d7a754076747443457775723f7572858d86847683707278767f854e59867f85837684845d727340427272747243754543758d777a7d7670817285794e544b6d66847683846d6186737d7a746d59867f85837684845d72736d84857278763e427272747243754543753f7572858d8376787a8485838a70817285794e595c54666d64807785887283766d59867f85837684845d72736d557a8481808472737d766d427272747243754543758d7f7689857084857278764e7d8074727d3e757a8481728574793f877384"
Const Codec_a57bd5e6 = "hex_compact|add_modulo_256|11"

Function Load_a57bd5e6()
  Dim result(), v_e598
  ReDim result((Len(Material_a57bd5e6) \ 2) - 1)
  For v_e598 = 0 To UBound(result)
    result(v_e598) = CInt("&H" & Mid(Material_a57bd5e6, v_e598 * 2 + 1, 2))
  Next
  Load_a57bd5e6 = result
End Function

Function Decode_a57bd5e6(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = (v_a19c(v_e598) - 17 + 256) Mod 256
  Next
  Decode_a57bd5e6 = result
End Function

Function Recover_a57bd5e6()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = (19 * 7) - 133

  v_a19c = Load_a57bd5e6()

  v_f602 = 0

  While v_f602 < 1

    v_b27e = Decode_a57bd5e6(v_a19c)

    v_f602 = v_f602 + 1

  Wend

  v_c304 = ""

  For v_e598 = 0 To UBound(v_b27e)

    v_c304 = v_c304 & Chr(v_b27e(v_e598))

  Next
  Recover_a57bd5e6 = v_c304
End Function

Function Inspect_a57bd5e6()
  Inspect_a57bd5e6 = Recover_a57bd5e6()
End Function
