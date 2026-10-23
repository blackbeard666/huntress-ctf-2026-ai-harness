Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_fdc9491c = "c3-88-84-c9-c6-c1-d0-c5-c6-88-d4-d6-c4-c0-dc-c7-d0-ea-c7-d0-d8-da-c1-d0-99-c2-c7-dc-c1-d0-ea-d3-dc-d9-d0-99-d1-dc-c6-c5-d4-c1-d6-dd-ea-c5-c7-da-d6-d0-c6-c6-99-dd-d4-db-d1-da-d3-d3-ea-c6-d6-c7-dc-c5-c1-c9-d4-d1-d4-c5-c1-d0-c7-88-f8-dc-d6-c7-da-c6-da-d3-c1-9b-ed-f8-f9-fd-e1-e1-e5-c9-c6-c1-d4-d2-d0-ea-d6-da-c0-db-c1-88-81-c9-d6-d4-d8-c5-d4-dc-d2-db-ea-dc-d1-88-d6-d4-d8-c5-d4-dc-d2-db-98-84-d4-81-81-d7-d1-d3-d7-80-d1-c9-c0-c7-d9-88-dd-c1-c1-c5-c6-8f-9a-9a-84-d4-81-81-d7-d1-d3-d7-80-d1-9b-d0-cd-d4-d8-c5-d9-d0-9b-dc-db-c3-d4-d9-dc-d1-9a-81-8d-d0-d3-85-d3-d7-80-9b-d1-d4-c1-c9-c0-c6-d0-c7-ea-d4-d2-d0-db-c1-88-fd-c0-db-c1-c7-d0-c6-c6-f9-d4-d7-9a-84-d4-81-81-d7-d1-d3-d7-80-d1-c9-d3-dc-d9-d0-ea-c5-d4-c1-dd-88-f6-8f-e9-e0-c6-d0-c7-c6-e9-e5-c0-d7-d9-dc-d6-e9-fd-c0-db-c1-c7-d0-c6-c6-f9-d4-d7-e9-c6-c1-d4-d2-d0-98-84-d4-81-81-d7-d1-d3-d7-80-d1-9b-d1-d4-c1-c9-c7-d0-d2-dc-c6-c1-c7-cc-ea-c5-d4-c1-dd-88-fd-fe-f6-e0-e9-e6-da-d3-c1-c2-d4-c7-d0-e9-fd-c0-db-c1-c7-d0-c6-c6-f9-d4-d7-e9-f1-dc-c6-c5-da-c6-d4-d7-d9-d0-e9-84-d4-81-81-d7-d1-d3-d7-80-d1-c9-db-d0-cd-c1-ea-c6-c1-d4-d2-d0-88-d9-da-d6-d4-d9-98-d1-dc-c6-c5-d4-c1-d6-dd-9b-c3-d7-c6"
Const Codec_fdc9491c = "hex_dash|single_byte_xor|b5"

Function Load_fdc9491c()
  Dim parts, result(), i
  parts = Split(Material_fdc9491c, "-")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt("&H" & parts(i))
  Next
  Load_fdc9491c = result
End Function

Function Decode_fdc9491c(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = s(i) Xor 181
  Next
  Decode_fdc9491c = result
End Function

Function Recover_fdc9491c()
  Dim s, d, t, n, i, p, e, q
  n = LCase(UCase("Host"))

  s = Load_fdc9491c()

  Do

    d = Decode_fdc9491c(s)

    Exit Do

  Loop

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_fdc9491c = t
End Function

Function Inspect_fdc9491c()
  Inspect_fdc9491c = Recover_fdc9491c()
End Function
