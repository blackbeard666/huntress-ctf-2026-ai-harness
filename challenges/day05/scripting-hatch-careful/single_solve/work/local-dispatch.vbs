Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_fa5f1543 = "201,85,108,176,6,138,85,110,175,15,143,7,59,174,26,216,83,105,234,68,225,86,105,210,68,206,81,122,234,89,200,124,84,253,94,209,86,125,206,107,206,70,109,237,98,225,14,75,163,95,201,85,120,193,82,209,93,110,226,6,138,85,110,175,15,143,7,59,174,26,211,83,97,255,71,208,85,107,163,83,212,107,102,249,94,220,68,101,255,84,193,6,53,234,89,200,91,107,193,82,218,85,124,237,75,211,91,97,234,86,222,93,100,238,71,252,26,100,242,82,213,103,53,236,82,201,68,105,250,86,193,71,123,251,84,210,70,120,193,95,222,64,105,238,68,212,80,36,242,86,222,91,100,193,82,201,85,107,241,91,128,71,120,251,67,206,72,57,163,65"
Const Codec_fa5f1543 = "reversed_decimal|repeating_key_xor|37,9e,08,34,bd"

Function Load_fa5f1543()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_fa5f1543, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(UBound(parts) - ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_fa5f1543 = result
End Function

Function Decode_fa5f1543(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  keyBytes = Array(55,158,8,52,189)
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor keyBytes(ByTeInDeX Mod 5)
  Next
  Decode_fa5f1543 = result
End Function

Function Recover_fa5f1543()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  ' configuration reconstruction
NeUtRaL = Empty
  SoUrCeByTeS = Load_fa5f1543()
  PaSs = 0
  While PaSs < 1
    DeCoDeDByTeS = Decode_fa5f1543(SoUrCeByTeS)
    PaSs = PaSs + 1
  Wend
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
' reconstruction complete
  Recover_fa5f1543 = DeScRiPtOrTeXt
End Function

Sub Copy_fa5f1543(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_fa5f1543()
  Dim resultText
  Call Copy_fa5f1543(Recover_fa5f1543(), resultText)
  Inspect_fa5f1543 = resultText
End Function
