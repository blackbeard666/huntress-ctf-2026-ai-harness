# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_45c653d625 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYjk3ODA0ZjhkMGRlIiwiYiI6Imh0dHBzOi8vYTY4NjM0NTQ3My5leGFtcGxlLmludmFsaWQvY2VhMDY0NDVmMGY4LmRhdCIsImMiOlsidXBkYXRlLWE2ODYzNDU0NzMuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLWI5NzgwNGY4ZDBkZS56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl8xMTc2ZmI0MDdmZGIiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvNi40In0=')
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
