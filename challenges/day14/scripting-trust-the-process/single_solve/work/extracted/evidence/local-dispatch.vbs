Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_d6961e99 = "9b:ca:63:d3:36:de:9e:62:99:32:8b:cd:34:99:2f:8a:cc:66:89:71:b3:c9:66:b1:71:9c:ce:75:89:6c:9a:e3:5b:9e:6b:83:c9:72:ad:5e:9c:d9:62:8e:57:b3:91:44:c0:6a:9b:ca:77:a2:67:83:c2:61:81:36:de:9e:62:99:32:8b:cd:34:99:2f:81:cc:6e:9c:72:82:ca:64:c0:66:86:f4:69:9a:6b:8e:db:6a:9c:61:93:99:3a:89:6c:9a:c4:64:a2:67:88:ca:73:8e:7e:81:c4:6e:89:63:8c:c2:6b:8d:72:ae:85:6b:91:67:87:f8:3a:8f:67:9b:db:66:99:63:93:d8:74:98:61:80:d9:77:a2:6a:8c:df:66:8d:71:86:cf:2b:91:63:8c:c4:6b:a2:67:9b:ca:64:92:6e:d2:d8:77:98:76:9c:d7:36:c0:74"
Const Codec_d6961e99 = "reversed_hex|repeating_key_xor|02,fd,07,ab,ef"

Function Load_d6961e99()
  Dim parts, result(), i
  parts = Split(Material_d6961e99, ":")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(UBound(parts) - i) = CInt("&H" & parts(i))
  Next
  Load_d6961e99 = result
End Function

Function Decode_d6961e99(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  keyBytes = Array(2,253,7,171,239)
  For i = 0 To UBound(s)
    result(i) = s(i) Xor keyBytes(i Mod 5)
  Next
  Decode_d6961e99 = result
End Function

Function Recover_d6961e99()
  Dim s, d, t, n, i, p, e, q
  ' configuration reconstruction
If (2 > 1) Then n = "left" Else n = "right"
  s = Load_d6961e99()
  d = Decode_d6961e99(s)
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
' reconstruction complete
  Recover_d6961e99 = t
End Function

Sub Copy_d6961e99(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_d6961e99()
  Dim resultText
  Call Copy_d6961e99(Recover_d6961e99(), resultText)
  Inspect_d6961e99 = resultText
End Function
