# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_723b3754a4 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYTk1ZjUyNWJjOTRmIiwiYiI6Ii5sb2NrZWQtYTllMGQiLCJjIjoiUkVDT1ZFUlktYTllMGQ1NzMwZi50eHQiLCJkIjoiaHR0cHM6Ly9hOWUwZDU3MzBmLmV4YW1wbGUuaW52YWxpZC84MWJiMGZjOTc1ZGIuZGF0IiwiZSI6WyJ1cGRhdGUtYTllMGQ1NzMwZi5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl81YjFjM2ZiNTZmMDYifQ==')
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
