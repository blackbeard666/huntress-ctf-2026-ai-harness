#!/bin/bash
# usage: bash cominterop_oracle.sh FILE  -> builds cominterop_oracle.cs (System.Reflection.Metadata) once into $TMPDIR and runs it
set -e; H=$(dirname "$(realpath "$0")"); W=${TMPDIR:-/tmp}/cominterop_oracle
if [ ! -f "$W/out/o.dll" ] || [ "$H/cominterop_oracle.cs" -nt "$W/out/o.dll" ]; then mkdir -p "$W"; cp "$H/cominterop_oracle.cs" "$W/O.cs"
  printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>o</AssemblyName><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable></PropertyGroup></Project>\n' > "$W/o.csproj"
  (cd "$W" && dotnet build -c Release -o out 2>&1 | grep -E " error " ; true); fi
dotnet "$W/out/o.dll" "$(realpath "$1")"
