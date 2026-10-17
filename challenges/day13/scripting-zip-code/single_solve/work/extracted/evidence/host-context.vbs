Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_a582215f = "733a2e797071626d703a6162606c61625c606c6b636664726f5e71666c6b296f6271726f6b5c606c6b636664726f5e71666c6b795e615e6d71626f3a50606f666d71666b642b41666071666c6b5e6f767970715e64625c606c726b713a2e79605e6a6d5e66646b5c66613a605e6a6d5e66646b2a355f322f2e632f2e616379656c70715c66613a656c70712a355f322f2e632f2e6163"
Const Codec_a582215f = "hex_compact|subtract_modulo_256|03"

Function Load_a582215f()
  Dim result(), i
  ReDim result((Len(Material_a582215f) \ 2) - 1)
  For i = 0 To UBound(result)
    result(i) = CInt("&H" & Mid(Material_a582215f, i * 2 + 1, 2))
  Next
  Load_a582215f = result
End Function

Function Decode_a582215f(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) + 3) Mod 256
  Next
  Decode_a582215f = result
End Function

Function Recover_a582215f()
  Dim s, d, t, n, i, p, e, q
  If (2 > 1) Then n = "left" Else n = "right"

  s = Load_a582215f()

  Do

    d = Decode_a582215f(s)

    Exit Do

  Loop

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_a582215f = t
End Function

Sub Copy_a582215f(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_a582215f()
  Dim resultText
  Call Copy_a582215f(Recover_a582215f(), resultText)
  Inspect_a582215f = resultText
End Function
