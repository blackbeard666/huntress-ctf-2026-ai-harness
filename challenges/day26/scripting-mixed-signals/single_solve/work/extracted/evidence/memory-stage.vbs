Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_97f23358 = "763d317c73746570733d616371756972655f72656d6f74652c64697370617463685f6d656d6f72797c616461707465723d57696e487474702e57696e48747470526571756573742e352e317c73746167655f636f756e743d327c63616d706169676e5f69643d63616d706169676e2d303865363435323665347c75726c3d68747470733a2f2f303865363435323665342e6578616d706c652e696e76616c69642f36663137613132332e6461747c757365725f6167656e743d48756e74726573734c61622f30386536343532366534"
Const Codec_97f23358 = "hex_compact|identity|"

Function Load_97f23358()
  Dim result(), ByTeInDeX
  ReDim result((Len(Material_97f23358) \ 2) - 1)
  For ByTeInDeX = 0 To UBound(result)
    result(ByTeInDeX) = CInt("&H" & Mid(Material_97f23358, ByTeInDeX * 2 + 1, 2))
  Next
  Load_97f23358 = result
End Function

Function Decode_97f23358(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_97f23358 = result
End Function

Function Recover_97f23358()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = UBound(Array(3, 5, 8, 13))

  SoUrCeByTeS = Load_97f23358()

  Select Case 1

    Case 1

      DeCoDeDByTeS = Decode_97f23358(SoUrCeByTeS)

    Case Else

      DeCoDeDByTeS = Array()

  End Select

  DeScRiPtOrTeXt = ""

  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)

    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))

  Next
  Recover_97f23358 = DeScRiPtOrTeXt
End Function

Sub Copy_97f23358(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_97f23358()
  Dim resultText
  Call Copy_97f23358(Recover_97f23358(), resultText)
  Inspect_97f23358 = resultText
End Function
