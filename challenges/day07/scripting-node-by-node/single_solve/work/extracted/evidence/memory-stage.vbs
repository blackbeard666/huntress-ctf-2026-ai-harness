Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_23238993 = "126-69-57-132-123-124-109-120-123-69-105-107-121-125-113-122-109-103-122-109-117-119-124-109-52-108-113-123-120-105-124-107-112-103-117-109-117-119-122-129-132-105-108-105-120-124-109-122-69-85-91-96-85-84-58-54-96-85-84-80-92-92-88-54-62-54-56-132-123-124-105-111-109-103-107-119-125-118-124-69-58-132-107-105-117-120-105-113-111-118-103-113-108-69-107-105-117-120-105-113-111-118-53-60-58-64-57-60-62-61-110-62-60-132-125-122-116-69-112-124-124-120-123-66-55-55-60-58-64-57-60-62-61-110-62-60-54-109-128-105-117-120-116-109-54-113-118-126-105-116-113-108-55-63-109-58-62-105-106-105-108-54-108-105-124-132-125-123-109-122-103-105-111-109-118-124-69-80-125-118-124-122-109-123-123-84-105-106-55-60-58-64-57-60-62-61-110-62-60"
Const Codec_23238993 = "decimal_dash|add_modulo_256|08"

Function Load_23238993()
  Dim parts, result(), materialIndex
  parts = Split(Material_23238993, "-")
  ReDim result(UBound(parts))
  For materialIndex = 0 To UBound(parts)
    result(materialIndex) = CInt(parts(materialIndex))
  Next
  Load_23238993 = result
End Function

Function Decode_23238993(ByRef storedMaterial)
  Dim result(), materialIndex, keyBytes, previous
  ReDim result(UBound(storedMaterial))
  For materialIndex = 0 To UBound(storedMaterial)
    result(materialIndex) = (storedMaterial(materialIndex) - 8 + 256) Mod 256
  Next
  Decode_23238993 = result
End Function

Function Recover_23238993()
  Dim storedMaterial, recoveredMaterial, configurationText, harmlessValue, materialIndex, decodePass, savedError, savedDescription
  If True Then
    harmlessValue = (19 * 7) - 133
      storedMaterial = Load_23238993()
      Select Case 1
        Case 1
          recoveredMaterial = Decode_23238993(storedMaterial)
        Case Else
          recoveredMaterial = Array()
      End Select
      configurationText = ""
      For materialIndex = 0 To UBound(recoveredMaterial)
        configurationText = configurationText & Chr(recoveredMaterial(materialIndex))
      Next
  End If
  Recover_23238993 = configurationText
End Function

Function Inspect_23238993()
  Dim fields
  fields = Split(Recover_23238993(), "|")
  Inspect_23238993 = Join(fields, "|")
End Function
