#!/bin/bash
# javac twin builds -> jars (JDK `jar`) for lib.binary.jvm_trigger_proof; usage: bash vtp_gen.sh OUTDIR
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
mk() {  # name class < java source
  mkdir -p $1; cat > $1/$2.java; javac --release 11 -g:none -d $1/out $1/$2.java
  (cd $1/out && printf 'Main-Class: %s\n' "$2" > m.txt && jar cfm "$OUT/$1.bin" m.txt *.class)
}
mk vtp_npe_optional_a HeadVulnerable <<'J'
public class HeadVulnerable {
  public static int head(String s) { return s.length() > 0 ? s.charAt(0) : -1; }
  public static void main(String[] a) { System.out.println(head(a.length > 0 ? a[0] : "x")); }
}
J
mk vtp_npe_optional_b HeadCorrected <<'J'
import java.util.Optional;
public class HeadCorrected {
  public static int head(String s) { return Optional.ofNullable(s).filter(x -> !x.isEmpty()).map(x -> (int) x.charAt(0)).orElse(-1); }
  public static void main(String[] a) { System.out.println(head(a.length > 0 ? a[0] : "x")); }
}
J
mk vtp_sioobe_a FourthVulnerable <<'J'
public class FourthVulnerable {
  public static int fourth(String s) { if (s == null) return -1; return s.charAt(s.length() > 3 ? 3 : 0); }
  public static void main(String[] a) { System.out.println(fourth("abcd")); }
}
J
mk vtp_sioobe_b FourthCorrected <<'J'
public class FourthCorrected {
  public static int fourth(String s) { if (s == null || s.isEmpty()) return -1; return s.charAt(s.length() > 3 ? 3 : 0); }
  public static void main(String[] a) { System.out.println(fourth("abcd")); }
}
J
mk vtp_aioobe_a TableVulnerable <<'J'
public class TableVulnerable {
  static final int[] TABLE = {10, 20, 30, 40};
  public static int lookup(int i) { if (i < 0 || i > TABLE.length) return -1; return TABLE[i]; }
  public static void main(String[] a) { System.out.println(lookup(a.length)); }
}
J
mk vtp_aioobe_b TableCorrected <<'J'
public class TableCorrected {
  static final int[] TABLE = {10, 20, 30, 40};
  public static int lookup(int i) { if (i < 0 || i >= TABLE.length) return -1; return TABLE[i]; }
  public static void main(String[] a) { System.out.println(lookup(a.length)); }
}
J
mk vtp_nfe_trycatch_a PortUnpatched <<'J'
public class PortUnpatched {
  public int port(String s) { return Integer.parseInt(s.trim()) + 1; }
  public static void main(String[] a) { System.out.println(new PortUnpatched().port("80")); }
}
J
mk vtp_nfe_trycatch_b PortPatched <<'J'
public class PortPatched {
  public int port(String s) { try { return Integer.parseInt(s.trim()) + 1; } catch (RuntimeException e) { return -1; } }
  public static void main(String[] a) { System.out.println(new PortPatched().port("80")); }
}
J
mk vtp_decoy_same_a SameVulnerable <<'J'
public class SameVulnerable {
  public static int head(String s) { return s == null || s.isEmpty() ? -1 : s.charAt(0); }
  public static void main(String[] a) { System.out.println(head("q") + " v"); }
}
J
mk vtp_decoy_same_b SameCorrected <<'J'
public class SameCorrected {
  public static int head(String s) { return s == null || s.isEmpty() ? -1 : s.charAt(0); }
  public static void main(String[] a) { System.out.println(head("q") + " c"); }
}
J
# decoy: a zip renamed .jar with no classfile + a gzip'd class impostor
printf 'Manifest-Version: 1.0\n' > MANIFEST.MF; zip -q -X "$OUT/vtp_decoy_noclass_a.bin" MANIFEST.MF
cp "$OUT/vtp_decoy_noclass_a.bin" "$OUT/vtp_decoy_noclass_b.bin"
