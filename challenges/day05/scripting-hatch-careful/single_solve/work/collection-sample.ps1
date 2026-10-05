# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_a147fbf98c {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiOGE5ZjVjNTRmYzc2IiwiYiI6Imh0dHBzOi8vY2RuLWJkZDEzYTcxYmEuZXhhbXBsZS5pbnZhbGlkL2VmOTg1N2Y0MzNkYS5iaW4iLCJjIjpbInVwZGF0ZS1iZGQxM2E3MWJhLmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS04YTlmNWM1NGZjNzYuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfOTZjNDFmYjg3NWI4IiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzkuOSJ9')
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
