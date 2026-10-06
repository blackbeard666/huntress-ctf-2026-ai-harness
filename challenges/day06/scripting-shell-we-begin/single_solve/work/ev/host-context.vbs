Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_1a34fc60 = "91,38,90,92,40,43,43,45,45,41,35,106,105,101,94,51,90,95,85,106,105,101,94,114,91,38,90,92,40,43,43,45,45,41,35,100,93,95,87,102,99,87,89,51,90,95,85,100,93,95,87,102,99,87,89,114,39,51,106,100,107,101,89,85,91,93,87,106,105,114,106,89,91,96,88,69,99,91,106,105,111,73,91,98,95,60,36,93,100,95,106,102,95,104,89,73,51,104,91,106,102,87,90,87,114,100,101,95,106,87,104,107,93,95,92,100,101,89,85,100,104,107,106,91,104,34,100,101,95,106,87,104,107,93,95,92,100,101,89,85,91,90,101,89,91,90,51,105,102,91,106,105,114,39,51,108"
Const Codec_1a34fc60 = "reversed_decimal|subtract_modulo_256|0a"

Function Load_1a34fc60()
  Dim parts, result(), item5
  parts = Split(Material_1a34fc60, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt(parts(item5))
  Next
  Load_1a34fc60 = result
End Function

Function Decode_1a34fc60(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = (item1(item5) + 10) Mod 256
  Next
  Decode_1a34fc60 = result
End Function

Function Recover_1a34fc60()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = Join(Array("north", "south"), ":")

  item1 = Load_1a34fc60()

  item6 = 0

  While item6 < 1

    item2 = Decode_1a34fc60(item1)

    item6 = item6 + 1

  Wend

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_1a34fc60 = item3
End Function

Sub Copy_1a34fc60(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_1a34fc60()
  Dim resultText
  Call Copy_1a34fc60(Recover_1a34fc60(), resultText)
  Inspect_1a34fc60 = resultText
End Function
