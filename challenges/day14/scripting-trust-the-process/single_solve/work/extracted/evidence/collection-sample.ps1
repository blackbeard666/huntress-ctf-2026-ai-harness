# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_c717947674 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiMzYzOTZjYWIzYTkxIiwiYiI6Imh0dHBzOi8vNzYxOTU2MjdhZi5leGFtcGxlLmludmFsaWQvMmY0MmFlNDUwOTk2LmRhdCIsImMiOlsidXBkYXRlLTc2MTk1NjI3YWYuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLTM2Mzk2Y2FiM2E5MS56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl8xOGQ3ZWFkODExZTYiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvOC41In0=')
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
