Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_4c9d5b18 = "76:3d:31:7c:73:74:65:70:73:3d:61:63:71:75:69:72:65:5f:72:65:6d:6f:74:65:2c:64:69:73:70:61:74:63:68:5f:6d:65:6d:6f:72:79:7c:61:64:61:70:74:65:72:3d:57:69:6e:48:74:74:70:2e:57:69:6e:48:74:74:70:52:65:71:75:65:73:74:2e:35:2e:31:7c:73:74:61:67:65:5f:63:6f:75:6e:74:3d:32:7c:63:61:6d:70:61:69:67:6e:5f:69:64:3d:63:61:6d:70:61:69:67:6e:2d:62:63:31:30:32:36:35:32:32:34:7c:75:72:6c:3d:68:74:74:70:73:3a:2f:2f:62:63:31:30:32:36:35:32:32:34:2e:65:78:61:6d:70:6c:65:2e:69:6e:76:61:6c:69:64:2f:37:39:32:37:62:35:64:64:2e:64:61:74:7c:75:73:65:72:5f:61:67:65:6e:74:3d:48:75:6e:74:72:65:73:73:4c:61:62:2f:62:63:31:30:32:36:35:32:32:34"
Const Codec_4c9d5b18 = "reversed_hex|reverse_bytes|"

Function Load_4c9d5b18()
  Dim parts, result(), item5
  parts = Split(Material_4c9d5b18, ":")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt("&H" & parts(item5))
  Next
  Load_4c9d5b18 = result
End Function

Function Decode_4c9d5b18(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5)
  Next
  Decode_4c9d5b18 = result
End Function

Function Recover_4c9d5b18()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
item4 = UBound(Array(3, 5, 8, 13))
  item1 = Load_4c9d5b18()
  For item6 = 0 To 0
    item2 = Decode_4c9d5b18(item1)
  Next
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_4c9d5b18 = item3
End Function

Function Inspect_4c9d5b18()
  Dim fields
  fields = Split(Recover_4c9d5b18(), "|")
  Inspect_4c9d5b18 = Join(fields, "|")
End Function
