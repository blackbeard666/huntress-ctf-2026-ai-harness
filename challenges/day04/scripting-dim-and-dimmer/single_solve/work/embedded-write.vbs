Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_1480b66b = "5c231762595a4b5659234a4b49554a4b454b53484b4a4a4b4a125d584f5a4b454c4f524b62474a47565a4b5823272a352a2814395a584b475362595a474d4b4549555b545a23186249475356474f4d54454f4a2349475356474f4d54131c171c481e191916491e624c4f524b4556475a4e232920423b594b585942365b48524f49422e5b545a584b595932474842595a474d4b131c171c481e191916491e144a475a"
Const Codec_1480b66b = "hex_compact|subtract_modulo_256|1a"

Function Load_1480b66b()
  Dim result(), i
  ReDim result((Len(Material_1480b66b) \ 2) - 1)
  For i = 0 To UBound(result)
    result(i) = CInt("&H" & Mid(Material_1480b66b, i * 2 + 1, 2))
  Next
  Load_1480b66b = result
End Function

Function Decode_1480b66b(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) + 26) Mod 256
  Next
  Decode_1480b66b = result
End Function

Function Recover_1480b66b()
  Dim s, d, t, n, i, p, e, q
  n = Empty
  s = Load_1480b66b()
  Select Case 1
    Case 1
      d = Decode_1480b66b(s)
    Case Else
      d = Array()
  End Select
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
  Recover_1480b66b = t
End Function

Sub Copy_1480b66b(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_1480b66b()
  Dim resultText
  Call Copy_1480b66b(Recover_1480b66b(), resultText)
  Inspect_1480b66b = resultText
End Function
