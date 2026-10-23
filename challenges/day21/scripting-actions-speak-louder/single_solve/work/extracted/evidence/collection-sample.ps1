# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_9b576378b4 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYmI0N2JiYWRhNDkwIiwiYiI6Imh0dHBzOi8vY2RuLTIwMzBlOTczNDUuZXhhbXBsZS5pbnZhbGlkLzkxNzJmZmYwOTcyYi5iaW4iLCJjIjpbInVwZGF0ZS0yMDMwZTk3MzQ1LmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS1iYjQ3YmJhZGE0OTAuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfMWNiNDg4Mzk1M2JmIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzIuOCJ9')
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
