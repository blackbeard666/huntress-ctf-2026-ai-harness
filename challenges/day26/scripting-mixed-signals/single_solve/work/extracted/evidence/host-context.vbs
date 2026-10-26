Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_6c6261ee = "ae93a2deadd9bcccbf82e683e08feb8ed1b2ddb3d5bcdbaedcbdc9a0cfa18dff9aee9be987d8bbd4badcb5d2a7d5b4c0a9c6a8d4b5d1b0c0b4d1a39ecdaedcb5c5b1d8b6d1ffb9d0bcd98af380f491fcb3d1bbdebdc9b5c6b2d3b4d18eed82f799edd0e19dfe9ff282e38aed83dcb5d1ec8fee83f392fb9cf2dfeddce583b183e580b2d7abc3acdfabf49df9c4acc3b0c4e9dbead3b587b5d3b684e1"
Const Codec_6c6261ee = "hex_compact|rolling_xor|d8"

Function Load_6c6261ee()
  Dim result(), ByTeInDeX
  ReDim result((Len(Material_6c6261ee) \ 2) - 1)
  For ByTeInDeX = 0 To UBound(result)
    result(ByTeInDeX) = CInt("&H" & Mid(Material_6c6261ee, ByTeInDeX * 2 + 1, 2))
  Next
  Load_6c6261ee = result
End Function

Function Decode_6c6261ee(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  previous = 216
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor previous
    previous = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_6c6261ee = result
End Function

Function Recover_6c6261ee()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    If (2 > 1) Then NeUtRaL = "left" Else NeUtRaL = "right"
      SoUrCeByTeS = Load_6c6261ee()
      Select Case 1
        Case 1
          DeCoDeDByTeS = Decode_6c6261ee(SoUrCeByTeS)
        Case Else
          DeCoDeDByTeS = Array()
      End Select
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_6c6261ee = DeScRiPtOrTeXt
End Function

Function Inspect_6c6261ee()
  Dim fields
  fields = Split(Recover_6c6261ee(), "|")
  Inspect_6c6261ee = Join(fields, "|")
End Function
