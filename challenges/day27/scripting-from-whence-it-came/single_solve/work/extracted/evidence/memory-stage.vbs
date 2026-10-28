Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_e872387f = "27,24,29,76,75,30,31,30,31,78,23,74,73,52,91,91,77,90,92,86,93,48,37,92,86,77,79,73,71,90,77,91,93,100,92,73,76,22,30,25,25,76,78,78,32,33,23,76,81,84,73,94,86,81,22,77,84,88,85,73,96,77,22,27,24,29,76,75,30,31,30,31,78,23,23,34,91,88,92,92,80,37,84,90,93,100,27,24,29,76,75,30,31,30,31,78,21,86,79,81,73,88,85,73,75,37,76,81,71,86,79,81,73,88,85,73,75,100,26,37,92,86,93,87,75,71,77,79,73,92,91,100,56,60,60,48,52,53,64,22,92,78,87,91,87,90,75,81,53,37,90,77,92,88,73,76,73,100,97,90,87,85,77,85,71,80,75,92,73,88,91,81,76,20,77,92,87,85,77,90,71,77,90,81,93,89,75,73,37,91,88,77,92,91,100,25,37,94"
Const Codec_e872387f = "reversed_decimal|subtract_modulo_256|18"

Function Load_e872387f()
  Dim parts, result(), i
  parts = Split(Material_e872387f, ",")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt(parts(i))
  Next
  Load_e872387f = result
End Function

Function Decode_e872387f(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) + 24) Mod 256
  Next
  Decode_e872387f = result
End Function

Function Recover_e872387f()
  Dim s, d, t, n, i, p, e, q
  If True Then
    n = Empty
      s = Load_e872387f()
      Do
        d = Decode_e872387f(s)
        Exit Do
      Loop
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_e872387f = t
End Function

Function Inspect_e872387f()
  Dim fields
  fields = Split(Recover_e872387f(), "|")
  Inspect_e872387f = Join(fields, "|")
End Function
