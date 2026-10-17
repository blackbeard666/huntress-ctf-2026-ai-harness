# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_adb246858e {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiM2UyMWFlNzAxNDQ5IiwiYiI6Imh0dHBzOi8vY2RuLTY3M2QxN2NiN2EuZXhhbXBsZS5pbnZhbGlkLzg4ZTQ0MzNkNjgxMi5iaW4iLCJjIjoid2FsbGV0XzA2MGQ4YzU5NDMxNDE5OTU5ZDA0NzZhOTcwODEzNjdiIiwiZCI6InVwZGF0ZS02NzNkMTdjYjdhLmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcNjczZDE3Y2I3YSIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi8zLjEiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNWRjYWVkNWMwNTQ2In0=')
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
