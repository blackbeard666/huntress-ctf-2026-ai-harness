#!/bin/sh
# Regenerate gnat_* fixtures: gcc (no GNAT on this host) builds a C image laid out like a gnatbind'ed Ada program
# (_ada_<main>/adainit/adafinal/ada_main___elabb symbols, binder main-program-name + GNAT Version strings,
# Ada Exception_Data structs, a hand-written DWARF4 compile unit with producer "GNU Ada 13.3.0" + DW_LANG_Ada2005).
set -e
cd "$(dirname "$0")"
T=${TMPDIR:-/tmp}/gnatfx; mkdir -p "$T"
cat > "$T/ada.c" <<'C'
struct exc { char nhbo, lang; int name_len; const char *full_name; void *htable, *foreign, *hook; };
const char ada_main_program_name[] = "_ada_cfg_main";
const char GNAT_Version[] = "GNAT Version: 13.3.0";
struct exc constraint_error = {0, 'A', 17, "CONSTRAINT_ERROR", 0, 0, 0};
struct exc program_error = {0, 'A', 14, "PROGRAM_ERROR", 0, 0, 0};
struct exc cfg_main__bad_config = {0, 'A', 20, "CFG_MAIN.BAD_CONFIG", 0, 0, 0};
struct exc cfg_util__key_error = {0, 'A', 19, "CFG_UTIL.KEY_ERROR", 0, 0, 0};
volatile int sink;
void __gnat_rcheck_CE_Explicit_Raise(void) { sink = 1; }
void ada_main___elabb(void) { sink = 2; }
void cfg_util___elabs(void) { sink = 3; }
void adainit(void) { ada_main___elabb(); cfg_util___elabs(); }
void adafinal(void) { sink = 4; }
unsigned char cfg_util__xor_byte(unsigned char b) { return b ^ 0x5a; }
void cfg_main__decode_blob(unsigned char *p, int n) { for (int i = 0; i < n; i++) p[i] = cfg_util__xor_byte(p[i]); }
void _ada_cfg_main(void) { unsigned char b[4] = {1, 2, 3, 4}; cfg_main__decode_blob(b, 4); sink = b[0]; }
int main(void) { adainit(); _ada_cfg_main(); adafinal(); return sink == 99; }
C
cat > "$T/dw.s" <<'S'
	.section .debug_abbrev,"",@progbits
.Labbrev:
	.uleb128 1
	.uleb128 0x11
	.byte 0
	.uleb128 0x25
	.uleb128 0x08
	.uleb128 0x13
	.uleb128 0x0b
	.uleb128 0x03
	.uleb128 0x0e
	.byte 0, 0
	.byte 0
	.section .debug_info,"",@progbits
	.long .Lend - .Lstart
.Lstart:
	.value 4
	.long .Labbrev
	.byte 8
	.uleb128 1
	.string "GNU Ada 13.3.0 -O2 -gnatn -g -mtune=generic -march=x86-64"
	.byte 0x2e
	.long .Lname
.Lend:
	.section .debug_str,"MS",@progbits,1
.Lname:
	.string "cfg_main.adb"
S
gcc -O1 -fno-inline -no-pie -o gnat_synth_ada2005.bin "$T/ada.c" "$T/dw.s"
strip -s -o gnat_synth_stripped.bin gnat_synth_ada2005.bin
printf 'int main(void){return 0;}\n' > "$T/plain.c"
gcc -O1 -g -no-pie -o gnat_decoy_plain_c.bin "$T/plain.c"
printf 'GNAT Version: 14.2.0\n_ada_fake_main adainit adafinal __gnat_raise GNU Ada 14.2.0 CFG_MAIN.BAD_CONFIG\n' > gnat_decoy_text_impostor.bin
