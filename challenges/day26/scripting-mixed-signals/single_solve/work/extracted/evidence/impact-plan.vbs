Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_05c05499 = "81483c877e7f707b7e4870798078707d6c7f706a7f6c7d72707f7e377f7d6c797e717a7d786a6e7a797f70797f37827d747f706a7d706e7a81707d846a797a7f70876c6f6c7b7f707d484c4f5a4f4d395e7f7d706c78877e7f6c72706a6e7a80797f483d876e6c787b6c7472796a746f486e6c787b6c7472793840703e6d4271414042448770837f70797e747a7948393d40706f4439777a6e76706f87797a7f706a796c7870485d504e5a61505d386f3c4044443e6e3c397f837f"
Const Codec_05c05499 = "hex_compact|add_modulo_256|0b"

Function Load_05c05499()
  Dim result(), i
  ReDim result((Len(Material_05c05499) \ 2) - 1)
  For i = 0 To UBound(result)
    result(i) = CInt("&H" & Mid(Material_05c05499, i * 2 + 1, 2))
  Next
  Load_05c05499 = result
End Function

Function Decode_05c05499(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) - 11 + 256) Mod 256
  Next
  Decode_05c05499 = result
End Function

Function Recover_05c05499()
  Dim s, d, t, n, i, p, e, q
  n = Join(Array("north", "south"), ":")

  s = Load_05c05499()

  For p = 0 To 0

    d = Decode_05c05499(s)

  Next

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_05c05499 = t
End Function

Function Inspect_05c05499()
  Inspect_05c05499 = Recover_05c05499()
End Function
