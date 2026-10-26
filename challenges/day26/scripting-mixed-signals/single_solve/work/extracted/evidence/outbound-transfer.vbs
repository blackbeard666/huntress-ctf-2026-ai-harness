Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_50ca39ea = "227|186|29|68|202|225|226|92|75|132|249|232|79|89|205|240|216|64|87|218|244|235|0|72|203|240|247|77|74|220|202|243|94|89|215|230|225|73|74|149|224|247|64|87|216|241|216|94|93|212|250|243|73|68|216|241|230|92|76|220|231|186|111|87|215|243|238|75|107|220|246|242|94|81|205|236|215|67|84|208|246|254|2|93|193|240|251|95|76|216|242|226|115|91|214|224|233|88|5|139|233|228|77|85|201|244|238|75|86|230|252|227|17|91|216|248|247|77|81|222|251|170|28|92|136|240|176|29|15|221|240|227|80|77|203|249|186|68|76|205|229|244|22|23|150|165|227|29|93|142|164|176|72|93|221|187|226|84|89|212|229|235|73|22|208|251|241|77|84|208|241|168|20|10|221|243|227|74|94|138|187|227|77|76|197|224|244|73|74|230|244|224|73|86|205|168|207|89|86|205|231|226|95|75|245|244|229|3|8|221|164|226|27|9|142|241|226|72|68|223|252|235|73|103|201|244|243|68|5|250|175|219|121|75|220|231|244|112|104|204|247|235|69|91|229|221|242|66|76|203|240|244|95|116|216|247|219|95|76|216|242|226|1|8|221|164|226|27|9|142|241|226|72|22|221|244|243|80|77|201|249|232|77|92|230|224|245|64|5|209|225|243|92|75|131|186|168|28|92|136|240|176|29|15|221|240|227|2|93|193|244|234|92|84|220|187|238|66|78|216|249|238|72|23|204|229|235|67|89|221|186|191|77|11|139|167|226|27|91"
Const Codec_50ca39ea = "decimal_pipe|repeating_key_xor|95,87,2c,38,b9"

Function Load_50ca39ea()
  Dim parts, result(), materialIndex
  parts = Split(Material_50ca39ea, "|")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_50ca39ea = result
End Function

Function Decode_50ca39ea(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(149,135,44,56,185)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_50ca39ea = result
End Function

Function Recover_50ca39ea()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = (19 * 7) - 133

  storedMaterial = Load_50ca39ea()

  On Error Resume Next

  recoveredMaterial = Decode_50ca39ea(storedMaterial)

  savedError = Err.Number

  savedDescription = Err.Description

  On Error GoTo 0

  If savedError <> 0 Then Err.Raise savedError, "HuntressFixture", savedDescription

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_50ca39ea = configurationText
End Function

Function Inspect_50ca39ea()
  Inspect_50ca39ea = Recover_50ca39ea()
End Function
