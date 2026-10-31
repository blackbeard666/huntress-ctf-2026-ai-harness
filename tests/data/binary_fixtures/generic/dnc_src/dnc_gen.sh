#!/bin/bash
# gf-dotnet-counts members: dotnet SDK (Roslyn csc / vbc) Release builds of Program.cs / Program.vb -> ../dnc_cs.dll,
# ../dnc_vb.dll (deterministic builds). Needs `source bin/env.sh` (dotnet 10 SDK).
set -e; H=$(dirname "$(realpath "$0")"); W=${TMPDIR:-/tmp}/dnc_gen; rm -rf "$W"; mkdir -p "$W/cs" "$W/vb"
cp "$H/Program.cs" "$W/cs/"; cp "$H/Program.vb" "$W/vb/"
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>dnc_cs</AssemblyName><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable><Deterministic>true</Deterministic><DebugType>none</DebugType><UseAppHost>false</UseAppHost></PropertyGroup></Project>\n' > "$W/cs/c.csproj"
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>dnc_vb</AssemblyName><RootNamespace></RootNamespace><StartupObject>Bravo.Entry</StartupObject><Deterministic>true</Deterministic><DebugType>none</DebugType><UseAppHost>false</UseAppHost></PropertyGroup></Project>\n' > "$W/vb/v.vbproj"
(cd "$W/cs" && dotnet build -c Release -o out >/dev/null) && cp "$W/cs/out/dnc_cs.dll" "$H/../dnc_cs.dll"
(cd "$W/vb" && dotnet build -c Release -o out >/dev/null) && cp "$W/vb/out/dnc_vb.dll" "$H/../dnc_vb.dll"
