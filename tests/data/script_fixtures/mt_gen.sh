#!/usr/bin/env bash
# material_text static-matcher fixtures (prebuild mastery-scale-bench-30k): coreutils base64/xxd + perl xor writers.
set -euo pipefail
cd "$(dirname "$0")"
P1='v=3|language=vbscript|role=downloader|verdict=malicious|attack=T1105|adapter=http_get|stage_count=2|steps=acquire_remote,write_file|campaign_id=VBS-7e41c0aa|url=https://vbs-7e41c0aa.example.invalid/stage.bin'
B=$(printf %s "$P1" | perl -pe 's/(.)/chr(ord($1)^0x5a)/gse' | base64 -w0)
{ printf "' split-part material: Material_7e41_a + Material_7e41_b, neighbours Material_7e41x / Material_7e4 are not it\r\n"
  printf 'Const Codec_7e41 = "base64|single_byte_xor|5a"\r\n'
  printf 'Material_7e41x = "%s"\r\n' "QUJDREVGR0g="
  printf 'Material_7e4 = "%s"\r\n' "SUpLTE1OT1A="
  printf 'Material_7e41_a = "%s"\r\n' "${B:0:60}"
  printf 'Material_7e41_b = "%s"\r\n' "${B:60}"
  printf 'plan = Decode(Material_7e41_a & Material_7e41_b, Codec_7e41)\r\n'; } > mt_split_parts.vbs
P2='v=3|language=powershell|role=persistence|verdict=malicious|attack=T1547.001|adapter=run_key|stage_count=1|steps=write_registry|campaign_id=PS-c0de9b12|file_path=C:\Users\Public\c0de9b12.ps1'
H=$(printf %s "$P2" | xxd -p | tr -d '\n')
{ printf '$Codec_c0de = '"'"'hex|identity|'"'"'\n'
  printf '$Material_c0de = '"'"'%s'"'"'\n' "${H:0:100}"
  printf 'Write-Host $Material_c0de.Length\n'
  printf '$Material_c0de += '"'"'%s'"'"'\n' "${H:100}"
  printf '$plan = -join ($Material_c0de -split "(..)" | ? { $_ } | %% { [char][Convert]::ToByte($_, 16) })\n'; } > mt_ps_append.ps1
# decoy: the declared ident has no assignment; only neighbours (Material_51abc / Material_51ab2) hold a non-plan blob
N=$(printf %s 'not a plan: inventory refresh complete' | perl -pe 's/(.)/chr(ord($1)^0x33)/gse' | base64 -w0)
{ printf 'Const Codec_51ab = "base64|single_byte_xor|33"\r\n'
  printf 'Material_51abc = "%s"\r\n' "$N"
  printf 'Material_51ab2 = "%s"\r\n' "$N"
  printf 'WScript.Echo Material_51ab\r\n'; } > mt_decoy_neighbours.vbs
