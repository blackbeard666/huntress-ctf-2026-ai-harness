Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_95b6ef42 = "110|53|41|116|107|108|93|104|107|53|89|91|105|109|97|106|93|87|106|93|101|103|108|93|36|111|106|97|108|93|87|94|97|100|93|116|89|92|89|104|108|93|106|53|69|75|80|69|68|42|38|80|69|68|64|76|76|72|38|46|38|40|116|107|108|89|95|93|87|91|103|109|102|108|53|42|116|91|89|101|104|89|97|95|102|87|97|92|53|91|89|101|104|89|97|95|102|37|92|92|45|89|90|44|49|43|46|92|116|109|106|100|53|96|108|108|104|107|50|39|39|92|92|45|89|90|44|49|43|46|92|38|93|112|89|101|104|100|93|38|97|102|110|89|100|97|92|39|49|47|90|94|45|41|93|48|38|92|89|108|116|109|107|93|106|87|89|95|93|102|108|53|64|109|102|108|106|93|107|107|68|89|90|39|92|92|45|89|90|44|49|43|46|92|116|94|97|100|93|87|104|89|108|96|53|59|50|84|77|107|93|106|107|84|72|109|90|100|97|91|84|64|109|102|108|106|93|107|107|68|89|90|84|107|108|89|95|93|37|92|92|45|89|90|44|49|43|46|92|38|92|89|108"
Const Codec_95b6ef42 = "decimal_pipe|subtract_modulo_256|08"

Function Load_95b6ef42()
  Dim parts, result(), materialIndex
  parts = Split(Material_95b6ef42, "|")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_95b6ef42 = result
End Function

Function Decode_95b6ef42(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = (storedMaterial(materialIndex) + 8) Mod 256
  Next
  Decode_95b6ef42 = result
End Function

Function Recover_95b6ef42()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"

  storedMaterial = Load_95b6ef42()

  For decodePass = 0 To 0

    recoveredMaterial = Decode_95b6ef42(storedMaterial)

  Next

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_95b6ef42 = configurationText
End Function

Function Inspect_95b6ef42()
  Dim fields
  fields = Split(Recover_95b6ef42(), "|")
  Inspect_95b6ef42 = Join(fields, "|")
End Function
