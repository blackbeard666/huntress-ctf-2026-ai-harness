Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_59bf5de1 = "118,61,49,124,115,116,101,112,115,61,100,101,99,111,100,101,95,101,109,98,101,100,100,101,100,44,119,114,105,116,101,95,102,105,108,101,124,97,100,97,112,116,101,114,61,65,68,79,68,66,46,83,116,114,101,97,109,124,115,116,97,103,101,95,99,111,117,110,116,61,50,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,97,52,55,55,51,98,99,101,102,101,124,102,105,108,101,95,112,97,116,104,61,67,58,92,85,115,101,114,115,92,80,117,98,108,105,99,92,72,117,110,116,114,101,115,115,76,97,98,92,115,116,97,103,101,45,97,52,55,55,51,98,99,101,102,101,46,100,97,116"
Const Codec_59bf5de1 = "reversed_decimal|reverse_bytes|"

Function Load_59bf5de1()
  Dim parts, result(), i
  parts = Split(Material_59bf5de1, ",")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt(parts(i))
  Next
  Load_59bf5de1 = result
End Function

Function Decode_59bf5de1(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(UBound(s) - i) = s(i)
  Next
  Decode_59bf5de1 = result
End Function

Function Recover_59bf5de1()
  Dim s, d, t, n, i, p, e, q
  n = Join(Array("north", "south"), ":")

  s = Load_59bf5de1()

  Do

    d = Decode_59bf5de1(s)

    Exit Do

  Loop

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_59bf5de1 = t
End Function

Function Inspect_59bf5de1()
  Dim fields
  fields = Split(Recover_59bf5de1(), "|")
  Inspect_59bf5de1 = Join(fields, "|")
End Function
