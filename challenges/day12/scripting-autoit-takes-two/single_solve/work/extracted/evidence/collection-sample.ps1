# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_17751122e3 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNTI4YjQ0ODE4MWZkIiwiYiI6Imh0dHBzOi8vMjI1NmJmNzI5Zi5leGFtcGxlLmludmFsaWQvMzkyNmI2YzcwY2JjLmRhdCIsImMiOlsidXBkYXRlLTIyNTZiZjcyOWYuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLTUyOGI0NDgxODFmZC56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9mMWJjNmI5OWFmODEiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvNC42In0=')
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
