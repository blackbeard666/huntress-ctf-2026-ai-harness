#!/bin/bash
# vcls_gen.sh: vulnerable (a) / fixed (b) twins whose bug class is planted in the source (gcc C twins, javac jars).
# Usage: bash vcls_gen.sh OUTDIR   (then: python3 vcls_mkjson.py OUTDIR)
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
common='#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
int helper_sum(int a, int b) { return a * 3 + b; }
'
mkc() { # name opt vuln_body fixed_body
  printf '%s\n%s\nint main(int c, char **v){ return target(c > 1 ? v[1] : "x", helper_sum(c, 2)); }\n' "$common" "$3" > $1_a.c
  printf '%s\n%s\nint main(int c, char **v){ return target(c > 1 ? v[1] : "x", helper_sum(c, 2)); }\n' "$common" "$4" > $1_b.c
  for s in a b; do gcc $2 -w -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-inline -o $OUT/vcls_$1_$s.bin $1_$s.c; done
}
mkc divzero "-O0" \
 'int target(const char *s, int d){ int n = (int)strlen(s) * 100; return n / d; }' \
 'int target(const char *s, int d){ int n = (int)strlen(s) * 100; if (d == 0) return -1; return n / d; }'
mkc intovf "-O2" \
 'char *target2(int n, int sz){ return malloc(n * sz); } int target(const char *s, int i){ return target2(i, (int)strlen(s)) != 0; }' \
 'char *target2(int n, int sz){ int t; if (__builtin_mul_overflow(n, sz, &t)) return 0; return malloc(t); } int target(const char *s, int i){ return target2(i, (int)strlen(s)) != 0; }'
mkc cmdinj "-O0" \
 'int target(const char *s, int i){ char cmd[128]; snprintf(cmd, sizeof cmd, "ping -c1 %s", s); return system(cmd) + i; }' \
 'int target(const char *s, int i){ char cmd[128]; if (strpbrk(s, ";|&`$")) return -1; snprintf(cmd, sizeof cmd, "ping -c1 %s", s); return system(cmd) + i; }'
mkc path "-O0" \
 'int target(const char *s, int i){ char p[256]; snprintf(p, sizeof p, "/srv/files/%s", s); return open(p, O_RDONLY) + i; }' \
 'int target(const char *s, int i){ char p[256]; if (strstr(s, "..")) return -1; snprintf(p, sizeof p, "/srv/files/%s", s); return open(p, O_RDONLY) + i; }'
mkc toctou "-O0" \
 'int target(const char *s, int i){ if (access(s, R_OK) != 0) return -1; return open(s, O_RDONLY) + i; }' \
 'int target(const char *s, int i){ int fd = open(s, O_RDONLY | O_NOFOLLOW); struct stat st; if (fd < 0 || fstat(fd, &st) != 0) return -1; return fd + i; }'
mkc dfree "-O0" \
 'int target(const char *s, int i){ char *p = malloc(32); strncpy(p, s, 31); if (i > 3) free(p); free(p); return i; }' \
 'int target(const char *s, int i){ char *p = malloc(32); strncpy(p, s, 31); free(p); return i; }'
