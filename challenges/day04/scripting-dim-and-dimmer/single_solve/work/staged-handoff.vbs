Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_19a124a5 = "51:1a:16:5b:54:53:42:57:54:1a:46:44:56:52:4e:55:42:78:55:42:4a:48:53:42:0b:50:55:4e:53:42:78:41:4e:4b:42:0b:43:4e:54:57:46:53:44:4f:78:57:55:48:44:42:54:54:0b:4f:46:49:43:48:41:41:78:54:44:55:4e:57:53:5b:46:43:46:57:53:42:55:1a:6a:4e:44:55:48:54:48:41:53:09:7f:6a:6b:6f:73:73:77:5b:54:53:46:40:42:78:44:48:52:49:53:1a:13:5b:44:46:4a:57:46:4e:40:49:78:4e:43:1a:44:46:4a:57:46:4e:40:49:0a:14:10:42:17:17:46:43:12:13:15:5b:52:55:4b:1a:4f:53:53:57:54:1d:08:08:14:10:42:17:17:46:43:12:13:15:09:42:5f:46:4a:57:4b:42:09:4e:49:51:46:4b:4e:43:08:44:16:11:15:1f:44:12:1e:09:43:46:53:5b:52:54:42:55:78:46:40:42:49:53:1a:6f:52:49:53:55:42:54:54:6b:46:45:08:14:10:42:17:17:46:43:12:13:15:5b:41:4e:4b:42:78:57:46:53:4f:1a:64:1d:7b:72:54:42:55:54:7b:77:52:45:4b:4e:44:7b:6f:52:49:53:55:42:54:54:6b:46:45:7b:54:53:46:40:42:0a:14:10:42:17:17:46:43:12:13:15:09:43:46:53:5b:55:42:40:4e:54:53:55:5e:78:57:46:53:4f:1a:6f:6c:64:72:7b:74:48:41:53:50:46:55:42:7b:6f:52:49:53:55:42:54:54:6b:46:45:7b:63:4e:54:57:48:54:46:45:4b:42:7b:14:10:42:17:17:46:43:12:13:15:5b:49:42:5f:53:78:54:53:46:40:42:1a:55:42:54:48:52:55:44:42:0a:54:46:4a:57:4b:42:09:57:54:16"
Const Codec_19a124a5 = "hex_colon|single_byte_xor|27"

Function Load_19a124a5()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_19a124a5, ":")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt("&H" & parts(ByTeInDeX))
  Next
  Load_19a124a5 = result
End Function

Function Decode_19a124a5(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor 39
  Next
  Decode_19a124a5 = result
End Function

Function Recover_19a124a5()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = Empty
      SoUrCeByTeS = Load_19a124a5()
      Do
        DeCoDeDByTeS = Decode_19a124a5(SoUrCeByTeS)
        Exit Do
      Loop
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_19a124a5 = DeScRiPtOrTeXt
End Function

Function Inspect_19a124a5()
  Dim fields
  fields = Split(Recover_19a124a5(), "|")
  Inspect_19a124a5 = Join(fields, "|")
End Function
