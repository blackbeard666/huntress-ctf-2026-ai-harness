#!/bin/bash
# apihash_gen.sh <out.bin> <algo> <code|table> "<gcc flags>" <name>...
# Hash constants come from the independent perl hasher (apihash_hash.pl); gcc compiles a dl_iterate_phdr resolver
# that walks every loaded object's .dynsym, hashes each name with <algo> and compares it with the constants
# (code: a switch of cmp imm32 in code order; table: a const uint32_t[] in .rodata).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
out=$1 algo=$2 mode=$3 flags=$4; shift 4
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
mapfile -t H < <(perl "$here/apihash_hash.pl" "$algo" "$@" | cut -d' ' -f1)
case $algo in
  ror13)  HF='uint32_t h = 0; for (; *s; s++) h = ((h >> 13) | (h << 19)) + (unsigned char)*s; return h;' ;;
  djb2)   HF='uint32_t h = 5381; for (; *s; s++) h = h * 33 + (unsigned char)*s; return h;' ;;
  fnv1a)  HF='uint32_t h = 0x811C9DC5u; for (; *s; s++) { h ^= (unsigned char)*s; h *= 0x01000193u; } return h;' ;;
  crc32)  HF='uint32_t h = ~0u; for (; *s; s++) { h ^= (unsigned char)*s; for (int k = 0; k < 8; k++) h = (h >> 1) ^ (0xEDB88320u & -(h & 1)); } return ~h;' ;;
esac
{
  echo '#define _GNU_SOURCE'
  echo '#include <link.h>'
  echo '#include <stdint.h>'
  echo '#include <string.h>'
  echo 'static void *slot['$#'];'
  echo '__attribute__((noinline)) static uint32_t api_hash(const char *s) { '"$HF"' }'
  if [ "$mode" = table ]; then
    echo -n 'static const uint32_t wanted[] = {'; printf '%su, ' "${H[@]}"; echo '};'
    echo '__attribute__((noinline)) static int which(uint32_t h) { for (unsigned i = 0; i < sizeof wanted / sizeof *wanted; i++) if (wanted[i] == h) return (int)i; return -1; }'
  else
    echo '__attribute__((noinline)) static int which(uint32_t h) {'
    i=0; for h in "${H[@]}"; do echo "  if (h == ${h}u) return $i;"; i=$((i+1)); done
    echo '  return -1; }'
  fi
  cat <<'C'
static int cb(struct dl_phdr_info *info, size_t sz, void *u) {
  (void)sz; (void)u;
  ElfW(Sym) *sym = 0; const char *str = 0; uint32_t *gh = 0;
  for (int i = 0; i < info->dlpi_phnum; i++) {
    if (info->dlpi_phdr[i].p_type != PT_DYNAMIC) continue;
    for (ElfW(Dyn) *d = (ElfW(Dyn) *)(info->dlpi_addr + info->dlpi_phdr[i].p_vaddr); d->d_tag; d++) {
      if (d->d_tag == DT_SYMTAB) sym = (ElfW(Sym) *)d->d_un.d_ptr;
      if (d->d_tag == DT_STRTAB) str = (const char *)d->d_un.d_ptr;
      if (d->d_tag == DT_GNU_HASH) gh = (uint32_t *)d->d_un.d_ptr;
    }
  }
  if (!sym || !str || !gh || !strstr(info->dlpi_name, "libc.so")) return 0;
  if ((uintptr_t)sym < info->dlpi_addr) { sym = (void *)((char *)sym + info->dlpi_addr); str += info->dlpi_addr; gh = (void *)((char *)gh + info->dlpi_addr); }
  uint32_t nsym = 0, *bk = gh + 4 + gh[2] * (sizeof(ElfW(Addr)) / 4);
  for (uint32_t b = 0; b < gh[0]; b++) if (bk[b] > nsym) nsym = bk[b];
  if (nsym) while (!(bk[gh[0] + nsym - gh[1]] & 1)) nsym++;
  for (uint32_t k = gh[1]; k <= nsym; k++) {
    int w = which(api_hash(str + sym[k].st_name));
    if (w >= 0 && !slot[w]) slot[w] = (void *)(info->dlpi_addr + sym[k].st_value);
  }
  return 0;
}
int main(void) {
  dl_iterate_phdr(cb, 0);
  if (slot[0] && slot[1]) ((int (*)(const char *, ...))slot[1])("%s\n", ((char *(*)(const char *))slot[0])("HOME"));
  return 0;
}
C
} > "$tmp/r.c"
gcc $flags -o "$here/$out" "$tmp/r.c"
strip "$here/$out"
