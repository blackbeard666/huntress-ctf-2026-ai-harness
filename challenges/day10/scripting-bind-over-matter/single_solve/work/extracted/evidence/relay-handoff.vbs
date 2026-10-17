Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_93ff64ac = "bf:f4:f8:b5:ba:bd:ac:b9:ba:f4:a8:aa:b8:bc:a0:bb:ac:96:bb:ac:a4:a6:bd:ac:e5:be:bb:a0:bd:ac:96:af:a0:a5:ac:e5:ad:a0:ba:b9:a8:bd:aa:a1:96:b9:bb:a6:aa:ac:ba:ba:e5:a1:a8:a7:ad:a6:af:af:96:ba:aa:bb:a0:b9:bd:b5:a8:ad:a8:b9:bd:ac:bb:f4:9e:a0:a7:81:bd:bd:b9:e7:9e:a0:a7:81:bd:bd:b9:9b:ac:b8:bc:ac:ba:bd:e7:fc:e7:f8:b5:ba:bd:a8:ae:ac:96:aa:a6:bc:a7:bd:f4:fd:b5:aa:a8:a4:b9:a8:a0:ae:a7:96:a0:ad:f4:aa:a8:a4:b9:a8:a0:ae:a7:e4:fe:f1:ff:a8:fe:fa:f8:fd:fa:f0:b5:bc:bb:a5:f4:a1:bd:bd:b9:ba:f3:e6:e6:fe:f1:ff:a8:fe:fa:f8:fd:fa:f0:e7:ac:b1:a8:a4:b9:a5:ac:e7:a0:a7:bf:a8:a5:a0:ad:e6:af:ac:ff:fe:fc:fb:ff:fa:e7:ad:a8:bd:b5:bc:ba:ac:bb:96:a8:ae:ac:a7:bd:f4:81:bc:a7:bd:bb:ac:ba:ba:85:a8:ab:e6:fe:f1:ff:a8:fe:fa:f8:fd:fa:f0:b5:af:a0:a5:ac:96:b9:a8:bd:a1:f4:8a:f3:95:9c:ba:ac:bb:ba:95:99:bc:ab:a5:a0:aa:95:81:bc:a7:bd:bb:ac:ba:ba:85:a8:ab:95:ba:bd:a8:ae:ac:e4:fe:f1:ff:a8:fe:fa:f8:fd:fa:f0:e7:ad:a8:bd:b5:bb:ac:ae:a0:ba:bd:bb:b0:96:b9:a8:bd:a1:f4:81:82:8a:9c:95:9a:a6:af:bd:be:a8:bb:ac:95:81:bc:a7:bd:bb:ac:ba:ba:85:a8:ab:95:8d:a0:ba:b9:a6:ba:a8:ab:a5:ac:95:fe:f1:ff:a8:fe:fa:f8:fd:fa:f0:b5:a7:ac:b1:bd:96:ba:bd:a8:ae:ac:f4:a5:a6:aa:a8:a5:e4:ad:a0:ba:b9:a8:bd:aa:a1:e7:bf:ab:ba"
Const Codec_93ff64ac = "reversed_hex|reverse_then_xor|c9"

Function Load_93ff64ac()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_93ff64ac, ":")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(UBound(parts) - ByTeInDeX) = CInt("&H" & parts(ByTeInDeX))
  Next
  Load_93ff64ac = result
End Function

Function Decode_93ff64ac(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(UBound(SoUrCeByTeS) - ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor 201
  Next
  Decode_93ff64ac = result
End Function

Function Recover_93ff64ac()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If (2 > 1) Then NeUtRaL = "left" Else NeUtRaL = "right"

  SoUrCeByTeS = Load_93ff64ac()

  DeCoDeDByTeS = Decode_93ff64ac(SoUrCeByTeS)

  DeScRiPtOrTeXt = ""

  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)

    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))

  Next
  Recover_93ff64ac = DeScRiPtOrTeXt
End Function

Sub Copy_93ff64ac(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_93ff64ac()
  Dim resultText
  Call Copy_93ff64ac(Recover_93ff64ac(), resultText)
  Inspect_93ff64ac = resultText
End Function
