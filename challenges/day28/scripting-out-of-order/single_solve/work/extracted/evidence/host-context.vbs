Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_7080aaae = "12,7,0,13,3,6,4,3,0,7,25,64,71,91,92,9,80,93,107,64,71,91,92,72,12,7,0,13,3,6,4,3,0,7,25,90,83,93,85,68,89,85,87,9,80,93,107,90,83,93,85,68,89,85,87,72,5,9,64,90,65,91,87,107,81,83,85,64,71,72,77,70,85,90,91,93,64,87,93,112,26,83,90,93,64,68,93,70,87,103,9,70,81,64,68,85,80,85,72,90,91,93,64,85,70,65,83,93,82,90,91,87,107,90,70,65,64,81,70,24,90,91,93,64,85,70,65,83,93,82,90,91,87,107,81,80,91,87,81,80,9,71,68,81,64,71,72,5,9,66"
Const Codec_7080aaae = "decimal_comma|reverse_then_xor|34"

Function Load_7080aaae()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_7080aaae, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_7080aaae = result
End Function

Function Decode_7080aaae(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(UBound(SoUrCeByTeS) - ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor 52
  Next
  Decode_7080aaae = result
End Function

Function Recover_7080aaae()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = Join(Array("north", "south"), ":")
      SoUrCeByTeS = Load_7080aaae()
      Do
        DeCoDeDByTeS = Decode_7080aaae(SoUrCeByTeS)
        Exit Do
      Loop
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_7080aaae = DeScRiPtOrTeXt
End Function

Function Inspect_7080aaae()
  Dim fields
  fields = Split(Recover_7080aaae(), "|")
  Inspect_7080aaae = Join(fields, "|")
End Function
