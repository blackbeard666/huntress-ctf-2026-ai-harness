Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_59388a23 = "108|51|39|114|105|106|91|102|105|51|90|91|89|101|90|91|85|89|101|100|92|95|93|107|104|87|106|95|101|100|34|104|91|106|107|104|100|85|89|101|100|92|95|93|107|104|87|106|95|101|100|114|87|90|87|102|106|91|104|51|73|89|104|95|102|106|95|100|93|36|60|95|98|91|73|111|105|106|91|99|69|88|96|91|89|106|114|105|106|87|93|91|85|89|101|107|100|106|51|39|114|89|87|99|102|87|95|93|100|85|95|90|51|89|87|99|102|87|95|93|100|35|89|89|38|92|89|41|41|47|91|92|114|94|101|105|106|85|95|90|51|94|101|105|106|35|89|89|38|92|89|41|41|47|91|92"
Const Codec_59388a23 = "decimal_pipe|subtract_modulo_256|0a"

Function Load_59388a23()
  Dim parts, result(), v_e598
  parts = Split(Material_59388a23, "|")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_59388a23 = result
End Function

Function Decode_59388a23(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = (v_a19c(v_e598) + 10) Mod 256
  Next
  Decode_59388a23 = result
End Function

Function Recover_59388a23()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = LCase(UCase("Host"))
      v_a19c = Load_59388a23()
      Select Case 1
        Case 1
          v_b27e = Decode_59388a23(v_a19c)
        Case Else
          v_b27e = Array()
      End Select
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_59388a23 = v_c304
End Function

Sub Copy_59388a23(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_59388a23()
  Dim resultText
  Call Copy_59388a23(Recover_59388a23(), resultText)
  Inspect_59388a23 = resultText
End Function
