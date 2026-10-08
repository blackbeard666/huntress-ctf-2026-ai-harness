Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_46278e7b = "89,70,73,19,26,75,75,27,73,70,73,74,25,70,18,74,76,70,89,88,65,71,70,49,88,88,74,87,89,83,90,45,65,72,78,81,71,90,53,65,88,87,74,88,58,65,31,40,34,77,89,70,85,68,74,81,78,75,97,26,75,75,27,73,70,73,74,25,70,18,83,76,78,70,85,82,70,72,34,73,78,68,83,76,78,70,85,82,70,72,97,23,34,89,83,90,84,72,68,74,76,70,89,88,97,83,84,78,89,70,72,78,81,85,85,38,19,81,81,74,77,56,34,87,74,89,85,70,73,70,97,88,88,74,72,84,87,85,68,77,72,89,70,85,88,78,73,17,81,70,72,84,81,68,74,89,70,72,84,81,34,88,85,74,89,88,97,22,34,91"
Const Codec_46278e7b = "reversed_decimal|subtract_modulo_256|1b"

Function Load_46278e7b()
  Dim parts, result(), item5
  parts = Split(Material_46278e7b, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(UBound(parts) - item5) = CInt(parts(item5))
  Next
  Load_46278e7b = result
End Function

Function Decode_46278e7b(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = (item1(item5) + 27) Mod 256
  Next
  Decode_46278e7b = result
End Function

Function Recover_46278e7b()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
item4 = (19 * 7) - 133
  item1 = Load_46278e7b()
  For item6 = 0 To 0
    item2 = Decode_46278e7b(item1)
  Next
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_46278e7b = item3
End Function

Function Inspect_46278e7b()
  Inspect_46278e7b = Recover_46278e7b()
End Function
