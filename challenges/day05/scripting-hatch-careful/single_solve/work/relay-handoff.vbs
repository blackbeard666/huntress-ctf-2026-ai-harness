Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_af055453 = "76-3d-31-7c-73-74-65-70-73-3d-61-63-71-75-69-72-65-5f-72-65-6d-6f-74-65-2c-77-72-69-74-65-5f-66-69-6c-65-2c-64-69-73-70-61-74-63-68-5f-70-72-6f-63-65-73-73-2c-68-61-6e-64-6f-66-66-5f-73-63-72-69-70-74-7c-61-64-61-70-74-65-72-3d-4d-53-58-4d-4c-32-2e-58-4d-4c-48-54-54-50-2e-36-2e-30-7c-73-74-61-67-65-5f-63-6f-75-6e-74-3d-34-7c-63-61-6d-70-61-69-67-6e-5f-69-64-3d-63-61-6d-70-61-69-67-6e-2d-62-32-31-62-38-62-31-34-65-65-7c-75-72-6c-3d-68-74-74-70-73-3a-2f-2f-62-32-31-62-38-62-31-34-65-65-2e-65-78-61-6d-70-6c-65-2e-69-6e-76-61-6c-69-64-2f-39-62-65-32-30-38-39-61-2e-64-61-74-7c-75-73-65-72-5f-61-67-65-6e-74-3d-48-75-6e-74-72-65-73-73-4c-61-62-2f-62-32-31-62-38-62-31-34-65-65-7c-66-69-6c-65-5f-70-61-74-68-3d-43-3a-5c-55-73-65-72-73-5c-50-75-62-6c-69-63-5c-48-75-6e-74-72-65-73-73-4c-61-62-5c-73-74-61-67-65-2d-62-32-31-62-38-62-31-34-65-65-2e-64-61-74-7c-72-65-67-69-73-74-72-79-5f-70-61-74-68-3d-48-4b-43-55-5c-53-6f-66-74-77-61-72-65-5c-48-75-6e-74-72-65-73-73-4c-61-62-5c-44-69-73-70-6f-73-61-62-6c-65-5c-62-32-31-62-38-62-31-34-65-65-7c-6e-65-78-74-5f-73-74-61-67-65-3d-6c-6f-63-61-6c-2d-64-69-73-70-61-74-63-68-2e-76-62-73"
Const Codec_af055453 = "hex_dash|identity|"

Function Load_af055453()
  Dim parts, result(), item5
  parts = Split(Material_af055453, "-")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt("&H" & parts(item5))
  Next
  Load_af055453 = result
End Function

Function Decode_af055453(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5)
  Next
  Decode_af055453 = result
End Function

Function Recover_af055453()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
item4 = Join(Array("north", "south"), ":")
  item1 = Load_af055453()
  Select Case 1
    Case 1
      item2 = Decode_af055453(item1)
    Case Else
      item2 = Array()
  End Select
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_af055453 = item3
End Function

Function Inspect_af055453()
  Inspect_af055453 = Recover_af055453()
End Function
