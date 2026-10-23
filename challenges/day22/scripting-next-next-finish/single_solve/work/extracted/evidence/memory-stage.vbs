Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_a70e7efa = "c0:fd:cc:b0:c3:b7:d2:a2:d1:ec:8d:ee:9f:ea:83:f1:94:cb:b9:dc:b1:de:aa:cf:e3:87:ee:9d:ed:8c:f8:9b:f3:ac:c1:a4:c9:a6:d4:ad:d1:b0:d4:b5:c5:b1:d4:a6:9b:d6:85:dd:90:dc:ee:c0:98:d5:99:d1:85:d1:81:af:99:b7:87:fb:88:fc:9d:fa:9f:c0:a3:cc:b9:d7:a3:9e:ac:d0:b3:d2:bf:cf:ae:c7:a0:ce:91:f8:9c:a1:c2:a3:ce:be:df:b6:d1:bf:92:f7:92:f3:c0:a5:97:a7:9f:ad:9e:e2:97:e5:89:b4:dc:a8:dc:ac:df:e5:ca:e5:80:e5:84:b7:d2:e0:d0:e8:da:e9:c7:a2:da:bb:d6:a6:ca:af:81:e8:86:f0:91:fd:94:f0:df:be:89:bc:8d:bb:8e:e8:df:f1:95:f4:80:fc:89:fa:9f:ed:b2:d3:b4:d1:bf:cb:f6:be:cb:a5:d1:a3:c6:b5:c6:8a:eb:89:a6:c3:a6:c7:f4:91:a3:93:ab:99:aa"
Const Codec_a70e7efa = "hex_colon|rolling_xor|b6"

Function Load_a70e7efa()
  Dim parts, result(), v_e598
  parts = Split(Material_a70e7efa, ":")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt("&H" & parts(v_e598))
  Next
  Load_a70e7efa = result
End Function

Function Decode_a70e7efa(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  previous = 182
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor previous
    previous = v_a19c(v_e598)
  Next
  Decode_a70e7efa = result
End Function

Function Recover_a70e7efa()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = Empty
  v_a19c = Load_a70e7efa()
  On Error Resume Next
  v_b27e = Decode_a70e7efa(v_a19c)
  v_a702 = Err.Number
  v_b803 = Err.Description
  On Error GoTo 0
  If v_a702 <> 0 Then Err.Raise v_a702, "HuntressFixture", v_b803
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_a70e7efa = v_c304
End Function

Sub Copy_a70e7efa(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_a70e7efa()
  Dim resultText
  Call Copy_a70e7efa(Recover_a70e7efa(), resultText)
  Inspect_a70e7efa = resultText
End Function
