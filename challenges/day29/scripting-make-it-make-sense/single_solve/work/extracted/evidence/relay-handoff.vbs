Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_6efa5820 = "05:4e:42:0f:00:07:16:03:00:4e:12:10:02:06:1a:01:16:2c:01:16:1e:1c:07:16:5f:04:01:1a:07:16:2c:15:1a:1f:16:5f:17:1a:00:03:12:07:10:1b:2c:03:01:1c:10:16:00:00:5f:1b:12:1d:17:1c:15:15:2c:00:10:01:1a:03:07:0f:12:17:12:03:07:16:01:4e:24:1a:1d:3b:07:07:03:5d:24:1a:1d:3b:07:07:03:21:16:02:06:16:00:07:5d:46:5d:42:0f:00:07:12:14:16:2c:10:1c:06:1d:07:4e:47:0f:10:12:1e:03:12:1a:14:1d:2c:1a:17:4e:10:12:1e:03:12:1a:14:1d:5e:47:46:41:44:42:45:47:45:47:11:0f:06:01:1f:4e:1b:07:07:03:00:49:5c:5c:47:46:41:44:42:45:47:45:47:11:5d:16:0b:12:1e:03:1f:16:5d:1a:1d:05:12:1f:1a:17:5c:16:16:15:15:44:4b:44:43:5d:17:12:07:0f:06:00:16:01:2c:12:14:16:1d:07:4e:3b:06:1d:07:01:16:00:00:3f:12:11:5c:47:46:41:44:42:45:47:45:47:11:0f:15:1a:1f:16:2c:03:12:07:1b:4e:30:49:2f:26:00:16:01:00:2f:23:06:11:1f:1a:10:2f:3b:06:1d:07:01:16:00:00:3f:12:11:2f:00:07:12:14:16:5e:47:46:41:44:42:45:47:45:47:11:5d:17:12:07:0f:01:16:14:1a:00:07:01:0a:2c:03:12:07:1b:4e:3b:38:30:26:2f:20:1c:15:07:04:12:01:16:2f:3b:06:1d:07:01:16:00:00:3f:12:11:2f:37:1a:00:03:1c:00:12:11:1f:16:2f:47:46:41:44:42:45:47:45:47:11:0f:1d:16:0b:07:2c:00:07:12:14:16:4e:1f:1c:10:12:1f:5e:17:1a:00:03:12:07:10:1b:5d:05:11:00"
Const Codec_6efa5820 = "hex_colon|single_byte_xor|73"

Function Load_6efa5820()
  Dim parts, result(), item5
  parts = Split(Material_6efa5820, ":")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt("&H" & parts(item5))
  Next
  Load_6efa5820 = result
End Function

Function Decode_6efa5820(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor 115
  Next
  Decode_6efa5820 = result
End Function

Function Recover_6efa5820()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = Empty

  item1 = Load_6efa5820()

  item2 = Decode_6efa5820(item1)

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_6efa5820 = item3
End Function

Sub Copy_6efa5820(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_6efa5820()
  Dim resultText
  Call Copy_6efa5820(Recover_6efa5820(), resultText)
  Inspect_6efa5820 = resultText
End Function
