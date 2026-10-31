Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_69200227 = "5c-23-17-62-59-5a-4b-56-59-23-52-55-49-47-5a-4b-45-52-55-49-47-52-12-4a-4f-59-56-47-5a-49-4e-45-56-58-55-49-4b-59-59-62-47-4a-47-56-5a-4b-58-23-3d-39-49-58-4f-56-5a-14-39-4e-4b-52-52-62-59-5a-47-4d-4b-45-49-55-5b-54-5a-23-18-62-49-47-53-56-47-4f-4d-54-45-4f-4a-23-49-47-53-56-47-4f-4d-54-13-4a-19-1d-4a-1c-4b-1c-4a-18-49-62-4c-4f-52-4b-45-56-47-5a-4e-23-29-20-42-3b-59-4b-58-59-42-36-5b-48-52-4f-49-42-2e-5b-54-5a-58-4b-59-59-32-47-48-42-59-5a-47-4d-4b-13-4a-19-1d-4a-1c-4b-1c-4a-18-49-14-4a-47-5a"
Const Codec_69200227 = "hex_dash|subtract_modulo_256|1a"

Function Load_69200227()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_69200227, "-")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt("&H" & parts(ByTeInDeX))
  Next
  Load_69200227 = result
End Function

Function Decode_69200227(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 26) Mod 256
  Next
  Decode_69200227 = result
End Function

Function Recover_69200227()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = (19 * 7) - 133
      SoUrCeByTeS = Load_69200227()
      Select Case 1
        Case 1
          DeCoDeDByTeS = Decode_69200227(SoUrCeByTeS)
        Case Else
          DeCoDeDByTeS = Array()
      End Select
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_69200227 = DeScRiPtOrTeXt
End Function

Sub Copy_69200227(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_69200227()
  Dim resultText
  Call Copy_69200227(Recover_69200227(), resultText)
  Inspect_69200227 = resultText
End Function
