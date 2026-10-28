Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_cba20490 = "6930246f66675863663057585662575852566261595c5a686554675c62611f65586768656152566261595c5a686554675c62616f54575463675865304656655c63675c615a21375c56675c626154656c6f6667545a5852566268616730246f56546063545c5a61525c573056546063545c5a6120595726562858262a24546f5b626667525c57305b62666720595726562858262a2454"
Const Codec_cba20490 = "hex_compact|subtract_modulo_256|0d"

Function Load_cba20490()
  Dim result(), ByTeInDeX
  ReDim result((Len(Material_cba20490) \ 2) - 1)
  For ByTeInDeX = 0 To UBound(result)
    result(ByTeInDeX) = CInt("&H" & Mid(Material_cba20490, ByTeInDeX * 2 + 1, 2))
  Next
  Load_cba20490 = result
End Function

Function Decode_cba20490(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 13) Mod 256
  Next
  Decode_cba20490 = result
End Function

Function Recover_cba20490()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = LCase(UCase("Host"))

  SoUrCeByTeS = Load_cba20490()

  Do

    DeCoDeDByTeS = Decode_cba20490(SoUrCeByTeS)

    Exit Do

  Loop

  DeScRiPtOrTeXt = ""

  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)

    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))

  Next
  Recover_cba20490 = DeScRiPtOrTeXt
End Function

Sub Copy_cba20490(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_cba20490()
  Dim resultText
  Call Copy_cba20490(Recover_cba20490(), resultText)
  Inspect_cba20490 = resultText
End Function
