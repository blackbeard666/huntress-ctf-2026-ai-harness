#!/usr/bin/env bash
# env-keyed HCFG fixtures (env-keyed-hcfg-derivation): the config is decrypted only on the 'true' branch with a key
# derived from the compared env literal. Writers: python stdlib (hashlib/zlib) for the encrypted blob, gcc (C ELF), the
# dotnet 10 SDK csc (C# dll) -- never lib.binary. Oracle: envkey_oracle.sh (openssl dgst key + python stdlib crc/json),
# and the ELFs themselves run with HUNTRESS_HOST_MODEL=<literal> print the decrypted JSON.
# usage (repo root): source bin/env.sh; bash tests/data/binary_fixtures/envkey_gen.sh
set -euo pipefail
OUT=$(cd "$(dirname "$0")" && pwd); W=${TMPDIR:-/tmp}/envkey_gen; rm -rf "$W"; mkdir -p "$W"; cd "$W"
# mkblob <kdf> <literal> <xorbyte> <json> <mode: whole|body> -> C initializer list on stdout, ciphertext in ct.bin
mkblob() { python3 - "$@" <<'EOF'
import hashlib, struct, sys, zlib
kdf, lit, k, js, mode = sys.argv[1], sys.argv[2].encode(), int(sys.argv[3], 0), sys.argv[4].encode(), sys.argv[5]
key = {"sha256": hashlib.sha256(lit).digest(), "crc32le": struct.pack("<I", zlib.crc32(lit)), "xor": lit}[kdf]
blob = b"HCFG" + struct.pack("<BBHI", 1, k, len(js), zlib.crc32(js)) + bytes(c ^ k for c in js)
ct = bytes(c ^ key[i % len(key)] for i, c in enumerate(blob)) if mode == "whole" else \
    blob[:12] + bytes(c ^ key[i % len(key)] for i, c in enumerate(blob[12:]))
open("ct.bin", "wb").write(ct)
print(",".join("0x%02x" % c for c in ct))
EOF
}
SHA256_C='
typedef unsigned int u32;
static const u32 K[64]={0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,
0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,
0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,
0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,
0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,
0xc67178f2};
#define R(x,n) (((x)>>(n))|((x)<<(32-(n))))
static void sha256(const unsigned char*m,size_t n,unsigned char o[32]){u32 h[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,
0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};unsigned char b[128];size_t L=((n+9+63)/64)*64,i,j;
for(size_t off=0;off<L;off+=64){for(i=0;i<64;i++){size_t p=off+i;b[i]=p<n?m[p]:p==n?0x80:0;}
if(off+64==L)for(i=0;i<8;i++)b[56+i]=(unsigned char)(((unsigned long long)n*8)>>(56-8*i));
u32 w[64],a[8];for(i=0;i<16;i++)w[i]=(u32)b[4*i]<<24|(u32)b[4*i+1]<<16|(u32)b[4*i+2]<<8|b[4*i+3];
for(;i<64;i++)w[i]=(R(w[i-2],17)^R(w[i-2],19)^(w[i-2]>>10))+w[i-7]+(R(w[i-15],7)^R(w[i-15],18)^(w[i-15]>>3))+w[i-16];
for(j=0;j<8;j++)a[j]=h[j];for(i=0;i<64;i++){u32 t1=a[7]+(R(a[4],6)^R(a[4],11)^R(a[4],25))+((a[4]&a[5])^(~a[4]&a[6]))+K[i]+w[i];
u32 t2=(R(a[0],2)^R(a[0],13)^R(a[0],22))+((a[0]&a[1])^(a[0]&a[2])^(a[1]&a[2]));for(j=7;j>0;j--)a[j]=a[j-1];a[4]+=t1;a[0]=t1+t2;}
for(j=0;j<8;j++)h[j]+=a[j];}for(i=0;i<32;i++)o[i]=(unsigned char)(h[i/4]>>(24-8*(i%4)));}
'
# 1: C ELF, whole blob ^ sha256("workstation") (repeating 32 B), compared against getenv("HUNTRESS_HOST_MODEL")
ARR=$(mkblob sha256 workstation 0x3c '{"c2":"10.13.37.21:8443","campaign":"truthforce","sleep":40,"flag":"flag{f0rc3_th3_truth_0ut}"}' whole)
cat > e1.c <<EOF
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
$SHA256_C
static unsigned char cfg_blob[] = {$ARR};
int main(void){const char*m=getenv("HUNTRESS_HOST_MODEL");if(!m){puts("no model");return 1;}
if(!strcmp(m,"sandbox")||!strcmp(m,"analysis")){puts("decoy branch");return 0;}
if(strcmp(m,"workstation")){puts("unknown host");return 2;}
unsigned char k[32];sha256((const unsigned char*)m,strlen(m),k);
for(size_t i=0;i<sizeof cfg_blob;i++)cfg_blob[i]^=k[i%32];
unsigned char x=cfg_blob[5];unsigned n=cfg_blob[6]|cfg_blob[7]<<8;for(unsigned i=0;i<n;i++)putchar(cfg_blob[12+i]^x);
putchar(10);return 0;}
EOF
gcc -O1 -s -o "$OUT/envkey_elf_sha256.bin" e1.c
# 2: C ELF, plain header, BODY ^ sha256("analysis") (32-byte key: beyond the 1-16 byte multixor-body pass), env HCTF_SITE
ARR=$(mkblob sha256 analysis 0x5a '{"c2":"198.51.100.61:443","campaign":"analysis-only","sleep":15,"flag":"flag{sh4_k3y3d_b0dy}"}' body)
cat > e2.c <<EOF
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
$SHA256_C
static unsigned char cfg_blob[] = {$ARR};
int main(void){const char*m=getenv("HCTF_SITE");if(!m||strcmp(m,"analysis")){puts(m&&!strcmp(m,"workstation")?"decoy":"nope");return 1;}
unsigned char k[32];sha256((const unsigned char*)m,strlen(m),k);
unsigned char x=cfg_blob[5];unsigned n=cfg_blob[6]|cfg_blob[7]<<8;for(unsigned i=0;i<n;i++)putchar(cfg_blob[12+i]^k[i%32]^x);
putchar(10);return 0;}
EOF
gcc -O2 -o "$OUT/envkey_elf_sha256_body.bin" e2.c
# 3: C# dll (csc via dotnet build), whole blob ^ SHA256.HashData(UTF8("workstation")); literal in #US as UTF-16
ARR=$(mkblob sha256 workstation 0x21 '{"c2":"203.0.113.88:9443","campaign":"dotnet-truth","sleep":25,"flag":"flag{cs_sha256_w0rkst4t10n}"}' whole)
mkdir cs; cd cs; dotnet new classlib -o . --force >/dev/null; rm -f Class1.cs
cat > Gate.cs <<EOF
using System; using System.Security.Cryptography; using System.Text;
namespace Hunt {
public static class Gate {
    static readonly byte[] Blob = new byte[] { $ARR };
    public static string Run() {
        var m = Environment.GetEnvironmentVariable("HUNTRESS_HOST_MODEL") ?? "";
        if (m == "sandbox" || m == "analysis") return "decoy";
        if (m != "workstation") return "unknown";
        var k = SHA256.HashData(Encoding.UTF8.GetBytes(m)); var b = (byte[])Blob.Clone();
        for (int i = 0; i < b.Length; i++) b[i] ^= k[i % 32];
        int n = b[6] | b[7] << 8; var p = new byte[n]; for (int i = 0; i < n; i++) p[i] = (byte)(b[12 + i] ^ b[5]);
        return Encoding.UTF8.GetString(p);
    }
}}
EOF
dotnet build -c Release -o out >/dev/null; cp out/cs.dll "$OUT/envkey_cs_sha256.bin"; cd ..
# decoy: C ELF with the same layout, blob ^ sha256 of a host name that is NOT in the binary ('workstation-77'); the
# compared literals are workstation/sandbox -> no literal-derived key decrypts it -> "none"
ARR=$(mkblob sha256 workstation-77 0x3c '{"c2":"10.13.37.99:8443","campaign":"hidden","sleep":40,"flag":"flag{n0t_d3r1v4bl3}"}' whole)
cat > d.c <<EOF
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned char cfg_blob[] = {$ARR};
int main(void){const char*m=getenv("HUNTRESS_HOST_MODEL");if(!m||strcmp(m,"workstation")){puts(m&&!strcmp(m,"sandbox")?"sb":"no");return 1;}
printf("%zu\n",sizeof cfg_blob);return 0;}
EOF
gcc -O1 -o "$OUT/envkey_decoy_elf.bin" d.c
echo ok
