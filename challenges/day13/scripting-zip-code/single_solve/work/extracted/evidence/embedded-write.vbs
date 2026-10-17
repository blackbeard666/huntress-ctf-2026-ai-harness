Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_9195d6af = "74-61-64-2e-35-36-39-63-32-66-39-61-36-37-2d-65-67-61-74-73-5c-62-61-4c-73-73-65-72-74-6e-75-48-5c-63-69-6c-62-75-50-5c-73-72-65-73-55-5c-3a-43-3d-68-74-61-70-5f-65-6c-69-66-7c-35-36-39-63-32-66-39-61-36-37-2d-6e-67-69-61-70-6d-61-63-3d-64-69-5f-6e-67-69-61-70-6d-61-63-7c-32-3d-74-6e-75-6f-63-5f-65-67-61-74-73-7c-6d-61-65-72-74-53-2e-42-44-4f-44-41-3d-72-65-74-70-61-64-61-7c-65-6c-69-66-5f-65-74-69-72-77-2c-64-65-64-64-65-62-6d-65-5f-65-64-6f-63-65-64-3d-73-70-65-74-73-7c-31-3d-76"
Const Codec_9195d6af = "hex_dash|reverse_bytes|"

Function Load_9195d6af()
  Dim parts, result(), i
  parts = Split(Material_9195d6af, "-")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt("&H" & parts(i))
  Next
  Load_9195d6af = result
End Function

Function Decode_9195d6af(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(UBound(s) - i) = s(i)
  Next
  Decode_9195d6af = result
End Function

Function Recover_9195d6af()
  Dim s, d, t, n, i, p, e, q
  ' configuration reconstruction
n = (19 * 7) - 133
  s = Load_9195d6af()
  Select Case 1
    Case 1
      d = Decode_9195d6af(s)
    Case Else
      d = Array()
  End Select
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
' reconstruction complete
  Recover_9195d6af = t
End Function

Sub Copy_9195d6af(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_9195d6af()
  Dim resultText
  Call Copy_9195d6af(Recover_9195d6af(), resultText)
  Inspect_9195d6af = resultText
End Function
