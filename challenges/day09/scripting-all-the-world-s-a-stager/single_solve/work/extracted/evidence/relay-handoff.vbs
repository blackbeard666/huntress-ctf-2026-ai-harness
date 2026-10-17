Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_750d6149 = "227|168|164|233|230|225|240|229|230|168|244|246|228|224|252|231|240|202|231|240|248|250|225|240|185|226|231|252|225|240|202|243|252|249|240|185|241|252|230|229|244|225|246|253|202|229|231|250|246|240|230|230|185|253|244|251|241|250|243|243|202|230|246|231|252|229|225|233|244|241|244|229|225|240|231|168|194|252|251|221|225|225|229|187|194|252|251|221|225|225|229|199|240|228|224|240|230|225|187|160|187|164|233|230|225|244|242|240|202|246|250|224|251|225|168|161|233|246|244|248|229|244|252|242|251|202|252|241|168|246|244|248|229|244|252|242|251|184|241|166|173|163|241|247|247|166|163|161|233|224|231|249|168|253|225|225|229|230|175|186|186|241|166|173|163|241|247|247|166|163|161|187|240|237|244|248|229|249|240|187|252|251|227|244|249|252|241|186|167|163|162|162|167|164|173|240|187|241|244|225|233|224|230|240|231|202|244|242|240|251|225|168|221|224|251|225|231|240|230|230|217|244|247|186|241|166|173|163|241|247|247|166|163|161|233|243|252|249|240|202|229|244|225|253|168|214|175|201|192|230|240|231|230|201|197|224|247|249|252|246|201|221|224|251|225|231|240|230|230|217|244|247|201|230|225|244|242|240|184|241|166|173|163|241|247|247|166|163|161|187|241|244|225|233|231|240|242|252|230|225|231|236|202|229|244|225|253|168|221|222|214|192|201|198|250|243|225|226|244|231|240|201|221|224|251|225|231|240|230|230|217|244|247|201|209|252|230|229|250|230|244|247|249|240|201|241|166|173|163|241|247|247|166|163|161|233|251|240|237|225|202|230|225|244|242|240|168|249|250|246|244|249|184|241|252|230|229|244|225|246|253|187|227|247|230"
Const Codec_750d6149 = "decimal_pipe|single_byte_xor|95"

Function Load_750d6149()
  Dim parts, result(), materialIndex
  parts = Split(Material_750d6149, "|")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_750d6149 = result
End Function

Function Decode_750d6149(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor 149
  Next
  Decode_750d6149 = result
End Function

Function Recover_750d6149()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = UBound(Array(3, 5, 8, 13))
  storedMaterial = Load_750d6149()
  Do
    recoveredMaterial = Decode_750d6149(storedMaterial)
    Exit Do
  Loop
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
  Recover_750d6149 = configurationText
End Function

Function Inspect_750d6149()
  Dim fields
  fields = Split(Recover_750d6149(), "|")
  Inspect_750d6149 = Join(fields, "|")
End Function
