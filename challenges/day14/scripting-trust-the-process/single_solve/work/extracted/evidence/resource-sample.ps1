# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_ca9194b88d {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYTdhYTBiMWFhNWY0IiwiYiI6Imh0dHBzOi8vY2RuLWNiNjU4YTlkZmIuZXhhbXBsZS5pbnZhbGlkL2IxNWU0OWI0ZjU5My5iaW4iLCJjIjoid2FsbGV0XzRlMTczN2VjYzM2NDQ3NzU3MDljNzhiNjhjZTA3MGVlIiwiZCI6InVwZGF0ZS1jYjY1OGE5ZGZiLmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcY2I2NThhOWRmYiIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi8zLjEiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfMGU1ZTVhYjU4ZTRhIn0=')
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
