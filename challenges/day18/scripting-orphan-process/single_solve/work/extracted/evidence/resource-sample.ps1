# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_a2f31a9ff6 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYWI1NDI5ZjEzNGUyIiwiYiI6Imh0dHBzOi8vY2RuLTRkMzc2ZDRlNzEuZXhhbXBsZS5pbnZhbGlkLzUwY2I4NjEyNWYyNi5iaW4iLCJjIjoid2FsbGV0XzM4NWY5YzJlMWI3ZDdlMzhiOGRmYTU1MTY3NjRjZDgwIiwiZCI6InVwZGF0ZS00ZDM3NmQ0ZTcxLmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcNGQzNzZkNGU3MSIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi83LjUiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNjUxMTZjNjExOWU2In0=')
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
