Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_608cc4be = "7478742e66376564366462372d5245564f4345523d656d616e5f65746f6e7c64656b636f6c2e35363837642e3d6e6f69736e657478657c346331666663326164342d6e676961706d61633d64695f6e676961706d61637c323d746e756f635f65676174737c6d61657274532e42444f44413d726574706164617c65746f6e5f797265766f6365725f65746972772c746e65746e6f635f6d726f66736e6172742c737465677261745f65746172656d756e653d73706574737c313d76"
Const Codec_608cc4be = "hex_compact|reverse_bytes|"

Function Load_608cc4be()
  Dim result(), item5
  ReDim result((Len(Material_608cc4be) \ 2) - 1)
  For item5 = 0 To UBound(result)
    result(item5) = CInt("&H" & Mid(Material_608cc4be, item5 * 2 + 1, 2))
  Next
  Load_608cc4be = result
End Function

Function Decode_608cc4be(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5)
  Next
  Decode_608cc4be = result
End Function

Function Recover_608cc4be()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
item4 = (19 * 7) - 133
  item1 = Load_608cc4be()
  Do
    item2 = Decode_608cc4be(item1)
    Exit Do
  Loop
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_608cc4be = item3
End Function

Function Inspect_608cc4be()
  Dim fields
  fields = Split(Recover_608cc4be(), "|")
  Inspect_608cc4be = Join(fields, "|")
End Function
