Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ef36fe16 = "5e2519645b5c4d585b254c4d4b574c4d474d554a4d4c4c4d4c145f5a515c4d474e51544d64494c49585c4d5a253b4b5a51585c51564f162e51544d3b615b5c4d55374a524d4b5c645b5c494f4d474b575d565c251a644b49555849514f5647514c254b49555849514f56151c211a1b491b184a1a20644e51544d4758495c50252b22443d5b4d5a5b44385d4a54514b44305d565c5a4d5b5b34494a445b5c494f4d151c211a1b491b184a1a20164c495c"
Const Codec_ef36fe16 = "hex_compact|subtract_modulo_256|18"

Function Load_ef36fe16()
  Dim result(), item5
  ReDim result((Len(Material_ef36fe16) \ 2) - 1)
  For item5 = 0 To UBound(result)
    result(item5) = CInt("&H" & Mid(Material_ef36fe16, item5 * 2 + 1, 2))
  Next
  Load_ef36fe16 = result
End Function

Function Decode_ef36fe16(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = (item1(item5) + 24) Mod 256
  Next
  Decode_ef36fe16 = result
End Function

Function Recover_ef36fe16()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = LCase(UCase("Host"))

  item1 = Load_ef36fe16()

  item2 = Decode_ef36fe16(item1)

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_ef36fe16 = item3
End Function

Sub Copy_ef36fe16(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_ef36fe16()
  Dim resultText
  Call Copy_ef36fe16(Recover_ef36fe16(), resultText)
  Inspect_ef36fe16 = resultText
End Function
