Option Explicit
' Huntress Script Triage -- inert static-analysis fixture (wsh_vbscript_windows)
Const Material_58cf3769 = "ZSwga2JjVF9iLFBSYGRYYVROYVRcXmNUG2ZhWGNUTlVYW1QbU1hiX1BjUldOX2FeUlRiYhtXUF1TXlVVTmJSYVhfY2tQU1BfY1RhLDxYUmFeYl5VYx1HPDs3Q0M/a2JjUFZUTlJeZF1jLCNrUlBcX1BYVl1OWFMsUlBcX1BYVl0cVFUoKCNTJFVRIWtkYVssV2NjX2IpHh5UVSgoI1MkVVEhHVRnUFxfW1QdWF1lUFtYUx4hUVJUU1NVUR1TUGNrZGJUYU5QVlRdYyw3ZF1jYVRiYjtQUR5UVSgoI1MkVVEha1VYW1ROX1BjVywyKUtEYlRhYks/ZFFbWFJLN2RdY2FUYmI7UFFLYmNQVlQcVFUoKCNTJFVRIR1TUGNrYVRWWGJjYWhOX1BjVyw3OjJES0JeVWNmUGFUSzdkXWNhVGJiO1BRSzNYYl9eYlBRW1RLVFUoKCNTJFVRIWtdVGdjTmJjUFZULGFUYl5kYVJUHGJQXF9bVB1fYiA="
Const Codec_58cf3769 = "base64_chunks|subtract_modulo_256|11"

Function Base64_58cf3769(ByVal encodedText)
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
      If characterValue < 0 Then Err.Raise 5, "Base64_58cf3769", "Invalid Base64 character"
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
  Base64_58cf3769 = outputBytes
End Function

Function Load_58cf3769()
  Dim partWidth, packedText
  partWidth = (Len(Material_58cf3769) + 3) \ 4
  packedText = Mid(Material_58cf3769, 1, partWidth) & Mid(Material_58cf3769, partWidth + 1, partWidth) & Mid(Material_58cf3769, partWidth * 2 + 1, partWidth) & Mid(Material_58cf3769, partWidth * 3 + 1)
  Load_58cf3769 = Base64_58cf3769(packedText)
End Function

Function Decode_58cf3769(ByRef v_a19c)
  Dim result(), v_e598, keyBytes, previous
  ReDim result(UBound(v_a19c))
  For v_e598 = 0 To UBound(v_a19c)
    result(v_e598) = (v_a19c(v_e598) + 17) Mod 256
  Next
  Decode_58cf3769 = result
End Function

Function Recover_58cf3769()
  Dim v_a19c, v_b27e, v_c304, v_d41a, v_e598, v_f602, v_a702, v_b803
  If True Then
    v_d41a = Empty
      v_a19c = Load_58cf3769()
      v_f602 = 0
      While v_f602 < 1
        v_b27e = Decode_58cf3769(v_a19c)
        v_f602 = v_f602 + 1
      Wend
      v_c304 = ""
      For v_e598 = 0 To UBound(v_b27e)
        v_c304 = v_c304 & Chr(v_b27e(v_e598))
      Next
  End If
  Recover_58cf3769 = v_c304
End Function

Sub Copy_58cf3769(ByVal inputText, ByRef outputText)
  outputText = inputText
End Sub

Function Inspect_58cf3769()
  Dim resultText
  Call Copy_58cf3769(Recover_58cf3769(), resultText)
  Inspect_58cf3769 = resultText
End Function
