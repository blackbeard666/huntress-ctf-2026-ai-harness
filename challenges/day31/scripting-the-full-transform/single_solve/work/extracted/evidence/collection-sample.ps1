# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_e1cc105e85 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMGQyMDZlYWE4MmYzIiwiYiI6Imh0dHBzOi8vOGQyZmJlYTQ0MC5leGFtcGxlLmludmFsaWQvODQyODA3ODRlNTA0LmRhdCIsImMiOlsidXBkYXRlLThkMmZiZWE0NDAuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLTBkMjA2ZWFhODJmMy56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9kZjIwMDVlZjljYTIiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvMS43In0=')
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
