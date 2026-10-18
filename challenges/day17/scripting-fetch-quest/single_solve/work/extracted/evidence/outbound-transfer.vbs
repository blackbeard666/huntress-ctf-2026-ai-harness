Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_4ce4d148 = "102-55-57-56-101-98-49-101-47-100-97-111-108-112-117-47-100-105-108-97-118-110-105-46-101-108-112-109-97-120-101-46-48-51-55-99-55-98-56-51-51-51-47-47-58-115-112-116-116-104-61-108-114-117-95-100-97-111-108-112-117-124-116-97-100-46-48-51-55-99-55-98-56-51-51-51-45-101-103-97-116-115-92-98-97-76-115-115-101-114-116-110-117-72-92-99-105-108-98-117-80-92-115-114-101-115-85-92-58-67-61-104-116-97-112-95-101-108-105-102-124-48-51-55-99-55-98-56-51-51-51-47-98-97-76-115-115-101-114-116-110-117-72-61-116-110-101-103-97-95-114-101-115-117-124-116-97-100-46-98-49-98-101-53-49-102-56-47-100-105-108-97-118-110-105-46-101-108-112-109-97-120-101-46-48-51-55-99-55-98-56-51-51-51-47-47-58-115-112-116-116-104-61-108-114-117-124-48-51-55-99-55-98-56-51-51-51-45-110-103-105-97-112-109-97-99-61-100-105-95-110-103-105-97-112-109-97-99-124-50-61-116-110-117-111-99-95-101-103-97-116-115-124-101-120-101-46-113-101-82-116-114-101-67-61-114-101-116-112-97-100-97-124-101-116-111-109-101-114-95-100-97-111-108-112-117-44-114-101-102-115-110-97-114-116-95-101-114-97-112-101-114-112-44-108-97-99-111-108-95-101-116-97-99-111-108-61-115-112-101-116-115-124-49-61-118"
Const Codec_4ce4d148 = "decimal_dash|reverse_bytes|"

Function Load_4ce4d148()
  Dim parts, result(), item5
  parts = Split(Material_4ce4d148, "-")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_4ce4d148 = result
End Function

Function Decode_4ce4d148(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5)
  Next
  Decode_4ce4d148 = result
End Function

Function Recover_4ce4d148()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  item4 = Empty
  item1 = Load_4ce4d148()
  item2 = Decode_4ce4d148(item1)
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
  Recover_4ce4d148 = item3
End Function

Sub Copy_4ce4d148(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_4ce4d148()
  Dim resultText
  Call Copy_4ce4d148(Recover_4ce4d148(), resultText)
  Inspect_4ce4d148 = resultText
End Function
