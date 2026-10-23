#!/bin/bash
# usage: bash dnlang_oracle.sh FILE -> builds dnlang_oracle.cs (System.Reflection.Metadata, not dnfile) once into $TMPDIR
# and prints the raw metadata facts (AssemblyRef/AssemblyDef versions, F# resources, closure/anon type counts, CorFlags).
set -e; H=$(dirname "$(realpath "$0")"); W=${TMPDIR:-/tmp}/dnlang_oracle
if [ ! -f "$W/out/o.dll" ]; then mkdir -p "$W"; cp "$H/dnlang_oracle.cs" "$W/O.cs"
  printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>o</AssemblyName><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>\n' > "$W/o.csproj"
  (cd "$W" && dotnet build -c Release -o out >/dev/null); fi
dotnet "$W/out/o.dll" "$(realpath "$1")"
