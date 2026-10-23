#!/bin/bash
# Generate GNU symbol-versioning / interposition fixtures (compiled only, NEVER run or preloaded).
# usage (from this dir): bash symver_gen.sh
set -e
T=${TMPDIR:-/tmp}/symver; mkdir -p "$T"
D=$(cd "$(dirname "$0")" && pwd)
# 1) versioned config getter: cfg_get@V1 (decoy) + cfg_get@@V2 (HCFG), weak/protected/unique/local symbols
cat > "$T/cfg.c" <<'C'
#include <stdio.h>
const char *cfg_get_v1(void) { return "HCFG{decoy_v1_not_this_one}"; }
const char *cfg_get_v2(void) { return "HCFG{symver_default_v2_wins}"; }
__asm__(".symver cfg_get_v1, cfg_get@V1");
__asm__(".symver cfg_get_v2, cfg_get@@V2");
__attribute__((weak)) int cfg_hook(int x) { return x + 1; }
__attribute__((visibility("protected"))) int cfg_level = 7;
__attribute__((visibility("hidden"))) int cfg_secret(void) { return 42; }
int cfg_count(void) { puts("count"); return cfg_secret(); }
__asm__(".globl cfg_unique\n.section .data.cfg_unique,\"aw\"\n.type cfg_unique, @gnu_unique_object\n"
        ".size cfg_unique, 4\ncfg_unique: .long 5\n.text");
C
cat > "$T/cfg.map" <<'M'
V1 { global: cfg_get; cfg_count; local: *; };
V2 { global: cfg_get; cfg_hook; cfg_level; cfg_unique; } V1;
M
gcc -O2 -fPIC -shared -Wl,--version-script="$T/cfg.map" -Wl,-soname,libcfg.so.2 -o "$D/symver_cfg_lib.bin" "$T/cfg.c"
# 2) LD_PRELOAD shim exporting libc names; open/getenv/__libc_start_main forward via dlsym(RTLD_NEXT, ...)
cat > "$T/shim.c" <<'C'
#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static const char cfg[] = "HCFG{preload_shim_cfg}";
int open(const char *p, int fl, ...) {
  static int (*real)(const char *, int, ...);
  va_list ap; va_start(ap, fl); int m = va_arg(ap, int); va_end(ap);
  if (!real) real = (int (*)(const char *, int, ...))dlsym(RTLD_NEXT, "open");
  if (strstr(p, "secret")) p = "/dev/null";
  return real(p, fl, m);
}
char *getenv(const char *n) {
  static char *(*real)(const char *);
  if (!strcmp(n, "HUNTRESS_CFG")) return (char *)cfg;
  if (!real) real = (char *(*)(const char *))dlsym(RTLD_NEXT, "getenv");
  return real(n);
}
int __libc_start_main(int (*m)(int, char **, char **), int c, char **v, void (*i)(void), void (*f)(void),
                      void (*r)(void), void *s) {
  int (*real)(int (*)(int, char **, char **), int, char **, void (*)(void), void (*)(void), void (*)(void), void *)
      = dlsym(RTLD_NEXT, "__libc_start_main");
  return real(m, c, v, i, f, r, s);
}
int puts(const char *s) { fputs("[shim] ", stderr); return fputs(s, stdout); }   /* interposed, no RTLD_NEXT */
int shim_ready(void) { return 1; }
C
gcc -O2 -fPIC -shared -o "$D/symver_preload_shim.bin" "$T/shim.c" -ldl
# 3) -O0 -fno-plt shim: RTLD_NEXT resolved in a static lazy helper; three-level versions (VERS_1.0 <- 1.1 <- 2.0)
cat > "$T/shim2.c" <<'C'
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stddef.h>
static void *(*real_dlsym)(void *, const char *);
static void *next_sym(const char *n) { return dlsym(RTLD_NEXT, n); }
void *malloc(size_t n) { static void *(*r)(size_t); if (!r) r = next_sym("malloc"); return r(n); }
void free(void *p) { static void (*r)(void *); if (!r) r = next_sym("free"); r(p); }
int unsetenv(const char *n) { (void)n; return 0; }
const char *api_cfg_old(void) { return "HCFG{old_api_decoy}"; }
const char *api_cfg_mid(void) { return "HCFG{mid_api_decoy}"; }
const char *api_cfg_new(void) { return "HCFG{vers_2_0_default}"; }
__asm__(".symver api_cfg_old, api_cfg@VERS_1.0");
__asm__(".symver api_cfg_mid, api_cfg@VERS_1.1");
__asm__(".symver api_cfg_new, api_cfg@@VERS_2.0");
__attribute__((weak)) void *dlsym_hook(void) { return (void *)real_dlsym; }
C
cat > "$T/shim2.map" <<'M'
VERS_1.0 { global: api_cfg; malloc; free; unsetenv; local: *; };
VERS_1.1 { global: api_cfg; } VERS_1.0;
VERS_2.0 { global: api_cfg; dlsym_hook; } VERS_1.1;
M
gcc -O0 -fno-plt -fPIC -shared -Wl,--version-script="$T/shim2.map" -o "$D/symver_noplt_shim.bin" "$T/shim2.c" -ldl
# 4) decoys: a static ELF (no .gnu.version* / no dynsym) and a text file renamed .so
printf 'int main(void){return 0;}\n' > "$T/s.c"
gcc -O2 -static -o "$T/static" "$T/s.c" && strip -o "$D/symver_decoy_static.bin" "$T/static" || true
printf 'V1 { global: cfg_get; };\nGLIBC_2.2.5 open@@V2 dlsym(RTLD_NEXT)\n' > "$D/symver_decoy_text.bin"
