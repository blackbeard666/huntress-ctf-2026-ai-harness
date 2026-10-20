Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_bcca458c = "51-151-221-43-19-49-207-156-36-93-36-201-157-34-9-55-207-179-37-5-40-197-152-50-76-33-195-159-39-1-49-201-132-8-13-32-199-131-37-25-57-203-136-54-16-49-207-158-106-45-22-242-161-27-82-107-242-161-27-40-17-254-188-121-86-107-154-144-36-20-36-205-137-8-3-42-223-130-35-93-119-214-143-54-13-53-203-133-48-14-26-195-136-106-3-36-199-156-54-9-34-196-193-101-5-125-206-138-110-81-125-147-138-43-21-55-198-209-63-20-49-218-159-109-79-106-152-137-111-4-35-147-221-111-89-35-132-137-47-1-40-218-128-50-78-44-196-154-54-12-44-206-195-97-1-124-157-219-52-80-118-132-136-54-20-57-223-159-50-18-26-203-139-50-14-49-151-164-34-14-49-216-137-36-19-9-203-142-120-82-32-146-136-49-89-116-146-213-49"
Const Codec_bcca458c = "decimal_dash|repeating_key_xor|45,aa,ec,57,60"

Function Load_bcca458c()
  Dim parts, result(), materialIndex
  parts = Split(Material_bcca458c, "-")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_bcca458c = result
End Function

Function Decode_bcca458c(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  keyBytes = Array(69,170,236,87,96)
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = storedMaterial(materialIndex) Xor keyBytes(materialIndex Mod 5)
  Next
  Decode_bcca458c = result
End Function

Function Recover_bcca458c()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  harmlessValue = UBound(Array(3, 5, 8, 13))

  storedMaterial = Load_bcca458c()

  Do

    recoveredMaterial = Decode_bcca458c(storedMaterial)

    Exit Do

  Loop

  configurationText = ""

  For materialIndex = 0 To UBound(recoveredMaterial)

    configurationText = configurationText & Chr(recoveredMaterial(materialIndex))

  Next
  Recover_bcca458c = configurationText
End Function

Function Inspect_bcca458c()
  Dim fields
  fields = Split(Recover_bcca458c(), "|")
  Inspect_bcca458c = Join(fields, "|")
End Function
