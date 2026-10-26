# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_4a392908f7 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMDkzNjBjOWYzZGRiIiwiYiI6Ii5sb2NrZWQtYWIzNTAiLCJjIjoiUkVDT1ZFUlktYWIzNTBkYjMzOC50eHQiLCJkIjoiaHR0cHM6Ly9hYjM1MGRiMzM4LmV4YW1wbGUuaW52YWxpZC8yZTc2Y2JiNWNjMGEuZGF0IiwiZSI6WyJ1cGRhdGUtYWIzNTBkYjMzOC5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9iNGY1YjgzOGM5MzAifQ==')
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
