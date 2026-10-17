Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_bd7b3987 = "6f362a756c6d5e696c3665685c5a6d5e5865685c5a65255d626c695a6d5c6158696b685c5e6c6c755a5d5a696d5e6b364c615e6565273a696965625c5a6d626867756c6d5a605e585c686e676d362b755c5a66695a62606758625d365c5a66695a626067262e2a5c2f3029292e5c5d755f62655e58695a6d61363c33554e6c5e6b6c55496e5b65625c55416e676d6b5e6c6c455a5b556c6d5a605e262e2a5c2f3029292e5c5d275d5a6d"
Const Codec_bd7b3987 = "hex_compact|subtract_modulo_256|07"

Function Load_bd7b3987()
  Dim result(), ByTeInDeX
  ReDim result((Len(Material_bd7b3987) \ 2) - 1)
  For ByTeInDeX = 0 To UBound(result)
    result(ByTeInDeX) = CInt("&H" & Mid(Material_bd7b3987, ByTeInDeX * 2 + 1, 2))
  Next
  Load_bd7b3987 = result
End Function

Function Decode_bd7b3987(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 7) Mod 256
  Next
  Decode_bd7b3987 = result
End Function

Function Recover_bd7b3987()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  ' configuration reconstruction
If (2 > 1) Then NeUtRaL = "left" Else NeUtRaL = "right"
  SoUrCeByTeS = Load_bd7b3987()
  Do
    DeCoDeDByTeS = Decode_bd7b3987(SoUrCeByTeS)
    Exit Do
  Loop
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
' reconstruction complete
  Recover_bd7b3987 = DeScRiPtOrTeXt
End Function

Function Inspect_bd7b3987()
  Inspect_bd7b3987 = Recover_bd7b3987()
End Function
