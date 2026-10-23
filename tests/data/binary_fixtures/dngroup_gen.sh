#!/usr/bin/env bash
# dotnet_group_facts fixtures (managed multi-member groups), built by the dotnet 10 SDK + zip, never by lib.binary.
# usage (repo root): source bin/env.sh; bash tests/data/binary_fixtures/dngroup_gen.sh
set -euo pipefail
OUT=$(cd "$(dirname "$0")" && pwd); W=${TMPDIR:-/tmp}/dngroup_gen; rm -rf "$W"; mkdir -p "$W"; cd "$W"
# 1) F# console publish output: sample.dll + FSharp.Core.dll + sample.runtimeconfig.json + sample.deps.json
dotnet new console -lang "F#" -n sample -o sample --force >/dev/null
cat > sample/Program.fs <<'FS'
module Hunt.Sample
[<EntryPoint>]
let main argv =
    printfn "beacon %d" argv.Length
    0
FS
sed -i 's#<TargetFramework>net10.0</TargetFramework>#<TargetFramework>net10.0</TargetFramework><Deterministic>true</Deterministic><Version>2.4.6</Version><SatelliteResourceLanguages>en</SatelliteResourceLanguages>#' sample/sample.fsproj
(cd sample && dotnet publish -c Release -o pub >/dev/null)
(cd sample/pub && mkdir z && for f in sample.deps.json FSharp.Core.dll sample.dll sample.runtimeconfig.json; do cp "$f" "z/d30--$f"; done \
  && cd z && rm -f "$OUT/dngroup_fsharp_publish.bin" && zip -X "$OUT/dngroup_fsharp_publish.bin" d30--sample.deps.json d30--FSharp.Core.dll d30--sample.dll d30--sample.runtimeconfig.json >/dev/null)
# decoy: the same publish output WITHOUT the primary (only the FSharp.Core dependency + the json support members)
(cd sample/pub/z && rm -f "$OUT/dngroup_decoy_noprimary.bin" && zip -X "$OUT/dngroup_decoy_noprimary.bin" d30--sample.deps.json d30--FSharp.Core.dll d30--sample.runtimeconfig.json >/dev/null)
# 2) C# app with a ProjectReference library (Acme.Helper 1.2.3.0, strong-named) -> HuntApp.dll + Acme.Helper.dll
dotnet new classlib -lang "C#" -n Acme.Helper -o helper --force >/dev/null
cat > helper/Class1.cs <<'CS'
namespace Acme.Helper { public static class Util { public static int Twice(int x) => x * 2; } }
CS
dotnet new console -lang "C#" -n HuntApp -o app --force >/dev/null
cat > app/Program.cs <<'CS'
class Program { static int Main(string[] a) { System.Console.WriteLine(Acme.Helper.Util.Twice(a.Length)); return 0; } }
CS
python3 - <<'PY'
from Crypto.PublicKey import RSA   # snk = the CLR's PRIVATEKEYBLOB (RSA2) layout, written with pycryptodome
import struct
k = RSA.generate(1024, randfunc=__import__("random").Random(7).randbytes)
n = k.n.to_bytes(128, "little"); bl = lambda v, l: v.to_bytes(l, "little")
blob = struct.pack("<BBHI", 7, 2, 0, 0x2400) + b"RSA2" + struct.pack("<II", 1024, k.e) + n
blob += bl(k.p, 64) + bl(k.q, 64) + bl(k.d % (k.p - 1), 64) + bl(k.d % (k.q - 1), 64) + bl(pow(k.q, -1, k.p), 64) + bl(k.d, 128)
open("helper/key.snk", "wb").write(blob)
PY
sed -i 's#<TargetFramework>net10.0</TargetFramework>#<TargetFramework>net10.0</TargetFramework><Deterministic>true</Deterministic><AssemblyVersion>1.2.3.0</AssemblyVersion><SignAssembly>true</SignAssembly><AssemblyOriginatorKeyFile>key.snk</AssemblyOriginatorKeyFile>#' helper/Acme.Helper.csproj
sed -i 's#<TargetFramework>net10.0</TargetFramework>#<TargetFramework>net10.0</TargetFramework><Deterministic>true</Deterministic><AssemblyVersion>5.0.1.0</AssemblyVersion><RollForward>LatestMinor</RollForward>#' app/HuntApp.csproj
(cd app && dotnet add reference ../helper/Acme.Helper.csproj >/dev/null && dotnet publish -c Release -o pub >/dev/null)
(cd app/pub && mkdir z && for f in Acme.Helper.dll HuntApp.deps.json HuntApp.dll HuntApp.runtimeconfig.json; do cp "$f" "z/d31--$f"; done \
  && cd z && rm -f "$OUT/dngroup_csharp_projref.bin" && zip -X "$OUT/dngroup_csharp_projref.bin" d31--Acme.Helper.dll d31--HuntApp.deps.json d31--HuntApp.dll d31--HuntApp.runtimeconfig.json >/dev/null)
ls -la "$OUT"/dngroup_*.bin
