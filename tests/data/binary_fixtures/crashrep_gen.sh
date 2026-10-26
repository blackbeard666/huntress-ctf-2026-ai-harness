#!/usr/bin/env bash
# Generator for crashrep_* fixtures (textual crash REPORTS -> lib.binary.crash_report_field). Every .bin is the real
# stderr / report of an independent toolchain: gcc -fsanitize=address|undefined, gcc -fstack-protector-all + glibc,
# javac + java (incl. a real hs_err_pid log via sun.misc.Unsafe), go, rustc (RUST_BACKTRACE=1), python3, dotnet;
# dmesg lines are printf'd with the kernel's own printk layout (arch/x86/mm/fault.c show_signal_msg/print_vma_addr,
# arch/x86/kernel/traps.c); zip CLI member; iconv UTF-16LE. Expected facts: bash crashrep_oracle.sh (grep/sed/awk).
# usage: bash crashrep_gen.sh   (from tests/data/binary_fixtures; needs gcc java javac go rustc python3 dotnet zip iconv)
set -uo pipefail
here=$(pwd); w=$(mktemp -d); trap 'rm -rf "$w"' EXIT
cd "$w"
cat > asan.c <<'C'
#include <stdlib.h>
int victim(int *p, int i) { return p[i]; }
int main(int c, char **v) { int *p = malloc(3 * sizeof(int)); int r = victim(p, 3 + c - 1); free(p); return r; }
C
cat > uaf.c <<'C'
#include <stdlib.h>
void writer(char *p) { p[2] = 'x'; }
int main() { char *p = malloc(16); free(p); writer(p); return 0; }
C
cat > ubsan.c <<'C'
#include <limits.h>
int add(int a, int b) { return a + b; }
int main(int c, char **v) { return add(INT_MAX, c) & 1; }
C
cat > ssp.c <<'C'
#include <string.h>
void copy(const char *s) { char b[8]; strcpy(b, s); }
int main(int c, char **v) { copy("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"); return 0; }
C
cat > df.c <<'C'
#include <stdlib.h>
int main() { void *p = malloc(32); free(p); free(p); return 0; }
C
gcc -g -O0 -fsanitize=address -o asan asan.c && ./asan 2> "$here/crashrep_asan_hbo_read.bin"
cp asan "$here/crashrep_decoy_asan_elf.bin"   # DECOY: instrumented ELF, sanitizer format strings but no report
gcc -g -O0 -fsanitize=address -o uaf uaf.c && ./uaf 2> "$here/crashrep_asan_uaf_write.bin"
gcc -g -O0 -fsanitize=undefined -o ubsan ubsan.c && ./ubsan 2> "$here/crashrep_ubsan_sio.bin"
gcc -g -O0 -fstack-protector-all -o ssp ssp.c && (./ssp 2> "$here/crashrep_glibc_ssp.bin")
gcc -g -O0 -o df df.c && (./df 2> "$here/crashrep_glibc_tcache_df.bin")
mkdir -p j && cat > j/App.java <<'J'
package demo.app;
public class App {
    static int parse(String s) { return Integer.parseInt(s); }
    static int load(String s) {
        try { return parse(s); } catch (NumberFormatException e) { throw new IllegalStateException("bad config value", e); }
    }
    public static void main(String[] a) { System.out.println(load("x1")); }
}
J
javac -d j j/App.java && java -cp j demo.app.App 2> "$here/crashrep_java_causedby.bin"
cat > Unsafe.java <<'J'
import java.lang.reflect.Field;
public class Unsafe { public static void main(String[] a) throws Exception {
  Field f = sun.misc.Unsafe.class.getDeclaredField("theUnsafe"); f.setAccessible(true);
  sun.misc.Unsafe u = (sun.misc.Unsafe) f.get(null); u.putAddress(0x10L, 1L); } }
