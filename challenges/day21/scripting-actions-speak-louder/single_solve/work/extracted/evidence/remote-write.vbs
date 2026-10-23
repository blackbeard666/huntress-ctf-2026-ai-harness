Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_0428aaef = "223|148|152|213|218|221|204|217|218|148|200|202|216|220|192|219|204|246|219|204|196|198|221|204|133|222|219|192|221|204|246|207|192|197|204|213|200|205|200|217|221|204|219|148|228|192|202|219|198|218|198|207|221|135|241|228|229|225|253|253|249|213|218|221|200|206|204|246|202|198|220|199|221|148|155|213|202|200|196|217|200|192|206|199|246|192|205|148|202|200|196|217|200|192|206|199|132|157|155|144|156|153|152|152|158|159|207|213|220|219|197|148|193|221|221|217|218|147|134|134|157|155|144|156|153|152|152|158|159|207|135|204|209|200|196|217|197|204|135|192|199|223|200|197|192|205|134|155|144|205|156|156|157|204|145|135|205|200|221|213|220|218|204|219|246|200|206|204|199|221|148|225|220|199|221|219|204|218|218|229|200|203|134|157|155|144|156|153|152|152|158|159|207|213|207|192|197|204|246|217|200|221|193|148|234|147|245|252|218|204|219|218|245|249|220|203|197|192|202|245|225|220|199|221|219|204|218|218|229|200|203|245|218|221|200|206|204|132|157|155|144|156|153|152|152|158|159|207|135|205|200|221"
Const Codec_0428aaef = "decimal_pipe|single_byte_xor|a9"

Function Load_0428aaef()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_0428aaef, "|")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_0428aaef = result
End Function

Function Decode_0428aaef(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor 169
  Next
  Decode_0428aaef = result
End Function

Function Recover_0428aaef()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    If (2 > 1) Then NeUtRaL = "left" Else NeUtRaL = "right"
      SoUrCeByTeS = Load_0428aaef()
      Do
        DeCoDeDByTeS = Decode_0428aaef(SoUrCeByTeS)
        Exit Do
      Loop
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_0428aaef = DeScRiPtOrTeXt
End Function

Function Inspect_0428aaef()
  Inspect_0428aaef = Recover_0428aaef()
End Function
