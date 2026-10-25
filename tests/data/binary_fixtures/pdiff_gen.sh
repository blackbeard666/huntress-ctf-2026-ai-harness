#!/bin/bash
# javac twin builds -> jars (JDK `jar`); usage: bash pdiff_gen.sh OUTDIR
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
mk() {  # dir class < java source
  mkdir -p $1; cat > $1/$2.java; javac --release 11 -g:none -d $1/out $1/$2.java
  (cd $1/out && printf 'Main-Class: %s\n' "$2" > m.txt && jar cfm ../../$1.jar m.txt *.class)
}
mk bv GateVulnerable <<'J'
public class GateVulnerable {
  static final int[] TABLE = {7, 11, 13, 17};
  public static int pick(int i) { return TABLE[i] * 3; }
  public static String label(String s) { return "L:" + s.trim(); }
  public static void main(String[] a) { System.out.println(pick(a.length) + label("x")); }
}
J
mk bc GateCorrected <<'J'
public class GateCorrected {
  static final int[] TABLE = {7, 11, 13, 17};
  public static int pick(int i) { if (i < 0 || i >= TABLE.length) return -1; return TABLE[i] * 3; }
  public static String label(String s) { return "L:" + s.trim(); }
  public static void main(String[] a) { System.out.println(pick(a.length) + label("x")); }
}
J
mk ev ParserUnpatched <<'J'
public class ParserUnpatched {
  public int port(String s) { return Integer.parseInt(s) + 1; }
  public int twice(int x) { return x * 2; }
  public static void main(String[] a) { System.out.println(new ParserUnpatched().port("80")); }
}
J
mk ec ParserPatched <<'J'
public class ParserPatched {
  public int port(String s) { try { return Integer.parseInt(s) + 1; } catch (NumberFormatException e) { return -1; } }
  public int twice(int x) { return x * 2; }
  public static void main(String[] a) { System.out.println(new ParserPatched().port("80")); }
}
J
cp bv.jar "$OUT/pdiff_bounds_a.bin"; cp bc.jar "$OUT/pdiff_bounds_b.bin"
cp ev.jar "$OUT/pdiff_exc_a.bin"; cp ec.jar "$OUT/pdiff_exc_b.bin"
printf 'PK\x03\x04 not really a jar -- renamed text\n' > "$OUT/pdiff_decoy_a.bin"; cp bc.jar "$OUT/pdiff_decoy_b.bin"
cd /; rm -rf -- "$W"
