Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_621ecec5 = "3d-2c-38-60-26-2d-3a-2f-3e-3d-27-2a-63-22-2f-2d-21-22-73-2b-29-2f-3a-3d-11-3a-36-2b-20-32-2c-7f-7d-78-7d-79-79-7b-7c-79-12-2b-22-2c-2f-3d-21-3e-3d-27-0a-12-2c-2f-02-3d-3d-2b-3c-3a-20-3b-06-12-2b-3c-2f-39-3a-28-21-1d-12-1b-0d-05-06-73-26-3a-2f-3e-11-37-3c-3a-3d-27-29-2b-3c-32-3a-2f-2a-60-2c-7f-7d-78-7d-79-79-7b-7c-79-63-2b-29-2f-3a-3d-12-2c-2f-02-3d-3d-2b-3c-3a-20-3b-06-12-2d-27-22-2c-3b-1e-12-3d-3c-2b-3d-1b-12-74-0d-73-26-3a-2f-3e-11-2b-22-27-28-32-2c-7f-7d-78-7d-79-79-7b-7c-79-61-2c-2f-02-3d-3d-2b-3c-3a-20-3b-06-73-3a-20-2b-29-2f-11-3c-2b-3d-3b-32-3a-2f-2a-60-2a-7c-7a-7c-7d-2a-7e-7e-61-2a-27-22-2f-38-20-27-60-2b-22-3e-23-2f-36-2b-60-2c-7f-7d-78-7d-79-79-7b-7c-79-61-61-74-3d-3e-3a-3a-26-73-22-3c-3b-32-2c-7f-7d-78-7d-79-79-7b-7c-79-63-20-29-27-2f-3e-23-2f-2d-73-2a-27-11-20-29-27-2f-3e-23-2f-2d-32-7a-73-3a-20-3b-21-2d-11-2b-29-2f-3a-3d-32-7e-60-78-60-1e-1a-1a-06-02-03-16-60-7c-02-03-16-1d-03-73-3c-2b-3a-3e-2f-2a-2f-32-3a-3e-27-3c-2d-3d-11-28-28-21-2a-20-2f-26-62-3d-3d-2b-2d-21-3c-3e-11-26-2d-3a-2f-3e-3d-27-2a-62-2b-22-27-28-11-2b-3a-27-3c-39-62-2b-3a-21-23-2b-3c-11-2b-3c-27-3b-3f-2d-2f-73-3d-3e-2b-3a-3d-32-7f-73-38"
Const Codec_621ecec5 = "hex_dash|reverse_then_xor|4e"

Function Load_621ecec5()
  Dim parts, result(), item5
  parts = Split(Material_621ecec5, "-")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt("&H" & parts(item5))
  Next
  Load_621ecec5 = result
End Function

Function Decode_621ecec5(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5) Xor 78
  Next
  Decode_621ecec5 = result
End Function

Function Recover_621ecec5()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
item4 = Join(Array("north", "south"), ":")
  item1 = Load_621ecec5()
  Select Case 1
    Case 1
      item2 = Decode_621ecec5(item1)
    Case Else
      item2 = Array()
  End Select
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_621ecec5 = item3
End Function

Function Inspect_621ecec5()
  Inspect_621ecec5 = Recover_621ecec5()
End Function
