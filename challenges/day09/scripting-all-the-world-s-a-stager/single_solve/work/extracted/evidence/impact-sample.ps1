# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_7c56b68126 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMTljMjlhMmYzYjUwIiwiYiI6Ii5sb2NrZWQtZjc1NzYiLCJjIjoiUkVDT1ZFUlktZjc1NzY3Zjg5OC50eHQiLCJkIjoiaHR0cHM6Ly9mNzU3NjdmODk4LmV4YW1wbGUuaW52YWxpZC85MGQ3NmUzODMzMmIuZGF0IiwiZSI6WyJ1cGRhdGUtZjc1NzY3Zjg5OC5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl8yNzMwNjQxZTI3MGYifQ==')
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
