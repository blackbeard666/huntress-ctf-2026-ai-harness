Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_84471d90 = "147|90|78|153|144|145|130|141|144|90|130|139|146|138|130|143|126|145|130|124|145|126|143|132|130|145|144|73|145|143|126|139|144|131|140|143|138|124|128|140|139|145|130|139|145|73|148|143|134|145|130|124|143|130|128|140|147|130|143|150|124|139|140|145|130|153|126|129|126|141|145|130|143|90|94|97|108|97|95|75|112|145|143|130|126|138|153|144|145|126|132|130|124|128|140|146|139|145|90|79|153|128|126|138|141|126|134|132|139|124|134|129|90|128|126|138|141|126|134|132|139|74|129|85|82|78|130|77|84|130|126|81|153|130|149|145|130|139|144|134|140|139|90|75|85|131|78|79|83|75|137|140|128|136|130|129|153|139|140|145|130|124|139|126|138|130|90|111|98|96|108|115|98|111|74|80|86|131|82|78|78|85|83|75|145|149|145"
Const Codec_84471d90 = "decimal_pipe|add_modulo_256|1d"

Function Load_84471d90()
  Dim parts, result(), materialIndex
  parts = Split(Material_84471d90, "|")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_84471d90 = result
End Function

Function Decode_84471d90(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = (storedMaterial(materialIndex) - 29 + 256) Mod 256
  Next
  Decode_84471d90 = result
End Function

Function Recover_84471d90()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  ' configuration reconstruction
If (2 > 1) Then harmlessValue = "left" Else harmlessValue = "right"
  storedMaterial = Load_84471d90()
  Do
    recoveredMaterial = Decode_84471d90(storedMaterial)
    Exit Do
  Loop
  configurationText = ""
  For materialIndex = 0 To UBound(recoveredMaterial)
    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
  Next
' reconstruction complete
  Recover_84471d90 = configurationText
End Function

Function Inspect_84471d90()
  Inspect_84471d90 = Recover_84471d90()
End Function
