Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ea0a621d = "27,195,91,24,87,11,213,76,70,76,1,197,0,90,94,11,206,65,11,90,15,192,89,69,96,28,217,72,88,67,80,192,26,4,90,94,197,78,84,89,52,196,65,84,94,27,206,93,69,86,44,253,79,87,115,27,210,72,68,75,6,212,101,106,90,26,192,90,66,89,7,242,113,99,124,35,233,16,94,75,9,209,114,79,77,28,210,68,81,90,26,221,89,87,91,70,153,76,1,13,13,151,73,85,93,14,140,72,81,94,28,210,113,84,94,36,210,94,83,77,28,207,88,126,99,11,200,65,84,74,56,253,94,68,90,27,244,113,12,124,85,201,89,87,79,55,196,65,95,89,20,153,76,1,13,13,151,73,85,93,14,142,79,87,115,27,210,72,68,75,6,212,101,11,75,6,196,74,87,96,26,196,94,67,67,28,192,73,24,15,93,192,27,6,14,13,148,2,82,86,4,192,91,88,86,70,196,65,70,82,9,217,72,24,7,9,150,31,83,9,12,194,79,80,16,71,155,94,70,75,28,201,16,90,77,29,221,21,87,8,90,196,27,82,92,10,199,0,88,88,1,192,93,91,94,11,156,73,95,96,6,198,68,87,79,5,192,78,74,11,85,213,67,67,80,11,254,72,81,94,28,210,81,7,17,93,143,89,69,90,29,208,72,100,79,28,213,101,88,86,63,143,93,66,75,32,207,68,97,2,26,196,89,70,94,12,192,81,66,79,1,211,78,69,96,14,199,66,82,81,9,201,1,69,76,13,194,66,68,79,55,201,78,66,94,24,210,68,82,19,13,205,68,80,96,13,213,68,68,72,68,196,89,89,82,13,211,114,83,77,1,212,92,85,94,85,210,93,83,75,27,221,28,11,73"
Const Codec_ea0a621d = "reversed_decimal|repeating_key_xor|3f,36,2d,a1,68"

Function Load_ea0a621d()
  Dim parts, result(), i
  parts = Split(Material_ea0a621d, ",")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt(parts(i))
  Next
  Load_ea0a621d = result
End Function

Function Decode_ea0a621d(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  keyBytes = Array(63,54,45,161,104)
  For i = 0 To UBound(s)
    result(i) = s(i) Xor keyBytes(i Mod 5)
  Next
  Decode_ea0a621d = result
End Function

Function Recover_ea0a621d()
  Dim s, d, t, n, i, p, e, q
  If True Then
    If (2 > 1) Then n = "left" Else n = "right"
      s = Load_ea0a621d()
      p = 0
      While p < 1
        d = Decode_ea0a621d(s)
        p = p + 1
      Wend
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_ea0a621d = t
End Function

Sub Copy_ea0a621d(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_ea0a621d()
  Dim resultText
  Call Copy_ea0a621d(Recover_ea0a621d(), resultText)
  Inspect_ea0a621d = resultText
End Function
