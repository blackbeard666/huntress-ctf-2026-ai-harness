Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_8795450f = "76:3d:31:7c:73:74:65:70:73:3d:61:63:71:75:69:72:65:5f:72:65:6d:6f:74:65:2c:77:72:69:74:65:5f:66:69:6c:65:2c:64:69:73:70:61:74:63:68:5f:70:72:6f:63:65:73:73:2c:68:61:6e:64:6f:66:66:5f:73:63:72:69:70:74:7c:61:64:61:70:74:65:72:3d:4d:53:58:4d:4c:32:2e:58:4d:4c:48:54:54:50:2e:36:2e:30:7c:73:74:61:67:65:5f:63:6f:75:6e:74:3d:34:7c:63:61:6d:70:61:69:67:6e:5f:69:64:3d:63:61:6d:70:61:69:67:6e:2d:35:63:37:34:39:32:30:35:33:63:7c:75:72:6c:3d:68:74:74:70:73:3a:2f:2f:35:63:37:34:39:32:30:35:33:63:2e:65:78:61:6d:70:6c:65:2e:69:6e:76:61:6c:69:64:2f:32:63:30:61:38:63:61:30:2e:64:61:74:7c:75:73:65:72:5f:61:67:65:6e:74:3d:48:75:6e:74:72:65:73:73:4c:61:62:2f:35:63:37:34:39:32:30:35:33:63:7c:66:69:6c:65:5f:70:61:74:68:3d:43:3a:5c:55:73:65:72:73:5c:50:75:62:6c:69:63:5c:48:75:6e:74:72:65:73:73:4c:61:62:5c:73:74:61:67:65:2d:35:63:37:34:39:32:30:35:33:63:2e:64:61:74:7c:72:65:67:69:73:74:72:79:5f:70:61:74:68:3d:48:4b:43:55:5c:53:6f:66:74:77:61:72:65:5c:48:75:6e:74:72:65:73:73:4c:61:62:5c:44:69:73:70:6f:73:61:62:6c:65:5c:35:63:37:34:39:32:30:35:33:63:7c:6e:65:78:74:5f:73:74:61:67:65:3d:6c:6f:63:61:6c:2d:64:69:73:70:61:74:63:68:2e:76:62:73"
Const Codec_8795450f = "hex_colon|identity|"

Function Load_8795450f()
  Dim parts, result(), item5
  parts = Split(Material_8795450f, ":")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt("&H" & parts(item5))
  Next
  Load_8795450f = result
End Function

Function Decode_8795450f(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5)
  Next
  Decode_8795450f = result
End Function

Function Recover_8795450f()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
item4 = LCase(UCase("Host"))
  item1 = Load_8795450f()
  Select Case 1
    Case 1
      item2 = Decode_8795450f(item1)
    Case Else
      item2 = Array()
  End Select
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_8795450f = item3
End Function

Sub Copy_8795450f(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_8795450f()
  Dim resultText
  Call Copy_8795450f(Recover_8795450f(), resultText)
  Inspect_8795450f = resultText
End Function
