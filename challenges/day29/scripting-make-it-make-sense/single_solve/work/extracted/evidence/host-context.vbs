Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_683fcdfd = "219,144,156,209,222,217,200,221,222,144,201,200,206,194,201,200,242,206,194,195,203,196,202,216,223,204,217,196,194,195,129,223,200,217,216,223,195,242,206,194,195,203,196,202,216,223,204,217,196,194,195,209,204,201,204,221,217,200,223,144,254,206,223,196,221,217,196,195,202,131,233,196,206,217,196,194,195,204,223,212,209,222,217,204,202,200,242,206,194,216,195,217,144,156,209,206,204,192,221,204,196,202,195,242,196,201,144,206,204,192,221,204,196,202,195,128,207,159,201,156,157,201,158,152,148,200,209,197,194,222,217,242,196,201,144,197,194,222,217,128,207,159,201,156,157,201,158,152,148,200"
Const Codec_683fcdfd = "reversed_decimal|reverse_then_xor|ad"

Function Load_683fcdfd()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_683fcdfd, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(UBound(parts) - ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_683fcdfd = result
End Function

Function Decode_683fcdfd(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(UBound(SoUrCeByTeS) - ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor 173
  Next
  Decode_683fcdfd = result
End Function

Function Recover_683fcdfd()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    If (2 > 1) Then NeUtRaL = "left" Else NeUtRaL = "right"
      SoUrCeByTeS = Load_683fcdfd()
      Do
        DeCoDeDByTeS = Decode_683fcdfd(SoUrCeByTeS)
        Exit Do
      Loop
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_683fcdfd = DeScRiPtOrTeXt
End Function

Sub Copy_683fcdfd(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_683fcdfd()
  Dim resultText
  Call Copy_683fcdfd(Recover_683fcdfd(), resultText)
  Inspect_683fcdfd = resultText
End Function
