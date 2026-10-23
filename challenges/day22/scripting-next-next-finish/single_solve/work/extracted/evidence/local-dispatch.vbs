Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_8805426a = "93-5a-4e-99-90-91-82-8d-90-5a-89-8c-80-7e-91-82-7c-89-8c-80-7e-89-49-81-86-90-8d-7e-91-80-85-7c-8d-8f-8c-80-82-90-90-99-7e-81-7e-8d-91-82-8f-5a-74-70-80-8f-86-8d-91-4b-70-85-82-89-89-99-90-91-7e-84-82-7c-80-8c-92-8b-91-5a-4f-99-80-7e-8a-8d-7e-86-84-8b-7c-86-81-5a-80-7e-8a-8d-7e-86-84-8b-4a-52-7e-4d-81-80-83-56-51-53-51-99-83-86-89-82-7c-8d-7e-91-85-5a-60-57-79-72-90-82-8f-90-79-6d-92-7f-89-86-80-79-65-92-8b-91-8f-82-90-90-69-7e-7f-79-90-91-7e-84-82-4a-52-7e-4d-81-80-83-56-51-53-51-4b-81-7e-91"
Const Codec_8805426a = "hex_dash|add_modulo_256|1d"

Function Load_8805426a()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_8805426a, "-")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt("&H" & parts(ByTeInDeX))
  Next
  Load_8805426a = result
End Function

Function Decode_8805426a(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) - 29 + 256) Mod 256
  Next
  Decode_8805426a = result
End Function

Function Recover_8805426a()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = (19 * 7) - 133

  SoUrCeByTeS = Load_8805426a()

  DeCoDeDByTeS = Decode_8805426a(SoUrCeByTeS)

  DeScRiPtOrTeXt = ""

  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)

    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))

  Next
  Recover_8805426a = DeScRiPtOrTeXt
End Function

Function Inspect_8805426a()
  Inspect_8805426a = Recover_8805426a()
End Function
