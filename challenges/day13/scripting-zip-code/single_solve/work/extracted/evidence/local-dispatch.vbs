Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_0dd0665c = "91,34,22,97,88,89,74,85,88,34,81,84,72,70,89,74,68,81,84,72,70,81,17,73,78,88,85,70,89,72,77,68,85,87,84,72,74,88,88,97,70,73,70,85,89,74,87,34,60,56,72,87,78,85,89,19,56,77,74,81,81,97,88,89,70,76,74,68,72,84,90,83,89,34,23,97,72,70,82,85,70,78,76,83,68,78,73,34,72,70,82,85,70,78,76,83,18,70,22,29,71,28,26,27,70,72,27,97,75,78,81,74,68,85,70,89,77,34,40,31,65,58,88,74,87,88,65,53,90,71,81,78,72,65,45,90,83,89,87,74,88,88,49,70,71,65,88,89,70,76,74,18,70,22,29,71,28,26,27,70,72,27,19,73,70,89"
Const Codec_0dd0665c = "decimal_comma|subtract_modulo_256|1b"

Function Load_0dd0665c()
  Dim parts, result(), item5
  parts = Split(Material_0dd0665c, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_0dd0665c = result
End Function

Function Decode_0dd0665c(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = (item1(item5) + 27) Mod 256
  Next
  Decode_0dd0665c = result
End Function

Function Recover_0dd0665c()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = Join(Array("north", "south"), ":")

  item1 = Load_0dd0665c()

  item6 = 0

  While item6 < 1

    item2 = Decode_0dd0665c(item1)

    item6 = item6 + 1

  Wend

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_0dd0665c = item3
End Function

Function Inspect_0dd0665c()
  Inspect_0dd0665c = Recover_0dd0665c()
End Function
