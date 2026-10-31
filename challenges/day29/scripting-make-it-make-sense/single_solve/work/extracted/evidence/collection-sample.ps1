# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_ec94d2f564 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMjU1MjI2NzVmM2M5IiwiYiI6Imh0dHBzOi8vY2RuLWQ1MWYxN2ZlMDMuZXhhbXBsZS5pbnZhbGlkLzkyODk4MjNjYzJhMi5iaW4iLCJjIjpbInVwZGF0ZS1kNTFmMTdmZTAzLmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS0yNTUyMjY3NWYzYzkuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfMzM2YjczNDQzYWVlIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzMuMSJ9')
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
