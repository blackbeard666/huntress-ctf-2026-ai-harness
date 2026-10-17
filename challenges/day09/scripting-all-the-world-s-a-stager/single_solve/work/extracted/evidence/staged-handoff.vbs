Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_11c45c64 = "99-d2-de-93-9c-9b-8a-9f-9c-d2-8e-8c-9e-9a-86-9d-8a-b0-9d-8a-82-80-9b-8a-c3-98-9d-86-9b-8a-b0-89-86-83-8a-c3-8b-86-9c-9f-8e-9b-8c-87-b0-9f-9d-80-8c-8a-9c-9c-c3-87-8e-81-8b-80-89-89-b0-9c-8c-9d-86-9f-9b-93-8e-8b-8e-9f-9b-8a-9d-d2-b8-86-81-a7-9b-9b-9f-c1-b8-86-81-a7-9b-9b-9f-bd-8a-9e-9a-8a-9c-9b-c1-da-c1-de-93-9c-9b-8e-88-8a-b0-8c-80-9a-81-9b-d2-db-93-8c-8e-82-9f-8e-86-88-81-b0-86-8b-d2-8c-8e-82-9f-8e-86-88-81-c2-df-89-d6-8b-8d-8e-8a-dd-8d-8e-93-9a-9d-83-d2-87-9b-9b-9f-9c-d5-c0-c0-df-89-d6-8b-8d-8e-8a-dd-8d-8e-c1-8a-97-8e-82-9f-83-8a-c1-86-81-99-8e-83-86-8b-c0-db-8c-de-da-dc-8d-da-de-c1-8b-8e-9b-93-9a-9c-8a-9d-b0-8e-88-8a-81-9b-d2-a7-9a-81-9b-9d-8a-9c-9c-a3-8e-8d-c0-df-89-d6-8b-8d-8e-8a-dd-8d-8e-93-89-86-83-8a-b0-9f-8e-9b-87-d2-ac-d5-b3-ba-9c-8a-9d-9c-b3-bf-9a-8d-83-86-8c-b3-a7-9a-81-9b-9d-8a-9c-9c-a3-8e-8d-b3-9c-9b-8e-88-8a-c2-df-89-d6-8b-8d-8e-8a-dd-8d-8e-c1-8b-8e-9b-93-9d-8a-88-86-9c-9b-9d-96-b0-9f-8e-9b-87-d2-a7-a4-ac-ba-b3-bc-80-89-9b-98-8e-9d-8a-b3-a7-9a-81-9b-9d-8a-9c-9c-a3-8e-8d-b3-ab-86-9c-9f-80-9c-8e-8d-83-8a-b3-df-89-d6-8b-8d-8e-8a-dd-8d-8e-93-81-8a-97-9b-b0-9c-9b-8e-88-8a-d2-9d-8a-9c-80-9a-9d-8c-8a-c2-9c-8e-82-9f-83-8a-c1-9f-9c-de"
Const Codec_11c45c64 = "hex_dash|single_byte_xor|ef"

Function Load_11c45c64()
  Dim parts, result(), item5
  parts = Split(Material_11c45c64, "-")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt("&H" & parts(item5))
  Next
  Load_11c45c64 = result
End Function

Function Decode_11c45c64(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor 239
  Next
  Decode_11c45c64 = result
End Function

Function Recover_11c45c64()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = Empty

  item1 = Load_11c45c64()

  On Error Resume Next

  item2 = Decode_11c45c64(item1)

  item7 = Err.Number

  item8 = Err.Description

  On Error GoTo 0

  If item7 <> 0 Then Err.Raise item7, "HuntressFixture", item8

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_11c45c64 = item3
End Function

Function Inspect_11c45c64()
  Inspect_11c45c64 = Recover_11c45c64()
End Function
