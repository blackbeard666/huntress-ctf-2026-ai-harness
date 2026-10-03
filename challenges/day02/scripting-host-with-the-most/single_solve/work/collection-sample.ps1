# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_b29731dc90 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYTU5M2U1NjFmYjAyIiwiYiI6Imh0dHBzOi8vNGU0ZDE5NWM0Ny5leGFtcGxlLmludmFsaWQvYmI0NTc1OTliMGM0LmRhdCIsImMiOlsidXBkYXRlLTRlNGQxOTVjNDcuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLWE1OTNlNTYxZmIwMi56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl80NDkzMmJjZGIzZTQiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvOC43In0=')
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
