#!/usr/bin/env bash
# Independent oracle for crashrep_* fixtures: grep -P / sed / awk / unzip -p / iconv over the report text (never
# lib.binary). `cwe` and `format` are the PLANTED bug of crashrep_gen.sh's source (heap OOB read -> CWE-125, ...).
# usage: bash crashrep_oracle.sh   (from tests/data/binary_fixtures; rewrites crashrep_*.json)
set -uo pipefail
hx() { [ -n "$1" ] && printf '0x%x' "$((16#${1#0x}))" || printf none; }
nz() { [ -n "$1" ] && printf '%s' "$1" || printf none; }
emit() {   # name decoy note k1 v1 k2 v2 ...
  local n=$1 decoy=$2 note=$3; shift 3
  local facts='{}'
  while [ $# -ge 2 ]; do facts=$(jq -c --arg k "$1" --arg v "$2" '. + {($k): $v}' <<<"$facts"); shift 2; done
  jq -n --argjson f "$facts" --arg n "$n" --argjson d "$decoy" --arg note "$note" '{family: "crash_report",
    encoding: "none", expected_offset: null, expected_config: null, expected_facts: $f,
    generator_cmd: ("bash crashrep_gen.sh   # " + $note), oracle_cmd: ("bash crashrep_oracle.sh   # grep -P/sed/awk over " + $n + ".bin"),
    decoy: $d, note: "lib.binary.crash_report_field(data, key); fact names SPECULATIVE (off-peak breadth build)"}' > "$n.json"
}
f=crashrep_asan_hbo_read.bin
emit ${f%.bin} false "gcc -fsanitize=address heap OOB read p[3] of int[3]" found true format asan \
  kind "$(grep -oP 'AddressSanitizer: \K[\w-]+(?= on address)' $f)" \
  fault_addr "$(hx $(grep -oP 'on address \K0x[0-9a-f]+' $f))" pc "$(hx $(grep -oP ' at pc \K0x[0-9a-f]+' $f))" \
  access "$(grep -oP '^(READ|WRITE) of size \d+' $f)" access_type READ access_size "$(grep -oP '^READ of size \K\d+' $f)" \
  fault_function "$(grep -m1 -oP '^\s+#0 0x[0-9a-f]+ in \K\S+' $f)" \
  fault_line "$(grep -m1 -oP '^\s+#0 0x[0-9a-f]+ in \S+ \S+:\K\d+' $f)" \
  region_size "$(grep -oP '\d+(?=-byte region)' $f)" cwe CWE-125 cwe_specific CWE-122 bug_class out_of_bounds_read
f=crashrep_asan_uaf_write.bin
emit ${f%.bin} false "gcc -fsanitize=address write after free()" found true format asan \
  kind "$(grep -oP 'AddressSanitizer: \K[\w-]+(?= on address)' $f)" \
  fault_addr "$(hx $(grep -oP 'on address \K0x[0-9a-f]+' $f))" access "$(grep -oP '^(READ|WRITE) of size \d+' $f)" \
  fault_function "$(grep -m1 -oP '^\s+#0 0x[0-9a-f]+ in \K\S+' $f)" \
  free_function "$(awk '/^freed by thread/{f=1;next} f&&/#[0-9]+ /&&$4!="free"{print $4;exit}' $f)" \
  cwe CWE-416 bug_class use_after_free
f=crashrep_ubsan_sio.bin
emit ${f%.bin} false "gcc -fsanitize=undefined INT_MAX + 1" found true format ubsan \
  kind "$(sed -n 's/.*runtime error: \([^:]*\):.*/\1/p' $f)" message "$(sed -n 's/.*runtime error: //p' $f)" \
  fault_file "$(cut -d: -f1 $f)" fault_line "$(cut -d: -f2 $f)" cwe CWE-190
f=crashrep_glibc_ssp.bin
emit ${f%.bin} false "gcc -fstack-protector-all strcpy into char[8]" found true format glibc \
  kind "$(grep -oP '\*\*\* \K[^*]+(?= \*\*\*)' $f)" message "$(head -1 $f)" signal SIGABRT access_type WRITE \
  cwe CWE-787 cwe_specific CWE-121
