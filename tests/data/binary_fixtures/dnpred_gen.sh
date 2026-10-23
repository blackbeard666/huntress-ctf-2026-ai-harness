#!/bin/bash
# .NET anti-analysis predicate fixtures (D23 "Trust Issues" theme). usage: bash dnpred_gen.sh OUTDIR   (dotnet 10 SDK, offline)
#  dnpred_vb_net10.bin : VB.NET Exe: If(GetEnvironmentVariable("HUNTRESS_HOST_MODEL"),"workstation"), Stopwatch timing
#                        (ElapsedMilliseconds > 4000), Debugger.IsLogging, ProcessorCount < 3, MachineName = literal,
#                        Operators.CompareString model chains -> success/decoy/failure + anonymous-type JSON trace record
#  dnpred_cs_net10.bin : C# Exe: Debugger.IsAttached, DateTime.Now delta TotalMilliseconds > 2500, TickCount64,
#                        ProcessorCount <= 1, UserName == literal, string switch on the model (Roslyn length dispatch)
#  dnpred_decoy_lib.bin: C# library without predicates -> predicate_count 0 ; dnpred_decoy_trunc.bin: first 2048 bytes -> None
# Then dnpred_oracle.py writes each *.json from ilspycmd -il text + running the fixture with HUNTRESS_HOST_MODEL=<m>.
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
P='<TargetFramework>net10.0</TargetFramework><Deterministic>true</Deterministic><DebugType>none</DebugType><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable>'
mkdir -p Vb Cs Lib
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>%s<OutputType>Exe</OutputType><AssemblyName>PredVb</AssemblyName><RootNamespace>Hunt.Pred</RootNamespace><OptionStrict>On</OptionStrict></PropertyGroup></Project>\n' "$P" > Vb/Vb.vbproj
cat > Vb/P.vb <<'VB'
Imports System
Imports System.Diagnostics
Module Program
    Function Main() As Integer
        Dim model As String = If(Environment.GetEnvironmentVariable("HUNTRESS_HOST_MODEL"), "workstation")
        Dim sw As Stopwatch = Stopwatch.StartNew()
        Dim acc As Integer = 0
        For i As Integer = 0 To 63
            acc = acc Xor i
        Next
        sw.Stop()
        Dim detected As Boolean = Debugger.IsLogging() OrElse Environment.ProcessorCount < 3 OrElse sw.ElapsedMilliseconds > 4000 OrElse Environment.MachineName = "SANDBOX-01"
        If model = "workstation" Then detected = False
        If model = "analysis" OrElse model = "sandbox" Then detected = True
        Dim branch As String
        If model = "workstation" Then
            branch = "success"
        ElseIf model = "analysis" Then
            branch = "decoy"
        Else
            branch = "failure"
        End If
        Dim n As Integer = If(model = "workstation", 12, If(model = "analysis", 7, 3))
        Dim rec = New With {.schema = "huntress.binary.dynamic_trace.v1", .branch = branch, .event_count = n, .campaign = "FX-VB-001", .family = "vbnet_predicate_fixture", .effects = "inert_predicate_only", .network = "none", .analysis_detected = detected}
        Console.WriteLine(System.Text.Json.JsonSerializer.Serialize(rec))
        Return 0
    End Function
End Module
VB
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>%s<OutputType>Exe</OutputType><AssemblyName>PredCs</AssemblyName></PropertyGroup></Project>\n' "$P" > Cs/Cs.csproj
cat > Cs/P.cs <<'CS'
using System; using System.Diagnostics;
namespace Hunt.Pred {
  internal static class Program {
    static int Main() {
      string model = Environment.GetEnvironmentVariable("HUNTRESS_HOST_MODEL") ?? "workstation";
      DateTime t0 = DateTime.Now;
      long k0 = Environment.TickCount64;
      int acc = 0; for (int i = 0; i < 100; i++) acc ^= i * 7;
      bool detected = Debugger.IsAttached;
      if ((DateTime.Now - t0).TotalMilliseconds > 2500) detected = true;
      if (Environment.TickCount64 - k0 > 3000) detected = true;
      if (Environment.ProcessorCount <= 1) detected = true;
      if (Environment.UserName == "malware") detected = true;
      if (model != "workstation") detected = true;
      string branch; int n;
      switch (model) {
        case "workstation": branch = "success"; n = 21; break;
        case "analysis": branch = "decoy"; n = 9; break;
        case "sandbox": branch = "failure"; n = 4; break;
        default: branch = "failure"; n = 1; break;
      }
      var rec = new { schema = "huntress.binary.dynamic_trace.v1", branch = branch, event_count = n, campaign = "FX-CS-002",
                      family = "csharp_predicate_fixture", effects = "inert_predicate_only", network = "none", analysis_detected = detected };
      Console.WriteLine(System.Text.Json.JsonSerializer.Serialize(rec));
      return acc == -1 ? 1 : 0;
    }
  }
}
CS
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>%s<OutputType>Library</OutputType><AssemblyName>PredLib</AssemblyName></PropertyGroup></Project>\n' "$P" > Lib/Lib.csproj
cat > Lib/L.cs <<'CS'
namespace Hunt.Plain { public static class Calc { public static int Add(int a, int b) => a + b; public static string Hi(string n) => "hi " + n; } }
CS
for p in Vb Cs Lib; do (cd $p && dotnet build -c Release -o ../out/$p >/dev/null); done
cp out/Vb/PredVb.dll "$OUT/dnpred_vb_net10.bin"; cp out/Cs/PredCs.dll "$OUT/dnpred_cs_net10.bin"
cp out/Lib/PredLib.dll "$OUT/dnpred_decoy_lib.bin"; head -c 2048 out/Cs/PredCs.dll > "$OUT/dnpred_decoy_trunc.bin"
for p in Vb Cs; do for m in workstation analysis sandbox; do
  HUNTRESS_HOST_MODEL=$m dotnet out/$p/Pred$p.dll > "$OUT/.dnpred_run_${p}_$m.txt"; done; done
echo "$W"
