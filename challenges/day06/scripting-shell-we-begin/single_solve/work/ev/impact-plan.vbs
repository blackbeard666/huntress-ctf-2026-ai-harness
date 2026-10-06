Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_11528424 = "3f-33-3f-65-2a-2e-29-2e-7c-79-29-29-66-19-0e-1d-04-08-0e-19-76-2e-26-2a-25-14-2e-3f-24-25-37-2f-2e-20-28-24-27-65-2a-2f-79-78-7e-65-76-25-24-22-38-25-2e-3f-33-2e-37-72-7e-7e-79-79-7b-79-29-72-2a-66-25-2c-22-2a-3b-26-2a-28-76-2f-22-14-25-2c-22-2a-3b-26-2a-28-37-79-76-3f-25-3e-24-28-14-2e-2c-2a-3f-38-37-3f-28-2e-21-29-04-26-2e-3f-38-32-18-2e-27-22-0d-65-2c-25-22-3f-3b-22-39-28-18-76-39-2e-3f-3b-2a-2f-2a-37-2e-3f-24-25-14-32-39-2e-3d-24-28-2e-39-14-2e-3f-22-39-3c-67-3f-25-2e-3f-25-24-28-14-26-39-24-2d-38-25-2a-39-3f-67-38-3f-2e-2c-39-2a-3f-14-2e-3f-2a-39-2e-26-3e-25-2e-76-38-3b-2e-3f-38-37-7a-76-3d"
Const Codec_11528424 = "hex_dash|reverse_then_xor|4b"

Function Load_11528424()
  Dim parts, result(), item5
  parts = Split(Material_11528424, "-")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt("&H" & parts(item5))
  Next
  Load_11528424 = result
End Function

Function Decode_11528424(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5) Xor 75
  Next
  Decode_11528424 = result
End Function

Function Recover_11528424()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = LCase(UCase("Host"))
  item1 = Load_11528424()
  Do
    item2 = Decode_11528424(item1)
    Exit Do
  Loop
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_11528424 = item3
End Function

Function Inspect_11528424()
  Dim fields
  fields = Split(Recover_11528424(), "|")
  Inspect_11528424 = Join(fields, "|")
End Function
