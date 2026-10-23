#!/bin/bash
# usage: bash pinv_oracle.sh FILE  -> builds pinv_oracle.cs (System.Reflection.Metadata) once into $TMPDIR and runs it
set -e; H=$(dirname "$(realpath "$0")"); W=${TMPDIR:-/tmp}/pinv_oracle
if [ ! -f "$W/out/o.dll" ]; then mkdir -p "$W"; cp "$H/pinv_oracle.cs" "$W/O.cs"
  printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>o</AssemblyName><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>\n' > "$W/o.csproj"
  (cd "$W" && dotnet build -c Release -o out >/dev/null); fi
dotnet "$W/out/o.dll" "$(realpath "$1")"
