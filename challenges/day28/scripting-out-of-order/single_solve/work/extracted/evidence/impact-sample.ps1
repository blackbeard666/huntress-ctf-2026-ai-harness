# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_b3f256a93f {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiODFlMjczOTRmZDIwIiwiYiI6Ii5sb2NrZWQtODgxZTYiLCJjIjoiUkVDT1ZFUlktODgxZTZiZmYyMy50eHQiLCJkIjoiaHR0cHM6Ly84ODFlNmJmZjIzLmV4YW1wbGUuaW52YWxpZC84YjQ0NDlhYWQ3NDQuZGF0IiwiZSI6WyJ1cGRhdGUtODgxZTZiZmYyMy5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9jMmJhYzcwNWRlYTMifQ==')
  $reconstruct = {
    param([byte[]]$candidateBytes)
    return [byte[]]$candidateBytes
  }
  [byte[]]$plainMaterial = @(& $reconstruct $encodedMaterial)
  $decodedText = [Text.Encoding]::UTF8.GetString($plainMaterial)
  $descriptor = $decodedText | ConvertFrom-Json
  $record = $descriptor
  $nativeTypes = @([IO.File],[Security.Cryptography.Aes],[IO.DirectoryInfo])
  [pscustomobject]@{ A = $record.a; B = $record.b; C = $record.c; D = $record.d; Native = $nativeTypes }
}
