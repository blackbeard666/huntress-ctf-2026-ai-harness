Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_ea5cd939 = "94:5b:4f:9a:91:92:83:8e:91:5b:82:83:81:8d:82:83:7d:81:8d:8c:84:87:85:93:90:7f:92:87:8d:8c:4a:90:83:92:93:90:8c:7d:81:8d:8c:84:87:85:93:90:7f:92:87:8d:8c:9a:7f:82:7f:8e:92:83:90:5b:71:81:90:87:8e:92:87:8c:85:4c:64:87:8a:83:71:97:91:92:83:8b:6d:80:88:83:81:92:9a:91:92:7f:85:83:7d:81:8d:93:8c:92:5b:4f:9a:81:7f:8b:8e:7f:87:85:8c:7d:87:82:5b:81:7f:8b:8e:7f:87:85:8c:4b:57:82:57:55:83:53:52:83:51:80:9a:86:8d:91:92:7d:87:82:5b:86:8d:91:92:4b:57:82:57:55:83:53:52:83:51:80"
Const Codec_ea5cd939 = "hex_colon|add_modulo_256|1e"

Function Load_ea5cd939()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_ea5cd939, ":")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt("&H" & parts(ByTeInDeX))
  Next
  Load_ea5cd939 = result
End Function

Function Decode_ea5cd939(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = (SoUrCeByTeS(ByTeInDeX) - 30 + 256) Mod 256
  Next
  Decode_ea5cd939 = result
End Function

Function Recover_ea5cd939()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  ' configuration reconstruction
NeUtRaL = Empty
  SoUrCeByTeS = Load_ea5cd939()
  Do
    DeCoDeDByTeS = Decode_ea5cd939(SoUrCeByTeS)
    Exit Do
  Loop
  DeScRiPtOrTeXt = ""
  For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
    DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
  Next
' reconstruction complete
  Recover_ea5cd939 = DeScRiPtOrTeXt
End Function

Sub Copy_ea5cd939(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_ea5cd939()
  Dim resultText
  Call Copy_ea5cd939(Recover_ea5cd939(), resultText)
  Inspect_ea5cd939 = resultText
End Function
