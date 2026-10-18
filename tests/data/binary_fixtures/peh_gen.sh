#!/bin/sh
# PE optional-header fixtures (generators independent of lib.binary). usage: sh peh_gen.sh  (from this dir)
set -e
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
cat > "$W/main.go" <<'GO'
package main

import "fmt"

var cfg = "HCFG-not-a-blob"

func main() { fmt.Println("peh fixture", cfg) }
GO
cd "$W" && go mod init peh >/dev/null 2>&1 && cd - >/dev/null
# 1) Go windows/amd64 console, default link: COFF symbol table + DWARF sections with /N long names
(cd "$W" && CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -trimpath -o peh_go_amd64.exe .)
cp "$W/peh_go_amd64.exe" peh_go_amd64_symtab.bin
# 2) Go windows/386 GUI subsystem, -s -w: no COFF symtab, no DWARF
(cd "$W" && CGO_ENABLED=0 GOOS=windows GOARCH=386 go build -trimpath -ldflags="-s -w -H windowsgui" -o peh_go_386.exe .)
cp "$W/peh_go_386.exe" peh_go_386_gui_stripped.bin
# 3) .NET (dotnet build, Day-3 style DLL): copy of dnmeta_lib_net8.bin
cp dnmeta_lib_net8.bin peh_dotnet_dll.bin
# decoys: PE signature broken (MZ stub kept) and a header cut inside the optional header
python3 -c "import sys; d=bytearray(open('peh_go_386_gui_stripped.bin','rb').read()); p=int.from_bytes(d[0x3c:0x40],'little'); d[p:p+4]=b'NE\0\0'; open('peh_decoy_badsig.bin','wb').write(bytes(d))"
python3 -c "d=open('peh_go_amd64_symtab.bin','rb').read(); p=int.from_bytes(d[0x3c:0x40],'little'); open('peh_decoy_trunc.bin','wb').write(d[:p+24+40])"
