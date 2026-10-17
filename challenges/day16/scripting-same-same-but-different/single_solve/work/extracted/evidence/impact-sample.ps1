# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_044fca6e7f {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZWQ0YTQ0ZWFkOWM5IiwiYiI6Ii5sb2NrZWQtMTllYzMiLCJjIjoiUkVDT1ZFUlktMTllYzM3ZDU1Yy50eHQiLCJkIjoiaHR0cHM6Ly8xOWVjMzdkNTVjLmV4YW1wbGUuaW52YWxpZC81MjM3MjYxNmI5MmYuZGF0IiwiZSI6WyJ1cGRhdGUtMTllYzM3ZDU1Yy5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9hM2YzY2RjNjYyMDYifQ==')
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
