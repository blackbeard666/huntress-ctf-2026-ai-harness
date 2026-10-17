Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_6f332145 = "df8a832f11ddd2c2205fc8d4c3260bdbd2ed2107c4d8c6364edec5db2707f6d1db3f07d5d6d63212ddd2c06e2ffaefff1f5087efff1f2afde3e27d548787ce2016c8d0d70c01c6c2dc275f9bcbd1320fd9d6db340cf6ded66e01c8dac2320bced99f3600cdd4866004ca82d62f17dbdb8f3b16ddc7c1694d86d2d037019d84d43057cd99d72b03c4c7de364cc0d9c4320ec0d39d6b529c83876350cb99d63216d5c2c13610f6d6d5360cdd8afa260cddc5d72011e5d6d07c07cbd3d16751cfd487371ecfdede363dd9d6c63b5fea8dee0611ccc5c10f32dcd5de3a01f5ffc73d16dbd2c1202ec8d5ee2016c8d0d77e07cbd3d16751cfd487374ccdd6c6"
Const Codec_6f332145 = "hex_compact|repeating_key_xor|a9,b7,b2,53,62"

Function Load_6f332145()
  Dim result(), v_e598
  ReDim result((Len(Material_6f332145) \ 2) - 1)
  For v_e598 = 0 To UBound(result)
    result(v_e598) = CInt("&H" & Mid(Material_6f332145, v_e598 * 2 + 1, 2))
  Next
  Load_6f332145 = result
End Function

Function Decode_6f332145(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  keyBytes = Array(169,183,178,83,98)
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor keyBytes(v_e598 Mod 5)
  Next
  Decode_6f332145 = result
End Function

Function Recover_6f332145()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  v_d41a = UBound(Array(3, 5, 8, 13))
  v_a19c = Load_6f332145()
  Do
    v_b27e = Decode_6f332145(v_a19c)
    Exit Do
  Loop
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_6f332145 = v_c304
End Function

Sub Copy_6f332145(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_6f332145()
  Dim resultText
  Call Copy_6f332145(Recover_6f332145(), resultText)
  Inspect_6f332145 = resultText
End Function
