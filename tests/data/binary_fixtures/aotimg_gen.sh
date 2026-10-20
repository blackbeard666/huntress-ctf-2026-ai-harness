#!/usr/bin/env bash
# Offline generator for aotimg_* fixtures (GraalVM native-image / Julia sysimage look-alikes; native-image and julia are
# not installed, so the images are synthetic: gcc puts the runtime's real section/symbol names around an HCFG blob).
# Blob = 'HCFG' ver key len crc32(plain) + plain^key, written by python3 stdlib (struct/zlib/base64), not lib.binary.
# usage: bash aotimg_gen.sh   (from this directory)
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd); w=$(mktemp -d); trap 'rm -rf "$w"' EXIT; cd "$w"
blob() {  # $1 = json config, $2 = key -> C initializer of the blob bytes ; $3 = "b64" for base64 text
python3 -I - "$1" "$2" "${3:-raw}" <<'PY'
import base64, struct, sys, zlib
plain, key = sys.argv[1].encode(), int(sys.argv[2])
crc = zlib.crc32(plain) ^ (0xFFFFFFFF if sys.argv[3] == "badcrc" else 0)   # badcrc: a decoy that must NOT validate
b = b"HCFG" + struct.pack("<BBHI", 1, key, len(plain), crc) + bytes(c ^ key for c in plain)
if sys.argv[3] == "b64":
    b = base64.b64encode(b)
print(",".join(str(x) for x in b))
PY
}
# 1. GraalVM ELF: .svm_heap holds a Java byte[] (hub word + int length) whose payload is the raw blob
B1=$(blob '{"c2":"graal-heap.example","port":8443,"id":"svm-01"}' 90)
cat > g1.c <<C
__attribute__((section(".svm_heap"), used)) const unsigned char heap[] = {
  0x11,0x22,0x33,0x44,0,0,0,0, 0x50,0,0,0, $B1, 0 };
__attribute__((section(".svm_heap"), used)) const char res_name[] = "META-INF/native-image/resources/app.hcfg";
__attribute__((used)) const char __svm_version_info[] = "GraalVM 21.0.2+13.1 Java 21 CE";
__attribute__((used)) int __svm_vm_target = 1;
int IsolateEnterStub_JavaMainWrapper_run_5087f5482cc9a6abc971913ece43acb471d2631b_a61fe6c26e84dd4037e4629852b5488bfcc16e7e(int a){return a;}
int main(void){return 0;}
C
gcc -O0 -no-pie -o g1 g1.c && cp g1 "$here/aotimg_graal_heap_raw.bin"
# 2. GraalVM ELF: the blob base64'd inside a Latin-1 java.lang.String byte[] in .svm_heap; no version string
B2=$(blob '{"beacon":"https://svm.example/b","sleep":30}' 7 b64)
cat > g2.c <<C
__attribute__((section(".svm_heap"), used)) const unsigned char heap[] = { 0x99,0x88,0,0,0,0,0,0, 0x60,0,0,0, $B2, 0 };
__attribute__((used)) int __svm_vm_target = 2;
int main(void){return 0;}
C
gcc -O0 -o g2 g2.c && cp g2 "$here/aotimg_graal_heap_b64.bin"
# 3. Julia sysimage (sys.so): exported jl_system_image_data (in .rodata) carries the raw blob
B3=$(blob '{"c2":"jl.example:9000","mode":"sysimg"}' 33)
cat > j1.c <<C
const unsigned char jl_system_image_data[] = { 0x4a,0x4c,0,0, $B3, 1,2,3,4 };
const unsigned long jl_system_image_size = sizeof(jl_system_image_data);
const void *jl_image_pointers[] = { (const void*)jl_system_image_data, 0 };
const char jl_ver[] = "Julia Version 1.10.4";
C
gcc -O0 -shared -fPIC -o sys.so j1.c && cp sys.so "$here/aotimg_julia_sysimg.bin"
# 4. Julia PackageCompiler app launcher: DT_NEEDED libjulia.so.1, calls jl_init_with_image; no blob
cat > lj.c <<C
void jl_init_with_image(const char *a, const char *b){(void)a;(void)b;} void jl_atexit_hook(int c){(void)c;}
C
gcc -shared -fPIC -Wl,-soname,libjulia.so.1 -o libjulia.so.1 lj.c
cat > app.c <<C
void jl_init_with_image(const char *a, const char *b); void jl_atexit_hook(int c);
int main(void){ jl_init_with_image("bin", "../lib/julia/sys.so"); jl_atexit_hook(0); return 0; }
C
gcc -O0 -o app app.c ./libjulia.so.1 && cp app "$here/aotimg_julia_app.bin"
# 5. DECOY: plain C program quoting every cue as a string literal (no such section/symbol) + a bad-crc blob in .rodata
B5=$(blob '{"decoy":true}' 1 badcrc)
cat > d1.c <<C
const unsigned char cfg[] = { $B5 };
const char *cues[] = {"com.oracle.svm.core.VM", ".svm_heap", "__svm_vm_target", "jl_system_image_data", "libjulia.so.1",
                      "jl_init_with_image", "GraalVM 21.0.2"};
int main(void){ return cues[0][0] + cfg[0]; }
C
gcc -O0 -o d1 d1.c && cp d1 "$here/aotimg_decoy_strings.bin"
# 6. DECOY: fixture 1 truncated to its first 4096 bytes (section table gone)
head -c 4096 g1 > "$here/aotimg_decoy_trunc.bin"
