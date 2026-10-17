Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_5afb6560 = "239|227|239|181|170|162|170|250|163|171|173|250|182|201|222|205|212|216|222|201|166|254|246|250|245|196|254|239|244|245|231|255|254|240|248|244|247|181|173|174|169|249|168|181|166|245|244|242|232|245|254|239|227|254|231|253|175|250|173|174|173|249|173|163|169|182|245|252|242|250|235|246|250|248|166|255|242|196|245|252|242|250|235|246|250|248|231|169|166|239|245|238|244|248|196|254|252|250|239|232|231|239|248|254|241|249|212|246|254|239|232|226|200|254|247|242|221|181|252|245|242|239|235|242|233|248|200|166|233|254|239|235|250|255|250|231|254|239|244|245|196|226|233|254|237|244|248|254|233|196|254|239|242|233|236|183|239|245|254|239|245|244|248|196|246|233|244|253|232|245|250|233|239|183|232|239|254|252|233|250|239|196|254|239|250|233|254|246|238|245|254|166|232|235|254|239|232|231|170|166|237"
Const Codec_5afb6560 = "decimal_pipe|reverse_then_xor|9b"

Function Load_5afb6560()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_5afb6560, "|")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_5afb6560 = result
End Function

Function Decode_5afb6560(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(UBound(SoUrCeByTeS) - ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor 155
  Next
  Decode_5afb6560 = result
End Function

Function Recover_5afb6560()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = Join(Array("north", "south"), ":")
      SoUrCeByTeS = Load_5afb6560()
      DeCoDeDByTeS = Decode_5afb6560(SoUrCeByTeS)
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_5afb6560 = DeScRiPtOrTeXt
End Function

Sub Copy_5afb6560(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_5afb6560()
  Dim resultText
  Call Copy_5afb6560(Recover_5afb6560(), resultText)
  Inspect_5afb6560 = resultText
End Function
