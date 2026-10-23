# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_f65c1f59e4 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYmZiNWMwZjlkY2EzIiwiYiI6Imh0dHBzOi8vODFjZWNiYzA3Mi5leGFtcGxlLmludmFsaWQvMDY2MDliZDQxM2YwLmRhdCIsImMiOlsidXBkYXRlLTgxY2VjYmMwNzIuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLWJmYjVjMGY5ZGNhMy56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9iYzU5N2Q2OGJkNzMiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvOS42In0=')
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