J
javac -d . Unsafe.java 2>/dev/null; java -XX:ErrorFile="$w/hs_err_pid%p.log" -XX:-CreateCoredumpOnCrash -cp . Unsafe >/dev/null 2>&1
# keep the header + THREAD section only (the PROCESS/SYSTEM sections carry the host environment)
sed "/^---------------  P R O C E S S/,\$d" "$w"/hs_err_pid*.log > "$here/crashrep_hserr_unsafe.bin"
mkdir -p g && cat > g/main.go <<'G'
package main
import ("fmt"; "os")
func pick(xs []int, i int) int { return xs[i] }
func main() { xs := []int{1, 2, 3}; fmt.Println(pick(xs, len(os.Args)+4)) }
G
(cd g && go mod init demo >/dev/null 2>&1; go build -gcflags=all=-l -o m . && ./m 2> "$here/crashrep_go_index.bin")
cat > gonil.go <<'G'
package main
type T struct{ n int }
func (t *T) get() int { return t.n }
func main() { var t *T; println(t.get()) }
G
go build -gcflags=all=-l -o gonil gonil.go && ./gonil 2> "$here/crashrep_go_nil.bin"
mkdir -p r && cat > r/main.rs <<'R'
fn parse(s: &str) -> u32 { s.parse::<u32>().unwrap() }
fn main() { let v = std::env::args().count(); println!("{}", parse(if v > 5 { "1" } else { "nope" })); }
R
(cd r && rustc -g -o m main.rs && RUST_BACKTRACE=1 ./m 2> "$here/crashrep_rust_unwrap.bin")
cat > pyc.py <<'P'
def inner(d):
    return d["token"]
def outer():
    return inner({})
outer()
P
python3 -I pyc.py 2> "$here/crashrep_python_keyerror.bin"
cat > pychain.py <<'P'
import json
def load(s):
    try:
        return json.loads(s)
    except ValueError as e:
        raise RuntimeError("config broken") from e
load("{bad")
P
python3 -I pychain.py 2> "$here/crashrep_python_chain.bin"
mkdir -p dn && cat > dn/dn.csproj <<'X'
<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>
X
cat > dn/Program.cs <<'X'
namespace Demo.Svc {
  static class Loader {
    static string Read(string[] a, int i) { return a[i]; }
    public static void Main(string[] args) { System.Console.WriteLine(Read(args, 2)); }
  }
}
X
(cd dn && dotnet build -c Debug -o out -v q >/dev/null 2>&1 && (dotnet out/dn.dll 2> "$here/crashrep_dotnet_ioore.bin"))
iconv -f UTF-8 -t UTF-16LE "$here/crashrep_dotnet_ioore.bin" > "$here/crashrep_utf16_dotnet.bin"
printf '[ 4211.338190] %s[%d]: segfault at %lx ip %016lx sp %016lx error %lx in %s[%lx+%lx] likely on CPU %d (core %d, socket %d)\n[ 4211.338204] Code: 48 89 e5 48 89 7d f8 <8b> 00 5d c3\n' \
  vuln 31337 0 0x000055d0c4a0113d 0x00007ffd1f2e0a40 4 vuln 0x55d0c4a01000 0x1000 3 3 0 > "$here/crashrep_dmesg_segv_read.bin"
printf '[ 9.000001] %s[%d]: segfault at %lx ip %016lx sp %016lx error %lx in %s[%lx+%lx]\n' \
  writer 77 0x7f00deadbeef 0x0000000000401146 0x00007ffc00001000 6 writer 0x401000 0x1000 > "$here/crashrep_dmesg_segv_write.bin"
printf 'INFO 2026-10-26 worker started\nWARN retrying after Exception in handler (see docs)\nTraceback logging disabled; panic: none\n' > "$here/crashrep_decoy_log.bin"
printf 'Exception in thread "main" java.lang.IllegalStateException: bad config value\n' > "$here/crashrep_decoy_trunc.bin"
mkdir -p z/crash z/assets && cp "$here/crashrep_go_nil.bin" z/crash/panic.txt && printf 'not a report\n' > z/assets/readme.txt
(cd z && rm -f ../m.zip && zip -q -X ../m.zip assets/readme.txt crash/panic.txt) && cp m.zip "$here/crashrep_zip_go_nil.bin"
