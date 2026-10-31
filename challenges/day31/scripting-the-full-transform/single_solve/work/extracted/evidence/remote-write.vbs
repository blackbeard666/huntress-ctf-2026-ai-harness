Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_e30cfb42 = "8db081fd8efa9fef9ca1c0a3d2a7cebcd986f491fc93e782aed9abc2b6d38cea83ef8af697f392e296f381bcf1a2fab7fbc9e7bff2bef6a2f6a688be90a0dcafdbbaddb8e784eb9ef084b98bf794f598e889e087e9b6dfbb86e584e999f891f698b5d4b684e784b78ee88ebbc7b2c0ac91f98df989fac0efc0a1c3f192f1c2fb9dfbcee085fd9cf181ed88a6cfa1d7b6dab3d7f89efbceff9afbc8f9d7b3d2a6daafdcb9cb94f592f799edd098ed83f785e093e0accdaf80e183b1d2b182bbddbb8ef294fd91f4abdbbacea69bd8e2beeb98fd8ffca0f085e78be281dd95e08efa88ed9eeda1c0a2fe8df998ff9ab7d6b486e586b58cea8cb997f392e6"
Const Codec_e30cfb42 = "hex_compact|rolling_xor|fb"

Function Load_e30cfb42()
  Dim result(), ByTeInDeX
  ReDim result((Len(Material_e30cfb42) \ 2) - 1)
  For ByTeInDeX = 0 To UBound(result)
    result(ByTeInDeX) = CInt("&H" & Mid(Material_e30cfb42, ByTeInDeX * 2 + 1, 2))
  Next
  Load_e30cfb42 = result
End Function

Function Decode_e30cfb42(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  previous = 251
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor previous
    previous = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_e30cfb42 = result
End Function

Function Recover_e30cfb42()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = Join(Array("north", "south"), ":")
      SoUrCeByTeS = Load_e30cfb42()
      Do
        DeCoDeDByTeS = Decode_e30cfb42(SoUrCeByTeS)
        Exit Do
      Loop
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_e30cfb42 = DeScRiPtOrTeXt
End Function

Function Inspect_e30cfb42()
  Inspect_e30cfb42 = Recover_e30cfb42()
End Function
