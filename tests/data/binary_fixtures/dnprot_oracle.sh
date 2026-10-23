#!/bin/bash
# usage: bash dnprot_oracle.sh FILE -> builds dnprot_oracle.cs (System.Reflection.Metadata + runtime module ctor) once into $TMPDIR and runs it
set -e; H=$(dirname "$(realpath "$0")"); W=${TMPDIR:-/tmp}/dnprot_oracle
if [ ! -f "$W/out/o.dll" ] || [ "$H/dnprot_oracle.cs" -nt "$W/out/o.dll" ]; then mkdir -p "$W"; cp "$H/dnprot_oracle.cs" "$W/O.cs"
  printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>o</AssemblyName><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable><RollForward>Major</RollForward></PropertyGroup><ItemGroup><PackageReference Include="System.IO.Hashing" Version="8.0.0" /></ItemGroup></Project>\n' > "$W/o.csproj"
  (cd "$W" && dotnet build -c Release -o out 2>&1 | grep -E " error " ; true); fi
dotnet "$W/out/o.dll" "$(realpath "$1")"
