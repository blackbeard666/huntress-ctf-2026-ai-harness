#!/usr/bin/env bash
# dotnet_language_of fixtures, built by the dotnet 10 SDK (vbc / fsc / csc), never by lib.binary.
# usage (repo root): source bin/env.sh; bash tests/data/binary_fixtures/dnlang_gen.sh
set -euo pipefail
OUT=$(cd "$(dirname "$0")" && pwd); W=${TMPDIR:-/tmp}/dnlang_gen; rm -rf "$W"; mkdir -p "$W"; cd "$W"
# HCFG blob (stdlib python writer) embedded as an F# byte[] literal -> FieldRVA data in .text
python3 - <<'EOF'
import json, struct, zlib
cfg = json.dumps({"c2": "198.51.100.7", "sleep": 30}).encode(); key = 0x21
blob = b"HCFG" + struct.pack("<BBHI", 1, key, len(cfg), zlib.crc32(cfg)) + bytes(b ^ key for b in cfg)
open("blob.bin", "wb").write(blob)
arr = "; ".join("0x%02xuy" % b for b in blob)
open("Program.fs", "w").write(f'''module Hunt.Program
let cfgBlob : byte[] = [| {arr} |]
let adder n = fun x -> x + n
[<EntryPoint>]
let main argv =
    let k = argv.Length
    let fs = [ for i in 1..3 -> (fun y -> y * i + k) ]
    let r = {{| Name = "hunt"; Size = cfgBlob.Length |}}
    let total = fs |> List.sumBy (fun f -> f 2)
    printfn "%s %d %d %d" r.Name r.Size total (adder k 1)
    0
''')
EOF
dotnet new console -lang "F#" -o fs --force >/dev/null; cp Program.fs fs/Program.fs
dotnet new console -lang VB -o vb --force >/dev/null
cat > vb/Program.vb <<'EOF'
Imports System
Imports System.Linq

Module Program
    Sub Main(args As String())
        Dim n As Integer = args.Length
        Dim f As Func(Of Integer, Integer) = Function(x) x + n
        Dim anon = New With {.Name = "hunt", .Size = 7}
        Dim q = From i In Enumerable.Range(1, 5) Where i > n Select i * 2
        For Each v In q
            Console.WriteLine(f(v))
        Next
        Console.WriteLine(anon.Name & Microsoft.VisualBasic.Strings.Left("vbnet", 2))
    End Sub
End Module
EOF
dotnet new console -lang "C#" -o csimp --force >/dev/null
cat > csimp/Program.cs <<'EOF'
using System;
class Program {
    static void Main(string[] args) {
        int n = args.Length;
        Func<int,int> f = x => x + n;
        var a = new { Name = "FSharp.Core", Ref = "Microsoft.VisualBasic", T = "_Closure$__0-0", S = "<StartupCode$fs>", R = "FSharpSignatureCompressedData.fs" };
        Console.WriteLine(a.Name + a.Ref + a.T + a.S + a.R + f(1) + "<CrtImplementationDetails>");
    }
}
EOF
for p in fs/fs.fsproj vb/vb.vbproj csimp/csimp.csproj; do
  sed -i 's#<TargetFramework>net10.0</TargetFramework>#<TargetFramework>net10.0</TargetFramework><Deterministic>true</Deterministic>#' "$p"
  (cd "$(dirname "$p")" && dotnet build -c Release -o out >/dev/null); done
cp fs/out/fs.dll "$OUT/dnlang_fsharp_hcfg_net10.bin"; cp fs/out/FSharp.Core.dll "$OUT/dnlang_fsharp_core_dll.bin"
cp vb/out/vb.dll "$OUT/dnlang_vbnet_net10.bin"; cp csimp/out/csimp.dll "$OUT/dnlang_decoy_cs_cuestrings.bin"
printf 'MZ\x90\x00 not a PE: BSJB FSharp.Core Microsoft.VisualBasic.Core <StartupCode$fs> _Closure$__ FSharpSignatureCompressedData.fs\n' \
  > "$OUT/dnlang_decoy_text_impostor.bin"
echo "HCFG blob: $W/blob.bin"   # oracle offset: bytes.find(blob) in the F# dll