f=crashrep_glibc_tcache_df.bin
emit ${f%.bin} false "glibc free(p); free(p)" found true format glibc kind "$(head -1 $f)" cwe CWE-415 bug_class double_free
f=crashrep_java_causedby.bin
emit ${f%.bin} false "javac+java IllegalStateException wrapping NumberFormatException" found true format java \
  kind "$(sed -n 's/^Exception in thread "[^"]*" \([^:]*\):.*/\1/p' $f)" \
  message "$(sed -n 's/^Exception in thread "[^"]*" [^:]*: //p' $f)" \
  thread "$(sed -n 's/^Exception in thread "\([^"]*\)".*/\1/p' $f)" \
  fault_function "$(grep -m1 -oP '^\tat \K[^(]+' $f)" fault_line "$(grep -m1 -oP '^\tat [^(]+\([^:]+:\K\d+' $f)" \
  outer_function "$(awk '/^Caused by/{exit} /^\tat /{l=$2} END{}{} /^Caused by/{exit} {last=l} END{sub(/\(.*/,"",last); print last}' $f)" \
  frame_count "$(awk '/^Caused by/{exit} /^\tat /{n++} END{print n}' $f)" \
  root_cause "$(grep -oP '^Caused by: \K[^:]+' $f | tail -1)" \
  root_cause_function "$(awk '/^Caused by/{c=1;next} c&&/^\tat /&&$2!~/^java\./{s=$2; sub(/^.*\//,"",s); sub(/\(.*/,"",s); print s; exit}' $f)" \
  index none cwe CWE-248
f=crashrep_hserr_unsafe.bin
emit ${f%.bin} false "java sun.misc.Unsafe.putAddress(0x10) -> JVM SIGSEGV hs_err" found true format hs_err \
  signal "$(grep -m1 -oP '^#\s+\KSIG\w+' $f)" signal_number "$(grep -m1 -oP '^#\s+SIG\w+ \(\K0x[0-9a-f]+' $f)" \
  pc "$(hx $(grep -m1 -oP 'at pc=\K0x[0-9a-f]+' $f))" pid "$(grep -m1 -oP 'pid=\K\d+' $f)" \
  fault_addr "$(hx $(grep -oP 'si_addr: \K0x[0-9a-f]+' $f))" \
  problematic_library "$(awk '/Problematic frame:/{getline; match($0,/\[[^+]+/); print substr($0,RSTART+1,RLENGTH-1); exit}' $f)" \
  problematic_symbol "$(awk '/Problematic frame:/{getline; print $NF; exit}' $f | sed 's/+0x[0-9a-f]*$//')" \
  fault_function "$(grep -oP '^[jJ]\s+\K[^(]+' $f | grep -vE '^(jdk|sun|java)\.' | head -1)" cwe CWE-476
f=crashrep_go_index.bin
emit ${f%.bin} false "go xs[5] of len 3" found true format go message "$(sed -n 's/^panic: //p' $f)" \
  kind "$(sed -n 's/^panic: runtime error: \([^[]*\) \[.*/\1/p' $f)" \
  fault_function "$(awk '/^goroutine /{getline; sub(/\([^()]*\)$/,""); print; exit}' $f)" \
  fault_line "$(awk '/^goroutine /{getline; getline; split($1,a,":"); print a[2]; exit}' $f)" \
  thread "$(grep -oP '^goroutine \K\d+' $f)" index "$(grep -oP 'out of range \[\K\d+' $f)" \
  length "$(grep -oP 'with length \K\d+' $f)" cwe CWE-125
f=crashrep_go_nil.bin
emit ${f%.bin} false "go method on nil *T" found true format go \
  fault_addr "$(hx $(grep -oP 'addr=\K0x[0-9a-f]+' $f))" pc "$(hx $(grep -oP ' pc=\K0x[0-9a-f]+' $f))" \
  signal "$(grep -oP '^\[signal \K\w+' $f)" \
  fault_function "$(awk '/^goroutine /{getline; sub(/\([^()]*\)$/,""); print; exit}' $f)" cwe CWE-476 \
  bug_class null_pointer_dereference
f=crashrep_rust_unwrap.bin
emit ${f%.bin} false "rustc RUST_BACKTRACE=1 \"nope\".parse::<u32>().unwrap()" found true format rust kind panic \
  message "$(awk '/panicked at/{getline; print; exit}' $f)" thread "$(grep -oP "^thread '\K[^']+" $f)" \
  fault_file "$(grep -oP 'panicked at \K[^:]+' $f)" fault_line "$(grep -oP 'panicked at [^:]+:\K\d+' $f)" \
  fault_function "$(grep -oP '^\s+\d+: \K\S+' $f | grep -vE '^(std|core|alloc|__rustc)::|^rust_' | head -1)" \
  top_frame "$(grep -m1 -oP '^\s+0: \K\S+' $f)" error_type "$(grep -oP '`Err` value: \K\w+' $f)" cwe CWE-248
f=crashrep_python_keyerror.bin
emit ${f%.bin} false "python3 d['token'] on {}" found true format python \
  kind "$(tail -1 $f | cut -d: -f1)" message "$(tail -1 $f | cut -d: -f2- | sed 's/^ //')" \
  fault_function "$(grep -oP 'line \d+, in \K.+' $f | tail -1)" fault_line "$(grep -oP 'line \K\d+(?=, in )' $f | tail -1)" \
  outer_function "$(grep -oP 'line \d+, in \K.+' $f | head -1)" \
  frames "$(grep -oP 'line \d+, in \K.+' $f | tac | jq -R . | jq -sc .)" cwe CWE-248
f=crashrep_python_chain.bin
emit ${f%.bin} false "python3 raise RuntimeError from JSONDecodeError" found true format python \
  kind "$(tail -1 $f | cut -d: -f1)" message "$(tail -1 $f | cut -d: -f2- | sed 's/^ //')" \
  root_cause "$(grep -m1 -oP '^[\w.]+Error(?=:)' $f)" \
  fault_function "$(grep -oP 'line \d+, in \K.+' $f | tail -1)" frame_count 2 cwe CWE-248
for f in crashrep_dotnet_ioore.bin crashrep_utf16_dotnet.bin; do
  t=$(if [ $f = crashrep_utf16_dotnet.bin ]; then iconv -f UTF-16LE -t UTF-8 $f; else cat $f; fi)
  emit ${f%.bin} false "dotnet net10.0 args[2] on empty args$( [ $f = crashrep_utf16_dotnet.bin ] && echo ' | iconv -t UTF-16LE')" \
    found true format dotnet kind "$(sed -n 's/^Unhandled exception\. \([^:]*\):.*/\1/p' <<<"$t")" \
    message "$(sed -n 's/^Unhandled exception\. [^:]*: //p' <<<"$t")" \
    fault_function "$(grep -m1 -oP '^\s+at \K[^(]+' <<<"$t")" fault_line "$(grep -m1 -oP ':line \K\d+' <<<"$t")" \
    outer_function "$(grep -oP '^\s+at \K[^(]+' <<<"$t" | tail -1)" kind_short IndexOutOfRangeException cwe CWE-125
done
for f in crashrep_dmesg_segv_read.bin crashrep_dmesg_segv_write.bin; do
  err=$(grep -oP ' error \K[0-9a-f]+' $f); ip=$(grep -oP ' ip \K[0-9a-f]+' $f); base=$(grep -oP ' in \S+\[\K[0-9a-f]+' $f)
  emit ${f%.bin} false "printf with the kernel segfault printk layout" found true format dmesg kind segfault signal SIGSEGV \
    program "$(grep -oP '\] \K[^\[]+(?=\[\d+\]: segfault)' $f)" pid "$(grep -oP '\[\K\d+(?=\]: segfault)' $f)" \
    fault_addr "$(hx $(grep -oP 'segfault at \K[0-9a-f]+' $f))" pc "$(hx $ip)" error_code "$err" \
    access_type "$( (( 16#$err & 16 )) && echo EXEC || { (( 16#$err & 2 )) && echo WRITE || echo READ; })" \
    module_offset "$(printf '0x%x' $((16#$ip - 16#$base)))" \
    cwe "$( [ "$(grep -oP 'segfault at \K[0-9a-f]+' $f)" = 0 ] && echo CWE-476 || echo CWE-119)"
done
f=crashrep_zip_go_nil.bin
t=$(unzip -p $f crash/panic.txt)
emit ${f%.bin} false "zip -X of crash/panic.txt (= crashrep_go_nil.bin) + assets/readme.txt" found true format go \
  source "$(unzip -Z1 $f | grep panic)" fault_function "$(awk '/^goroutine /{getline; sub(/\([^()]*\)$/,""); print; exit}' <<<"$t")" \
  fault_addr "$(hx $(grep -oP 'addr=\K0x[0-9a-f]+' <<<"$t"))" cwe CWE-476
for n in crashrep_decoy_log crashrep_decoy_trunc crashrep_decoy_asan_elf; do
  emit $n true "DECOY: $(case $n in *log) echo 'log text naming Exception/Traceback/panic, no trace';; *trunc) echo 'Java header line only, no frames';; *) echo 'ASan-instrumented ELF itself (format strings, no report)';; esac)" \
    found false format none kind none fault_function none fault_addr none cwe none
done
