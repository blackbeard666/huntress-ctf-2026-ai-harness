# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_efdb630cd7 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMTk4OWMzODQ0ZTk2IiwiYiI6Imh0dHBzOi8vY2RuLTI3Y2E1NjdhYTEuZXhhbXBsZS5pbnZhbGlkLzE2YTE1M2EzYjliZi5iaW4iLCJjIjpbInVwZGF0ZS0yN2NhNTY3YWExLmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS0xOTg5YzM4NDRlOTYuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNGIwOTQzYmMyNTAyIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzkuMiJ9')
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
