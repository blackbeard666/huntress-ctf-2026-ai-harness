# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_628a56260d {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiN2ZiODVmYmRmMDllIiwiYiI6Imh0dHBzOi8vY2RuLTdiODUyMmUzYzQuZXhhbXBsZS5pbnZhbGlkLzIyMDgwZjMyOWNmMS5iaW4iLCJjIjpbInVwZGF0ZS03Yjg1MjJlM2M0LmRhdCIsIkxvZ2luIERhdGEiLCJDb29raWVzIl0sImQiOiJzdGFnZS03ZmI4NWZiZGYwOWUuemlwIiwiZSI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfM2FkY2U0ZTNhOGQwIiwiZiI6Ik1vemlsbGEvNS4wIEh1bnRyZXNzTGFiLzMuMyJ9')
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
