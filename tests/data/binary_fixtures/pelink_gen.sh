#!/bin/bash
# usage: pelink_gen.sh   (writes pelink_*.bin next to this script)
# PE loader/plugin pair (lib.binary.pe_link_facts / pe_link_pair). zig cc -target {x86_64,x86}-windows-gnu (MinGW-w64
# CRT + lld). plugin: .def file with LIBRARY plugin.dll, ordinals @3 @4 @7 DATA, @9 NONAME, forwarder
# fwd_sleep = KERNEL32.Sleep @10; exported data symbol plugin_config = HCFG blob in section .hcfg. loader: TLS
# callback in .CRT$XLB, LoadLibraryA("plugin.dll") + GetProcAddress("plugin_init") (x64) / LoadLibraryW(L"plugin32.dll")
# + GetProcAddress("plugin_version") (x86). HCFG blob = {"HCFG", u8 ver=1, u8 key, u16 len, u32 crc32(json),
# json ^ key}; crc32 from the gzip trailer (coreutils), body xor by perl. Decoys: an MZ text impostor (printf) and a
# 300-byte truncated copy of the plugin (head -c). zig cannot emit delay imports (no -delayload): not covered.
set -e
D="$(cd "$(dirname "$0")" && pwd)"; R="$(cd "$D/../../.." && pwd)"; W=$(mktemp -d)
Z() { (cd "$W" && PYTHONPATH="$R/tools/pyziglang" python3 -m ziglang cc "$@"); }
hcfg() {   # $1 json, $2 key -> C initializer
  local P="$1" K=$(( $2 )) LEN CRC BODY; LEN=$(printf '%s' "$P" | wc -c)
  CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
  BODY=$(perl -e 'print join ",", map { ord($_) ^ $ARGV[1] } split //, $ARGV[0]' "$P" "$K")
  echo "struct hcfg { char m[4]; unsigned char ver, key; unsigned short len; unsigned int crc; unsigned char body[$LEN]; };"
  echo "__attribute__((section(\".hcfg\"), used)) const struct hcfg plugin_config = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};"
}
plugin() {   # $1 json $2 key $3 target $4 out $5 dll file name (lld writes it as the export Name)
  { hcfg "$1" "$2"; cat <<'C'
int plugin_init(int x) { return x * 7 + plugin_config.len; }
const char *plugin_version(void) { return "2.1"; }
int hidden_entry(int x) { return x ^ 0x5a; }
C
  } > "$W/p.c"
  printf 'LIBRARY "plugin.dll"\nEXPORTS\n  plugin_init @3\n  plugin_version @4\n  plugin_config @7 DATA\n  hidden_entry @9 NONAME\n  fwd_sleep = KERNEL32.Sleep @10\n' > "$W/p.def"
  Z -target "$3" -shared -O2 -s -o "$5" p.c p.def && cp "$W/$5" "$D/$4"
}
loader() {   # $1 LoadLibrary call $2 symbol $3 target $4 out
  cat > "$W/l.c" <<C
#include <windows.h>
#include <stdio.h>
static void NTAPI tls_cb(PVOID h, DWORD r, PVOID p) { (void)h; (void)r; (void)p; }
__attribute__((section(".CRT\$XLB"), used)) PIMAGE_TLS_CALLBACK tls_cb_ptr = tls_cb;
typedef int (*init_fn)(int);
int main(void) {
  HMODULE h = $1;
  if (!h) return 1;
  init_fn f = (init_fn)GetProcAddress(h, "$2");
  MessageBoxA(0, "loaded", "pl", 0);
  printf("%d\n", f ? f(3) : -1);
  return 0;
}
C
  Z -target "$3" -O2 -s -o l.exe l.c -luser32 && cp "$W/l.exe" "$D/$4"
}
plugin '{"plugin":"alpha","port":4444,"key":"k1"}' 0x5a x86_64-windows-gnu pelink_plugin_x64.bin plugin.dll
loader 'LoadLibraryA("plugin.dll")' plugin_init x86_64-windows-gnu pelink_loader_x64.bin
plugin '{"plugin":"beta","c2":"10.0.0.7"}' 0 x86-windows-gnu pelink_plugin_x86.bin plugin32.dll
loader 'LoadLibraryW(L"plugin32.dll")' plugin_version x86-windows-gnu pelink_loader_x86.bin
printf 'MZ renamed impostor: plugin.dll LoadLibraryA GetProcAddress HCFG, e_lfanew -> nowhere\n%0200d\n' 0 > "$D/pelink_decoy_text.bin"
head -c 300 "$D/pelink_plugin_x64.bin" > "$D/pelink_decoy_trunc.bin"
rm -rf "$W"