mkj() {  # dir class < java source
  mkdir -p $1; cat > $1/$2.java; javac --release 11 -g:none -d $1/out $1/$2.java
  (cd $1/out && printf 'Main-Class: %s\n' "$2" > m.txt && jar cfm ../../$1.jar m.txt *.class)
}
mkj jdes_a StoreVulnerable <<'J'
import java.io.*;
public class StoreVulnerable {
  public static Object load(byte[] b) throws Exception { ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(b)); return in.readObject(); }
  public static void main(String[] a) throws Exception { System.out.println(load(new byte[0])); }
}
J
mkj jdes_b StoreCorrected <<'J'
import java.io.*;
public class StoreCorrected {
  public static Object load(byte[] b) throws Exception { ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(b)); in.setObjectInputFilter(ObjectInputFilter.Config.createFilter("java.lang.*;!*")); return in.readObject(); }
  public static void main(String[] a) throws Exception { System.out.println(load(new byte[0])); }
}
J
mkj jdiv_a RatioVulnerable <<'J'
public class RatioVulnerable {
  public static int ratio(int total, int parts) { return total / parts; }
  public static void main(String[] a) { System.out.println(ratio(10, a.length)); }
}
J
mkj jdiv_b RatioCorrected <<'J'
public class RatioCorrected {
  public static int ratio(int total, int parts) { if (parts == 0) return 0; return total / parts; }
  public static void main(String[] a) { System.out.println(ratio(10, a.length)); }
}
J
mkj jovf_a SizeVulnerable <<'J'
public class SizeVulnerable {
  public static int bytes(int n, int w) { return n * w + 16; }
  public static void main(String[] a) { System.out.println(bytes(a.length, 4)); }
}
J
mkj jovf_b SizeCorrected <<'J'
public class SizeCorrected {
  public static int bytes(int n, int w) { return Math.addExact(Math.multiplyExact(n, w), 16); }
  public static void main(String[] a) { System.out.println(bytes(a.length, 4)); }
}
J
mkj jobo_a FillVulnerable <<'J'
public class FillVulnerable {
  static int[] buf = new int[8];
  public static void fill(int n) { for (int i = 0; i <= n; i++) buf[i] = i; }
  public static void main(String[] a) { fill(a.length); System.out.println(buf[0]); }
}
J
mkj jobo_b FillCorrected <<'J'
public class FillCorrected {
  static int[] buf = new int[8];
  public static void fill(int n) { for (int i = 0; i < n; i++) buf[i] = i; }
  public static void main(String[] a) { fill(a.length); System.out.println(buf[0]); }
}
J
mkj jcmd_a PingVulnerable <<'J'
public class PingVulnerable {
  public static Process ping(String host) throws Exception { return Runtime.getRuntime().exec("ping -c1 " + host); }
  public static void main(String[] a) throws Exception { System.out.println(ping("x")); }
}
J
mkj jcmd_b PingCorrected <<'J'
public class PingCorrected {
  public static Process ping(String host) throws Exception { if (!host.matches("[A-Za-z0-9.-]+")) throw new IllegalArgumentException(); return Runtime.getRuntime().exec(new String[]{"ping", "-c1", host}); }
  public static void main(String[] a) throws Exception { System.out.println(ping("x")); }
}
J
mkj jpath_a FilesVulnerable <<'J'
import java.io.*;
public class FilesVulnerable {
  public static File open(String name) throws IOException { return new File("/srv/data", name); }
  public static void main(String[] a) throws Exception { System.out.println(open("x")); }
}
J
mkj jpath_b FilesCorrected <<'J'
import java.io.*;
public class FilesCorrected {
  public static File open(String name) throws IOException { File f = new File("/srv/data", name); if (!f.getCanonicalPath().startsWith("/srv/data/")) throw new IOException("traversal"); return f; }
  public static void main(String[] a) throws Exception { System.out.println(open("x")); }
}
J
mkj jsql_a UsersVulnerable <<'J'
import java.sql.*;
public class UsersVulnerable {
  public static ResultSet find(Connection c, String u) throws SQLException { Statement s = c.createStatement(); return s.executeQuery("SELECT * FROM users WHERE name='" + u + "'"); }
  public static void main(String[] a) { System.out.println("u"); }
}
J
mkj jsql_b UsersCorrected <<'J'
import java.sql.*;
public class UsersCorrected {
  public static ResultSet find(Connection c, String u) throws SQLException { PreparedStatement s = c.prepareStatement("SELECT * FROM users WHERE name=?"); s.setString(1, u); return s.executeQuery(); }
  public static void main(String[] a) { System.out.println("u"); }
}
J
for n in jdes jdiv jovf jobo jcmd jpath jsql; do cp ${n}_a.jar "$OUT/vcls_${n}_a.bin"; cp ${n}_b.jar "$OUT/vcls_${n}_b.bin"; done
# decoys: a renamed text impostor next to a real jar, and byte-identical ELF twins (nothing fixed)
printf 'PK\x03\x04 renamed notes, not a jar\n' > "$OUT/vcls_decoy_text_a.bin"; cp jdiv_b.jar "$OUT/vcls_decoy_text_b.bin"
cp "$OUT/vcls_divzero_a.bin" "$OUT/vcls_decoy_same_a.bin"; cp "$OUT/vcls_divzero_a.bin" "$OUT/vcls_decoy_same_b.bin"
cd /; rm -rf -- "$W"
