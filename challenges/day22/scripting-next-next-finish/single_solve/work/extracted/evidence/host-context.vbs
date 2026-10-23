Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_1de10bac = "98|51|53|49|102|57|100|97|56|100|45|116|115|111|104|61|100|105|95|116|115|111|104|124|98|51|53|49|102|57|100|97|56|100|45|110|103|105|97|112|109|97|99|61|100|105|95|110|103|105|97|112|109|97|99|124|49|61|116|110|117|111|99|95|101|103|97|116|115|124|116|99|101|106|98|79|109|101|116|115|121|83|101|108|105|70|46|103|110|105|116|112|105|114|99|83|61|114|101|116|112|97|100|97|124|110|111|105|116|97|114|117|103|105|102|110|111|99|95|110|114|117|116|101|114|44|110|111|105|116|97|114|117|103|105|102|110|111|99|95|101|100|111|99|101|100|61|115|112|101|116|115|124|49|61|118"
Const Codec_1de10bac = "decimal_pipe|reverse_bytes|"

Function Load_1de10bac()
  Dim parts, result(), materialIndex
  parts = Split(Material_1de10bac, "|")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_1de10bac = result
End Function

Function Decode_1de10bac(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(UBound(storedMaterial) - materialIndex) = storedMaterial(materialIndex)
  Next
  Decode_1de10bac = result
End Function

Function Recover_1de10bac()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = UBound(Array(3, 5, 8, 13))

  storedMaterial = Load_1de10bac()

  decodePass = 0

  While decodePass < 1

    recoveredMaterial = Decode_1de10bac(storedMaterial)

    decodePass = decodePass + 1

  Wend

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_1de10bac = configurationText
End Function

Function Inspect_1de10bac()
  Dim fields
  fields = Split(Recover_1de10bac(), "|")
  Inspect_1de10bac = Join(fields, "|")
End Function
