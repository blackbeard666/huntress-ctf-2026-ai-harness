Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_fcb62e2d = "176,141,188,192,179,199,162,210,161,156,253,158,239,154,243,129,228,187,201,172,193,174,218,191,147,228,150,255,139,238,177,215,190,210,183,203,170,206,175,223,171,206,188,129,204,159,199,138,198,244,218,130,207,131,203,159,203,155,181,131,173,157,225,146,230,135,224,133,218,185,214,163,205,185,132,182,202,169,200,165,213,180,221,186,212,139,226,134,187,216,185,212,164,197,172,203,165,136,177,133,224,211,183,132,182,143,189,139,247,130,240,156,161,201,189,201,185,202,240,223,240,201,253,152,171,207,252,206,247,197,243,221,184,192,161,204,188,208,181,155,242,156,234,139,231,142,234,197,166,195,245,144,166,145,245,147,189,217,184,204,176,197,182,211,161,254,159,248,157,243,135,186,242,135,233,157,239,138,249,138,198,167,197,234,211,231,130,177,213,230,212,237,223,233,149,243,154,246,147,204,188,221,169,193,252,191,133,217,140,255,154,232,155,199,151,226,128,236,133,230,186,242,135,233,157,239,138,249,138,198,167,197,153,234,158,255,152,253,208,233,221,184,139,239,220,238,215,229,211,253,153,248,140"
Const Codec_fcb62e2d = "decimal_comma|rolling_xor|c6"

Function Load_fcb62e2d()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_fcb62e2d, ",")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_fcb62e2d = result
End Function

Function Decode_fcb62e2d(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  previous = 198
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor previous
    previous = SoUrCeByTeS(ByTeInDeX)
  Next
  Decode_fcb62e2d = result
End Function

Function Recover_fcb62e2d()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  NeUtRaL = Join(Array("north", "south"), ":")

  SoUrCeByTeS = Load_fcb62e2d()

  On Error Resume Next

  DeCoDeDByTeS = Decode_fcb62e2d(SoUrCeByTeS)

  ErRoRnUmBeR = Err.Number

  ErRoRdEsCrIpTiOn = Err.Description

  On Error GoTo 0

  If ErRoRnUmBeR <> 0 Then Err.Raise ErRoRnUmBeR, "HuntressFixture", ErRoRdEsCrIpTiOn

  DeScRiPtOrTeXt = ""

  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)

    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))

  Next
  Recover_fcb62e2d = DeScRiPtOrTeXt
End Function

Function Inspect_fcb62e2d()
  Inspect_fcb62e2d = Recover_fcb62e2d()
End Function
