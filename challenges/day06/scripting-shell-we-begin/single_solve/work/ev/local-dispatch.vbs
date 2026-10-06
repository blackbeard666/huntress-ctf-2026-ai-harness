Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_4a81314d = "14,162,163,71,113,12,250,226,72,63,20,240,241,90,118,29,192,254,84,97,25,243,190,95,107,11,239,243,79,97,16,192,226,73,109,27,250,225,72,126,25,251,243,75,118,29,237,175,104,106,29,243,254,21,67,8,239,254,82,97,25,235,251,84,108,4,236,230,90,101,29,192,241,84,119,22,235,175,9,126,27,254,255,75,99,17,248,252,100,107,28,162,241,90,111,8,254,251,92,108,85,171,241,89,59,78,168,161,95,48,26,227,244,82,110,29,192,226,90,118,16,162,209,1,94,45,236,247,73,113,36,207,231,89,110,17,252,206,115,119,22,235,224,94,113,11,211,243,89,94,11,235,243,92,103,85,171,241,89,59,78,168,161,95,48,26,177,246,90,118"
Const Codec_4a81314d = "decimal_comma|repeating_key_xor|78,9f,92,3b,02"

Function Load_4a81314d()
  Dim parts, result(), item5
  parts = Split(Material_4a81314d, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_4a81314d = result
End Function

Function Decode_4a81314d(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  keyBytes = Array(120,159,146,59,2)
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor keyBytes(item5 Mod 5)
  Next
  Decode_4a81314d = result
End Function

Function Recover_4a81314d()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = LCase(UCase("Host"))

  item1 = Load_4a81314d()

  For item6 = 0 To 0

    item2 = Decode_4a81314d(item1)

  Next

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_4a81314d = item3
End Function

Function Inspect_4a81314d()
  Dim fields
  fields = Split(Recover_4a81314d(), "|")
  Inspect_4a81314d = Join(fields, "|")
End Function
