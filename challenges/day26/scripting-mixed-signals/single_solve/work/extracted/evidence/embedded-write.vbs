Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_f306afbd = "57:44:47:11:45:18:13:44:15:49:45:48:1c:1b:10:48:4a:44:57:56:3f:45:44:2f:56:56:48:55:57:51:58:2b:3f:46:4c:4f:45:58:33:3f:56:55:48:56:38:3f:1d:26:20:4b:57:44:53:42:48:4f:4c:49:5f:45:18:13:44:15:49:45:48:1c:1b:10:51:4a:4c:44:53:50:44:46:20:47:4c:42:51:4a:4c:44:53:50:44:46:5f:15:20:57:51:58:52:46:42:48:4a:44:57:56:5f:50:44:48:55:57:36:11:25:27:32:27:24:20:55:48:57:53:44:47:44:5f:48:4f:4c:49:42:48:57:4c:55:5a:0f:47:48:47:47:48:45:50:48:42:48:47:52:46:48:47:20:56:53:48:57:56:5f:14:20:59"
Const Codec_f306afbd = "reversed_hex|subtract_modulo_256|1d"

Function Load_f306afbd()
  Dim parts, result(), item5
  parts = Split(Material_f306afbd, ":")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt("&H" & parts(item5))
  Next
  Load_f306afbd = result
End Function

Function Decode_f306afbd(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = (item1(item5) + 29) Mod 256
  Next
  Decode_f306afbd = result
End Function

Function Recover_f306afbd()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = UBound(Array(3, 5, 8, 13))
  item1 = Load_f306afbd()
  Do
    item2 = Decode_f306afbd(item1)
    Exit Do
  Loop
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_f306afbd = item3
End Function

Function Inspect_f306afbd()
  Inspect_f306afbd = Recover_f306afbd()
End Function
