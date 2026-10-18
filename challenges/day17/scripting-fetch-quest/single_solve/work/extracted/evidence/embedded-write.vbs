Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_75ec5704 = "74-61-64-2e-37-36-37-34-62-33-64-30-31-37-2d-65-67-61-74-73-5c-62-61-4c-73-73-65-72-74-6e-75-48-5c-63-69-6c-62-75-50-5c-73-72-65-73-55-5c-3a-43-3d-68-74-61-70-5f-65-6c-69-66-7c-37-36-37-34-62-33-64-30-31-37-2d-6e-67-69-61-70-6d-61-63-3d-64-69-5f-6e-67-69-61-70-6d-61-63-7c-32-3d-74-6e-75-6f-63-5f-65-67-61-74-73-7c-74-63-65-6a-62-4f-6d-65-74-73-79-53-65-6c-69-46-2e-67-6e-69-74-70-69-72-63-53-3d-72-65-74-70-61-64-61-7c-65-6c-69-66-5f-65-74-69-72-77-2c-64-65-64-64-65-62-6d-65-5f-65-64-6f-63-65-64-3d-73-70-65-74-73-7c-31-3d-76"
Const Codec_75ec5704 = "hex_dash|reverse_bytes|"

Function Load_75ec5704()
  Dim parts, result(), i
  parts = Split(Material_75ec5704, "-")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt("&H" & parts(i))
  Next
  Load_75ec5704 = result
End Function

Function Decode_75ec5704(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(UBound(s) - i) = s(i)
  Next
  Decode_75ec5704 = result
End Function

Function Recover_75ec5704()
  Dim s, d, t, n, i, p, e, q
  ' configuration reconstruction
n = Empty
  s = Load_75ec5704()
  On Error Resume Next
  d = Decode_75ec5704(s)
  e = Err.Number
  q = Err.Description
  On Error GoTo 0
  If e <> 0 Then Err.Raise e, "HuntressFixture", q
  t = ""
  For i = 0 To UBound(d)
    t = t & Chr(d(i))
  Next
' reconstruction complete
  Recover_75ec5704 = t
End Function

Sub Copy_75ec5704(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_75ec5704()
  Dim resultText
  Call Copy_75ec5704(Recover_75ec5704(), resultText)
  Inspect_75ec5704 = resultText
End Function
