Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_5748aa1b = "243-184-180-249-246-241-224-245-246-184-224-235-240-232-224-247-228-241-224-218-241-228-247-226-224-241-246-169-241-247-228-235-246-227-234-247-232-218-230-234-235-241-224-235-241-169-242-247-236-241-224-218-247-224-230-234-243-224-247-252-218-235-234-241-224-249-228-225-228-245-241-224-247-184-214-230-247-236-245-241-236-235-226-171-195-236-233-224-214-252-246-241-224-232-202-231-239-224-230-241-249-246-241-228-226-224-218-230-234-240-235-241-184-183-249-230-228-232-245-228-236-226-235-218-236-225-184-230-228-232-245-228-236-226-235-168-182-189-224-183-176-230-179-189-182-225-249-224-253-241-224-235-246-236-234-235-184-171-228-180-178-188-224-171-233-234-230-238-224-225-249-235-234-241-224-218-235-228-232-224-184-215-192-198-202-211-192-215-168-181-183-227-228-228-179-180-228-171-241-253-241"
Const Codec_5748aa1b = "decimal_dash|single_byte_xor|85"

Function Load_5748aa1b()
  Dim parts, result(), ByTeInDeX
  parts = Split(Material_5748aa1b, "-")
  ReDim result(UBound(parts))
  For ByTeInDeX = 0 To UBound(parts)
    result(ByTeInDeX) = CInt(parts(ByTeInDeX))
  Next
  Load_5748aa1b = result
End Function

Function Decode_5748aa1b(ByRef SoUrCeByTeS)
  Dim result(), ByTeInDeX, keyBytes, previous
  ReDim result(UBound(SoUrCeByTeS))
  For ByTeInDeX = 0 To UBound(SoUrCeByTeS)
    result(ByTeInDeX) = SoUrCeByTeS(ByTeInDeX) Xor 133
  Next
  Decode_5748aa1b = result
End Function

Function Recover_5748aa1b()
  Dim SoUrCeByTeS, DeCoDeDByTeS, DeScRiPtOrTeXt, NeUtRaL, ByTeInDeX, PaSs, ErRoRnUmBeR, ErRoRdEsCrIpTiOn
  If True Then
    NeUtRaL = Join(Array("north", "south"), ":")
      SoUrCeByTeS = Load_5748aa1b()
      Select Case 1
        Case 1
          DeCoDeDByTeS = Decode_5748aa1b(SoUrCeByTeS)
        Case Else
          DeCoDeDByTeS = Array()
      End Select
      DeScRiPtOrTeXt = ""
      For ByTeInDeX = 0 To UBound(DeCoDeDByTeS)
        DeScRiPtOrTeXt = DeScRiPtOrTeXt & Chr(DeCoDeDByTeS(ByTeInDeX))
      Next
  End If
  Recover_5748aa1b = DeScRiPtOrTeXt
End Function

Function Inspect_5748aa1b()
  Dim fields
  fields = Split(Recover_5748aa1b(), "|")
  Inspect_5748aa1b = Join(fields, "|")
End Function
