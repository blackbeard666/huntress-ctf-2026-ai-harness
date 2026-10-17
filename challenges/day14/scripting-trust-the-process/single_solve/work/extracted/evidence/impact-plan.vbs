Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_f19641ef = "21:44:13:f7:61:6d:08:56:ec:6f:65:5f:4a:8b:13:03:73:24:9c:04:68:59:0a:b8:38:0a:59:13:b6:38:29:58:02:b2:35:3a:50:49:eb:33:34:5a:5e:f7:6b:3b:53:0e:aa:38:30:48:1f:bc:2a:30:05:50:ed:63:61:5f:51:ef:6f:78:52:00:b0:37:25:51:06:ba:6b:31:55:38:b7:31:3c:5d:17:b4:37:36:40:55:e4:22:3b:49:08:ba:09:30:5b:06:ad:25:29:48:04:bc:3c:37:73:0a:bc:22:26:45:34:bc:3a:3c:7a:49:be:38:3c:48:17:b0:24:36:6f:5a:ab:33:21:4c:06:bd:37:29:59:13:b6:38:0a:45:15:bc:20:3a:5f:02:ab:09:30:48:0e:ab:21:79:48:09:bc:22:3b:53:04:86:3b:27:53:01:aa:38:34:4e:13:f5:25:21:59:00:ab:37:21:63:02:ad:37:27:59:0a:ac:38:30:01:14:a9:33:21:4f:1b:e8:6b:23"
Const Codec_f19641ef = "reversed_hex|repeating_key_xor|55,56,d9,67,3c"

Function Load_f19641ef()
  Dim parts, result(), item5
  parts = Split(Material_f19641ef, ":")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt("&H" & parts(item5))
  Next
  Load_f19641ef = result
End Function

Function Decode_f19641ef(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  keyBytes = Array(85,86,217,103,60)
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor keyBytes(item5 Mod 5)
  Next
  Decode_f19641ef = result
End Function

Function Recover_f19641ef()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
If (2 > 1) Then item4 = "left" Else item4 = "right"
  item1 = Load_f19641ef()
  For item6 = 0 To 0
    item2 = Decode_f19641ef(item1)
  Next
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_f19641ef = item3
End Function

Sub Copy_f19641ef(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_f19641ef()
  Dim resultText
  Call Copy_f19641ef(Recover_f19641ef(), resultText)
  Inspect_f19641ef = resultText
End Function
