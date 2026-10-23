#!/bin/bash
# usage: bash mmnat_oracle.sh FILE -> System.Reflection.PortableExecutable facts (mmnat_oracle.cs, built once into $TMPDIR)
# Shellcode oracles (not this script): the x64 build really executes both stubs via mmap (mmnat_gen.sh prints
# 1077952583 / 4879); disasm: printf <bytes> > s.bin; objdump -D -b binary -m i386:x86-64 -M intel s.bin (or -m i386);
# Roslyn's <PrivateImplementationDetails> field name = uppercase sha256 of the array bytes (sha256sum).
set -e; H=$(dirname "$(realpath "$0")"); W=${TMPDIR:-/tmp}/mmnat_oracle
if [ ! -f "$W/out/o.dll" ]; then mkdir -p "$W"; cp "$H/mmnat_oracle.cs" "$W/O.cs"
  printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>o</AssemblyName><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>\n' > "$W/o.csproj"
  (cd "$W" && dotnet build -c Release -o out >/dev/null); fi
dotnet "$W/out/o.dll" "$(realpath "$1")"
