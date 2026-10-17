# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_a9b7458b40 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYTQ1NGE5NGM1Mjc5IiwiYiI6Imh0dHBzOi8vY2RuLTcxMWJmMWQzZDcuZXhhbXBsZS5pbnZhbGlkL2M2M2NkZDQzODU1Zi5iaW4iLCJjIjpbInVwZGF0ZS03MTFiZjFkM2Q3LmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS1hNDU0YTk0YzUyNzkuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfODIyNGU0MjAzZDYyIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzMuNyJ9')
  $reconstruct = {
    param([byte[]]$candidateBytes)
    return [byte[]]$candidateBytes
  }
  [byte[]]$plainMaterial = @(& $reconstruct $encodedMaterial)
  $decodedText = [Text.Encoding]::UTF8.GetString($plainMaterial)
  $descriptor = $decodedText | ConvertFrom-Json
  $record = $descriptor
  $nativeTypes = @([IO.File],[IO.Compression.ZipFile],[Net.HttpWebRequest])
  [pscustomobject]@{ A = $record.a; B = $record.b; C = $record.c; D = $record.d; Native = $nativeTypes }
}
