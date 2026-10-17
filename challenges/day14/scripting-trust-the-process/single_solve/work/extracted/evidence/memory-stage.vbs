Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_871e9cc9 = "33-30-31-64-39-64-61-38-62-66-2f-62-61-4c-73-73-65-72-74-6e-75-48-3d-74-6e-65-67-61-5f-72-65-73-75-7c-74-61-64-2e-31-63-65-38-66-31-33-61-2f-64-69-6c-61-76-6e-69-2e-65-6c-70-6d-61-78-65-2e-33-30-31-64-39-64-61-38-62-66-2f-2f-3a-73-70-74-74-68-3d-6c-72-75-7c-33-30-31-64-39-64-61-38-62-66-2d-6e-67-69-61-70-6d-61-63-3d-64-69-5f-6e-67-69-61-70-6d-61-63-7c-32-3d-74-6e-75-6f-63-5f-65-67-61-74-73-7c-31-2e-35-2e-74-73-65-75-71-65-52-70-74-74-48-6e-69-57-2e-70-74-74-48-6e-69-57-3d-72-65-74-70-61-64-61-7c-79-72-6f-6d-65-6d-5f-68-63-74-61-70-73-69-64-2c-65-74-6f-6d-65-72-5f-65-72-69-75-71-63-61-3d-73-70-65-74-73-7c-31-3d-76"
Const Codec_871e9cc9 = "hex_dash|reverse_bytes|"

Function Load_871e9cc9()
  Dim parts, result(), item5
  parts = Split(Material_871e9cc9, "-")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt("&H" & parts(item5))
  Next
  Load_871e9cc9 = result
End Function

Function Decode_871e9cc9(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5)
  Next
  Decode_871e9cc9 = result
End Function

Function Recover_871e9cc9()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If True Then
    item4 = LCase(UCase("Host"))
      item1 = Load_871e9cc9()
      On Error Resume Next
      item2 = Decode_871e9cc9(item1)
      item7 = Err.Number
      item8 = Err.Description
      On Error GoTo 0
      If item7 <> 0 Then Err.Raise item7, "HuntressFixture", item8
      item3 = ""
      For item5 = 0 To UBound(item2)
        item3 = item3 & Chr(item2(item5))
      Next
  End If
  Recover_871e9cc9 = item3
End Function

Function Inspect_871e9cc9()
  Dim fields
  fields = Split(Recover_871e9cc9(), "|")
  Inspect_871e9cc9 = Join(fields, "|")
End Function
