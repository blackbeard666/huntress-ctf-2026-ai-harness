Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_1dde599b = "218-231-214-170-217-173-200-184-203-246-151-244-133-240-153-235-142-209-163-198-171-196-176-213-249-142-252-149-225-132-219-189-212-184-221-161-192-164-197-181-193-164-214-235-166-207-172-222-177-194-173-203-191-145-201-132-200-128-212-128-208-172-223-171-202-173-200-151-244-155-238-128-244-201-251-135-228-133-232-152-249-144-247-153-198-175-203-246-149-244-153-233-136-225-134-232-197-164-149-161-145-160-145-167-146-160-146-238-155-233-133-184-208-164-208-160-211-233-198-233-136-185-141-189-140-189-139-190-140-190-144-245-141-236-129-241-157-248-214-191-209-167-198-170-195-167-136-177-134-178-138-235-210-229-134-168-204-173-217-165-208-163-198-180-235-138-237-136-230-146-175-231-146-252-136-250-159-236-159-211-178-208-255-158-175-155-171-154-171-157-168-154-168-212-178-219-183-210-141-253-156-232-128-189-254-196-152-205-190-219-169-218-134-214-163-193-173-196-167-251-179-198-168-220-174-203-184-203-135-230-132-216-171-223-190-217-188-145-240-193-245-197-244-197-243-198-244-198-232-140-237-153"
Const Codec_1dde599b = "decimal_dash|rolling_xor|ac"

Function Load_1dde599b()
  Dim parts, result(), i
  parts = Split(Material_1dde599b, "-")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt(parts(i))
  Next
  Load_1dde599b = result
End Function

Function Decode_1dde599b(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  previous = 172
  For i = 0 To UBound(s)
    result(i) = s(i) Xor previous
    previous = s(i)
  Next
  Decode_1dde599b = result
End Function

Function Recover_1dde599b()
  Dim s, d, t, n, i, p, e, q
  n = UBound(Array(3, 5, 8, 13))

  s = Load_1dde599b()

  p = 0

  While p < 1

    d = Decode_1dde599b(s)

    p = p + 1

  Wend

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_1dde599b = t
End Function

Function Inspect_1dde599b()
  Dim fields
  fields = Split(Recover_1dde599b(), "|")
  Inspect_1dde599b = Join(fields, "|")
End Function
