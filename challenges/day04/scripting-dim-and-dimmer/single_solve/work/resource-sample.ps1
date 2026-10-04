# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_b67cb07368 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZmM2NjgzYWU3YTc3IiwiYiI6Imh0dHBzOi8vZDQxYzgzYzRiZi5leGFtcGxlLmludmFsaWQvYzNkZTY1NGY1ODkxLmRhdCIsImMiOiJ3YWxsZXRfNjczZjI4NGNlMTU3MDRjNjM4OWNlODg5MDEzYTI4YTQiLCJkIjoidXBkYXRlLWQ0MWM4M2M0YmYuZGF0IiwiZSI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcUnVuXFxkNDFjODNjNGJmIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzIuOCIsImciOjY0LCJoIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9iNzY1MzE0OTVkNWYifQ==')
  $reconstruct = {
    param([byte[]]$candidateBytes)
    return [byte[]]$candidateBytes
  }
  [byte[]]$plainMaterial = @(& $reconstruct $encodedMaterial)
  $decodedText = [Text.Encoding]::UTF8.GetString($plainMaterial)
  $descriptor = $decodedText | ConvertFrom-Json
  $record = $descriptor
  $nativeTypes = @([Diagnostics.Process],[Microsoft.Win32.Registry],[Net.WebClient])
  [pscustomobject]@{ A = $record.a; B = $record.b; C = $record.c; D = $record.d; Native = $nativeTypes }
}
