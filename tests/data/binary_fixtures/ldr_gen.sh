#!/bin/bash
# usage: ldr_gen.sh out.bin cc mode json [crc_xor]      (cc: gcc | aarch64-linux-gnu-gcc; mode: tls | ifunc)
# Loader-time code paths ("the loader's handshake"): every program has a __thread config (.tdata) + .tbss buffer, an
# __attribute__((ifunc)) symbol, a .preinit_array entry, prioritized constructors (101 / 202) and a destructor.
# blob: printf header + crc32 from the gzip trailer (crc_xor != 0 -> corrupted header crc = decoy), stored ENCODED
# (perl) and decoded at LOAD time, never by main:
#   tls   : `__thread unsigned char tcfg[] = {enc}` in .tdata, enc[i] = b[i] ^ ((0x5a + 3*i) & 0xff); constructor(101)
#           decodes it into the .tbss TLS buffer tbuf (thread pointer relative accesses)
#   ifunc : static const enc[], enc[i] = b[i] ^ k_i, k_0 = 0x3c, k_{i+1} = (k_i*0x2d + 0x11) & 0xff; the IFUNC
#           RESOLVER of `pick` decodes it into global g_buf (IRELATIVE time, before .init_array) and returns impl_fast
# `prog dump` writes the decoded buffer to stdout, `prog which` prints the function the ifunc bound (oracle).
set -e
P="$4"; W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
CRC=$(printf %08x $(( 0x$CRC ^ ${5:-0} )))
{ printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))";
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$W/blob.raw"
N=$(wc -c < "$W/blob.raw")
ENC=$(MODE="$3" perl -0777 -ne 'my @b = unpack("C*", $_); my ($k, @o) = (0x3c);
  for my $i (0..$#b) { if ($ENV{MODE} eq "tls") { push @o, $b[$i] ^ ((0x5a + 3 * $i) & 0xff) }
                       else { push @o, $b[$i] ^ $k; $k = ($k * 0x2d + 0x11) & 0xff } }
  print join(",", @o)' < "$W/blob.raw")
{ echo '#include <stdio.h>'; echo '#include <string.h>'
  echo 'volatile int g_mode = 2, g_pre, g_late;'
  echo '__thread char t_name[16] = "ldr-worker-07";'
  if [ "$3" = tls ]; then
    echo "__thread unsigned char tcfg[$N] = {$ENC};"
    echo "__thread unsigned char tbuf[$N];"
    echo '__attribute__((constructor(101))) static void tls_init(void) {'
    echo '  for (unsigned i = 0; i < sizeof tcfg; i++) tbuf[i] = tcfg[i] ^ (unsigned char)(0x5a + 3 * i); }'
    echo 'static unsigned char *cfg(void) { return tbuf; }'
  else
    echo "static const unsigned char enc[$N] = {$ENC};"
    echo "unsigned char g_buf[$N];"
    echo "__thread unsigned char tbuf[64];"
    echo 'static unsigned char *cfg(void) { return g_buf; }'
  fi
  echo '__attribute__((noinline)) static const char *impl_fast(void) { return "impl_fast"; }'
  echo '__attribute__((noinline)) static const char *impl_slow(void) { return "impl_slow"; }'
  echo 'static const char *(*pick_resolver(void))(void) {'
  [ "$3" = ifunc ] && echo '  unsigned char k = 0x3c; for (unsigned i = 0; i < sizeof enc; i++) { g_buf[i] = enc[i] ^ k; k = k * 0x2d + 0x11; }'
  echo '  return g_mode == 2 ? impl_fast : impl_slow; }'
  echo 'const char *pick(void) __attribute__((ifunc("pick_resolver")));'
  echo 'static void pre_hook(int c, char **v, char **e) { g_pre = 1; }'
  echo '__attribute__((section(".preinit_array"), used)) static void (*p_pre)(int, char **, char **) = pre_hook;'
  echo '__attribute__((constructor(202))) static void late_init(void) { g_late = g_pre + 1; }'
  echo '__attribute__((destructor)) static void cfg_wipe(void) { memset(cfg(), 0, 8); }'
  echo 'int main(int c, char **v) {'
  echo "  if (c > 1 && !strcmp(v[1], \"dump\")) { fwrite(cfg(), 1, $N, stdout); return 0; }"
  echo '  if (c > 1 && !strcmp(v[1], "which")) { puts(pick()); return 0; }'
  echo '  printf("%s %d\n", t_name, g_late); return 0; }'
} > "$W/m.c"
"$2" -O2 -fPIE -pie -o "$1" "$W/m.c"
rm -rf "$W"
