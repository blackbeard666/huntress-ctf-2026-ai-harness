# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_45126c2dde {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYzI2YjRmZTc1NTg1IiwiYiI6Imh0dHBzOi8vMTQ5MDU5OGVjMS5leGFtcGxlLmludmFsaWQvNzUwYjAzMjVmMDI5LmRhdCIsImMiOlsidXBkYXRlLTE0OTA1OThlYzEuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLWMyNmI0ZmU3NTU4NS56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl8wZTJkMWUwYjI1MWUiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvMC40In0=')
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
