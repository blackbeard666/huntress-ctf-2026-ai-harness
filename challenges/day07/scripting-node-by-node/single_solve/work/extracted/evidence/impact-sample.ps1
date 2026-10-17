# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_7a2e73ed41 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMzk3YzExMDUyMDI0IiwiYiI6Ii5sb2NrZWQtMDJhNGIiLCJjIjoiUkVDT1ZFUlktMDJhNGJlNmEyOC50eHQiLCJkIjoiaHR0cHM6Ly8wMmE0YmU2YTI4LmV4YW1wbGUuaW52YWxpZC8zZjExMGZhY2I3MjEuZGF0IiwiZSI6WyJ1cGRhdGUtMDJhNGJlNmEyOC5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl82OWZmODY4NjExMjAifQ==')
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
