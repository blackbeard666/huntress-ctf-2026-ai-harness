#!/bin/bash
# usage: kmod_gen.sh out.ko kind json key
# kind: attr    (gcc -O2 -c: kernel-style .modinfo / __versions / .gnu.linkonce.this_module / ___ksymtab+ sections via
#                __attribute__((section)), init_module/cleanup_module aliases, blob in .rodata; ld -r with a 2nd object
#                = the .mod.o, like kbuild's final link)
#     | objcopy (gcc -O2 -c of a bare module, blob in .data, then objcopy --add-section .modinfo=<NUL-joined file>:
#                no __versions, no exports, empty depends=)
#     | plain   (the attr source minus every module section: an ordinary x86-64 ET_REL .o -- a DECOY for the format)
#     | trunc   (the attr .ko cut to its first 2 KiB: a DECOY -- section table past EOF)
# blob = {char m[4]; u8 ver, key; u16 len; u32 crc; u8 body[]}; crc32 = gzip trailer of the JSON (coreutils), body = JSON xor key (perl).
set -e
OUT=$(readlink -f "$1"); P="$3"; K=$(( ${4:-0} )); W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
BODY=$(perl -e 'print join ",", map { ord($_) ^ $ARGV[1] } split //, $ARGV[0]' "$P" "$K")
BLOB="struct hcfg { char m[4]; unsigned char ver, key; unsigned short len; unsigned int crc; unsigned char body[$LEN]; };"
case "$2" in
  attr|plain|trunc) cat > "$W/m.c" <<C
$BLOB
#define MI(id, s) static const char __UNIQUE_ID_##id[] __attribute__((section(".modinfo"), used, aligned(1))) = s
struct kernel_symbol { int value_offset, name_offset, namespace_offset; };
static const struct hcfg hcfg_blob __attribute__((used)) = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};
int rk_hide_pid(int pid) { return pid ^ hcfg_blob.len; }
int rk_filter_dirent(int x) { return x + hcfg_blob.body[0]; }
static int __attribute__((used)) rootkit_init(void) { return rk_hide_pid(1) & 0; }
static void __attribute__((used)) rootkit_exit(void) { }
#ifndef PLAIN
int init_module(void) __attribute__((alias("rootkit_init")));
void cleanup_module(void) __attribute__((alias("rootkit_exit")));
MI(license, "license=GPL");
MI(author, "author=Huntress Arena <arena@example.invalid>");
MI(description, "description=boundary crossing LKM sample");
MI(version, "version=1.3.7");
MI(alias, "alias=net-pf-31");
MI(parm, "parm=hide_pid:pid to hide (int)");
MI(parmtype, "parmtype=hide_pid:int");
static const char __kstrtab_rk_hide_pid[] __attribute__((section("__ksymtab_strings"), used, aligned(1))) = "rk_hide_pid";
static const char __kstrtab_rk_filter_dirent[] __attribute__((section("__ksymtab_strings"), used, aligned(1))) = "rk_filter_dirent";
static const struct kernel_symbol __ksymtab_rk_hide_pid __attribute__((section("___ksymtab+rk_hide_pid"), used)) = {0, 0, 0};
static const struct kernel_symbol __ksymtab_rk_filter_dirent __attribute__((section("___ksymtab_gpl+rk_filter_dirent"), used)) = {0, 0, 0};
#endif
C
     cat > "$W/m.mod.c" <<C
#define MI(id, s) static const char __UNIQUE_ID_##id[] __attribute__((section(".modinfo"), used, aligned(1))) = s
struct modversion_info { unsigned long crc; char name[64 - sizeof(unsigned long)]; };
struct module { int state; void *next, *prev; char name[64 - sizeof(unsigned long)]; int (*init)(void); void (*exit)(void); };
extern int init_module(void); extern void cleanup_module(void);
struct module __this_module __attribute__((section(".gnu.linkonce.this_module"), used)) = {
  .name = "hcfg_rootkit", .init = init_module, .exit = cleanup_module };
MI(retpoline, "retpoline=Y");
MI(name, "name=hcfg_rootkit");
MI(depends, "depends=nf_tables,x_tables");
MI(vermagic, "vermagic=6.8.0-45-generic SMP preempt mod_unload modversions ");
MI(srcversion, "srcversion=4F1C2A9D0B3E8E7A6C5D4B3");
static const struct modversion_info ____versions[] __attribute__((used, section("__versions"))) = {
  { 0x7f4e2a1b, "module_layout" }, { 0x92997ed8, "_printk" }, { 0x0c1a2b3d, "kallsyms_lookup_name" },
  { 0xdeadbeef, "nf_register_net_hook" } };
C
     if [ "$2" = plain ]; then gcc -O2 -fno-asynchronous-unwind-tables -DPLAIN -c -o "$OUT" "$W/m.c"
     else
       gcc -O2 -fno-asynchronous-unwind-tables -c -o "$W/m.o" "$W/m.c"
       gcc -O2 -fno-asynchronous-unwind-tables -c -o "$W/m.mod.o" "$W/m.mod.c"
       ld -r -o "$W/m.ko" "$W/m.o" "$W/m.mod.o"
       if [ "$2" = trunc ]; then head -c 2048 "$W/m.ko" > "$OUT"; else cp "$W/m.ko" "$OUT"; fi
     fi ;;
  objcopy) cat > "$W/b.c" <<C
$BLOB
struct hcfg hcfg_cfg = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};
int init_module(void) { return hcfg_cfg.len & 0; }
void cleanup_module(void) { hcfg_cfg.ver = 0; }
C
     gcc -O2 -fno-asynchronous-unwind-tables -c -o "$W/b.o" "$W/b.c"
     printf 'license=Dual MIT/GPL\0description=keylogger shim (objcopy-built)\0author=r00t\0depends=\0name=kbd_shim\0vermagic=5.15.0-122-generic SMP mod_unload modversions \0' > "$W/mi"
     objcopy --add-section .modinfo="$W/mi" --set-section-flags .modinfo=alloc,readonly,data "$W/b.o" "$OUT" ;;
esac
rm -rf "$W"
