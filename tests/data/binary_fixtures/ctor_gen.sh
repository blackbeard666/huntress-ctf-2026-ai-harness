#!/bin/bash
# usage: ctor_gen.sh out.bin cc opt mode json [crc_xor]     (cc: gcc | aarch64-linux-gnu-gcc; mode: lcg | keyed)
# blob: printf header + crc32 from the gzip trailer (crc_xor != 0 -> corrupted header crc = decoy). The blob is stored
# ENCODED in `static const unsigned char enc[]` (perl encodes it) and decoded at LOAD time by an
# __attribute__((constructor)) function, never by main:
#   lcg   : enc[i] = b[i] ^ k_i, k_0 = 0xa7, k_{i+1} = (k_i*0x6b + 0x3d) & 0xff     -> decoded into global g_buf[N]
#   keyed : enc[i] = ((b[i] + 7*i) & 0xff) ^ key[i % strlen(key)], key "k3y-s3cr3t" -> malloc + memcpy + strlen,
#           decoded in place into heap buffer g_cfg (the constructor calls libc through the PLT/GOT)
# `prog dump` writes the decoded buffer to stdout (oracle).
set -e
P="$5"; W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
CRC=$(printf %08x $(( 0x$CRC ^ ${6:-0} )))
{ printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))";
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$W/blob.raw"
N=$(wc -c < "$W/blob.raw")
ENC=$(MODE="$4" perl -0777 -ne 'my @b = unpack("C*", $_); my ($k, @o) = (0xa7); my @key = unpack("C*", "k3y-s3cr3t");
  for my $i (0..$#b) { if ($ENV{MODE} eq "lcg") { push @o, $b[$i] ^ $k; $k = ($k * 0x6b + 0x3d) & 0xff }
                       else { push @o, (($b[$i] + 7 * $i) & 0xff) ^ $key[$i % @key] } }
  print join(",", @o)' < "$W/blob.raw")
{ echo '#include <stdio.h>'; echo '#include <stdlib.h>'; echo '#include <string.h>'
  echo "static const unsigned char enc[$N] = {$ENC};"
  if [ "$4" = lcg ]; then
    echo "unsigned char g_buf[$N];"
    echo '__attribute__((constructor)) static void cfg_init(void) {'
    echo '  unsigned char k = 0xa7; for (unsigned i = 0; i < sizeof enc; i++) { g_buf[i] = enc[i] ^ k; k = k * 0x6b + 0x3d; } }'
    echo 'static unsigned char *cfg(void) { return g_buf; }'
  else
    echo 'unsigned char *g_cfg; const char *volatile g_key = "k3y-s3cr3t";'
    echo '__attribute__((constructor(101))) static void cfg_init(void) {'
    echo '  g_cfg = malloc(sizeof enc); memcpy(g_cfg, enc, sizeof enc); size_t kl = strlen(g_key);'
    echo '  for (size_t i = 0; i < sizeof enc; i++) g_cfg[i] = (unsigned char)((g_cfg[i] ^ g_key[i % kl]) - 7 * i); }'
    echo 'static unsigned char *cfg(void) { return g_cfg; }'
  fi
  echo 'int main(int c, char **v) {'
  echo "  if (c > 1 && !strcmp(v[1], \"dump\")) { fwrite(cfg(), 1, $N, stdout); return 0; }"
  echo '  printf("usage: %s <cfg>\n", v[0]); return 0; }'
} > "$W/m.c"
"$2" -O"$3" -o "$1" "$W/m.c"
rm -rf "$W"
