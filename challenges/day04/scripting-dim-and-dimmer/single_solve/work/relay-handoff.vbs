Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_0f8a0210 = "1b26176b186c09790a3756354431582a4f1062076a057114384f3d5420451a7c15791c30543d4e3e5f2b48207f0f7d12711467143850315f3b5432540b781b6900700478197d1c6c187d0f327f2c7439754769317c30782c782806301e2e522155345336690a65107e0a37037f1c7d106001680f613e57330e6d0c611170197e103d0e6d54350137013001324e3b49251870047000734966497a192041754375447546680d7514790965002e47295f3e523b5f704274122a122713230d69087c00750663114e2f482d43370a4237592d5f3a493a7617755a690a3352665066576655294f264a2f700061157d4003396530432654277b2b5e3c50395a064e3b5521533645367a1b792556224324416c5f3c05645066506150634d29483c40325730592a5e2c550a7a1b6f073a72397a2f73204f295d2a4b395c00483d5327553043307c1d7f23670e7d0d621170127e1b4774172e4f7b4d7b4a7b48345a3f47336c1f6b0a6d083559365534587511780b7b1a6e0d654b3d5f2c"
Const Codec_0f8a0210 = "hex_compact|rolling_xor|6d"

Function Load_0f8a0210()
  Dim result(), item5
  ReDim result((Len(Material_0f8a0210) \ 2) - 1)
  For item5 = 0 To UBound(result)
    result(item5) = CInt("&H" & Mid(Material_0f8a0210, item5 * 2 + 1, 2))
  Next
  Load_0f8a0210 = result
End Function

Function Decode_0f8a0210(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  previous = 109
  For item5 = 0 To UBound(item1)
    result(item5) = item1(item5) Xor previous
    previous = item1(item5)
  Next
  Decode_0f8a0210 = result
End Function

Function Recover_0f8a0210()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = LCase(UCase("Host"))

  item1 = Load_0f8a0210()

  Select Case 1

    Case 1

      item2 = Decode_0f8a0210(item1)

    Case Else

      item2 = Array()

  End Select

  item3 = ""

  For item5 = 0 To UBound(item2)

    item3 = item3 & Chr(item2(item5))

  Next
  Recover_0f8a0210 = item3
End Function

Sub Copy_0f8a0210(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_0f8a0210()
  Dim resultText
  Call Copy_0f8a0210(Recover_0f8a0210(), resultText)
  Inspect_0f8a0210 = resultText
End Function
