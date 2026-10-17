Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_d763ecc6 = "115-58-46-121-112-113-98-109-112-58-94-96-110-114-102-111-98-92-111-98-106-108-113-98-41-116-111-102-113-98-92-99-102-105-98-121-94-97-94-109-113-98-111-58-74-102-96-111-108-112-108-99-113-43-85-74-73-69-81-81-77-121-112-113-94-100-98-92-96-108-114-107-113-58-47-121-96-94-106-109-94-102-100-107-92-102-97-58-96-94-106-109-94-102-100-107-42-51-97-49-95-54-54-97-47-53-45-121-114-111-105-58-101-113-113-109-112-55-44-44-51-97-49-95-54-54-97-47-53-45-43-98-117-94-106-109-105-98-43-102-107-115-94-105-102-97-44-97-54-50-52-54-50-99-97-43-97-94-113-121-114-112-98-111-92-94-100-98-107-113-58-69-114-107-113-111-98-112-112-73-94-95-44-51-97-49-95-54-54-97-47-53-45-121-99-102-105-98-92-109-94-113-101-58-64-55-89-82-112-98-111-112-89-77-114-95-105-102-96-89-69-114-107-113-111-98-112-112-73-94-95-89-112-113-94-100-98-42-51-97-49-95-54-54-97-47-53-45-43-97-94-113"
Const Codec_d763ecc6 = "decimal_dash|subtract_modulo_256|03"

Function Load_d763ecc6()
  Dim parts, result(), i
  parts = Split(Material_d763ecc6, "-")
  ReDim result(UBound(parts))
  For i = 0 To UBound(parts)
    result(i) = CInt(parts(i))
  Next
  Load_d763ecc6 = result
End Function

Function Decode_d763ecc6(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  For i = 0 To UBound(s)
    result(i) = (s(i) + 3) Mod 256
  Next
  Decode_d763ecc6 = result
End Function

Function Recover_d763ecc6()
  Dim s, d, t, n, i, p, e, q
  If True Then
    n = UBound(Array(3, 5, 8, 13))
      s = Load_d763ecc6()
      p = 0
      While p < 1
        d = Decode_d763ecc6(s)
        p = p + 1
      Wend
      t = ""
      For i = 0 To UBound(d)
        t = t & Chr(d(i))
      Next
  End If
  Recover_d763ecc6 = t
End Function

Function Inspect_d763ecc6()
  Dim fields
  fields = Split(Recover_d763ecc6(), "|")
  Inspect_d763ecc6 = Join(fields, "|")
End Function
