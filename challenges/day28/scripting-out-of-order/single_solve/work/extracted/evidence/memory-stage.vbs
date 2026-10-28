Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_bbc22ea6 = "76:3d:31:7c:73:74:65:70:73:3d:61:63:71:75:69:72:65:5f:72:65:6d:6f:74:65:2c:64:69:73:70:61:74:63:68:5f:6d:65:6d:6f:72:79:7c:61:64:61:70:74:65:72:3d:4d:53:58:4d:4c:32:2e:58:4d:4c:48:54:54:50:2e:36:2e:30:7c:73:74:61:67:65:5f:63:6f:75:6e:74:3d:32:7c:63:61:6d:70:61:69:67:6e:5f:69:64:3d:63:61:6d:70:61:69:67:6e:2d:35:35:37:37:66:35:31:62:33:32:7c:75:72:6c:3d:68:74:74:70:73:3a:2f:2f:35:35:37:37:66:35:31:62:33:32:2e:65:78:61:6d:70:6c:65:2e:69:6e:76:61:6c:69:64:2f:33:32:31:64:64:66:37:33:2e:64:61:74:7c:75:73:65:72:5f:61:67:65:6e:74:3d:48:75:6e:74:72:65:73:73:4c:61:62:2f:35:35:37:37:66:35:31:62:33:32"
Const Codec_bbc22ea6 = "hex_colon|identity|"

Function Load_bbc22ea6()
  Dim parts, result(), i
  parts = Split(Material_bbc22ea6, ":")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt("&H" & parts(i))
  Next
  Load_bbc22ea6 = result
End Function

Function Decode_bbc22ea6(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = s(i)
  Next
  Decode_bbc22ea6 = result
End Function

Function Recover_bbc22ea6()
  Dim s, d, t, n, i, p, e, q
  n = UBound(Array(3, 5, 8, 13))
  s = Load_bbc22ea6()
  p = 0
  While p < 1
    d = Decode_bbc22ea6(s)
    p = p + 1
  Wend
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
  Recover_bbc22ea6 = t
End Function

Sub Copy_bbc22ea6(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_bbc22ea6()
  Dim resultText
  Call Copy_bbc22ea6(Recover_bbc22ea6(), resultText)
  Inspect_bbc22ea6 = resultText
End Function
