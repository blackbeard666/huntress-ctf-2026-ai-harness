#!/usr/bin/env bash
# Clojure AOT namespace fixtures (lib.binary.clojure_facts): real clojure.core/compile (Clojure 1.12.0, OpenJDK 21)
# + `jar --create` WITHOUT clojure.jar; the cached D25 sample jar; a plain javac jar decoy.
# usage (repo root): bash tests/data/binary_fixtures/cljns_gen.sh
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../../.." && pwd)
J=$root/tools/jvmlangs/x/usr/share/java
CP=$J/clojure-1.12.0.jar:$J/spec.alpha.jar:$J/core.specs.alpha.jar
w=$(mktemp -d); trap 'rm -rf "$w"' EXIT
mkdir -p "$w/src/acme" "$w/classes" "$w/java"
cat > "$w/src/acme/tool_kit.clj" <<'CLJ'
(ns acme.tool-kit
  (:gen-class))

(def blob-key "SENGRwEAAAB0ZXN0LWNvbmZpZw==")

(defn valid?
  "true when the frame is non-empty"
  [frame]
  (pos? (count frame)))

(defn parse->map
  ([s] (parse->map s ","))
  ([s sep] {:parts (clojure.string/split s (re-pattern sep))}))

(def ^:private counter (atom 0))

(defn -main [& args]
  (println (valid? args) (parse->map "a,b") blob-key ((fn [x] (inc x)) 1)))
CLJ
(cd "$w" && java -cp "$CP:src" -Dclojure.compile.path=classes clojure.main -e "(compile 'acme.tool-kit)" >/dev/null)
printf 'Main-Class: acme.tool_kit\n' > "$w/m.txt"
(cd "$w/classes" && jar --create --file "$w/aot.jar" --manifest "$w/m.txt" acme)
cp "$w/aot.jar" "$here/cljns_aot_toolkit.bin"
cp "$root/challenges/day25/binary-out-of-bounds/single_solve/work/extracted/evidence/d25--sample-vulnerable.jar" \
   "$here/cljns_d25_vulnerable.bin"
cat > "$w/java/Plain__init.java" <<'JAVA'
public class Plain__init { public static void main(String[] a) { System.out.println("clojure/lang/RT"); } }
JAVA
(cd "$w/java" && javac --release 17 Plain__init.java && printf 'Main-Class: Plain__init\n' > m.txt \
   && jar --create --file "$w/decoy.jar" --manifest m.txt Plain__init.class)
cp "$w/decoy.jar" "$here/cljns_decoy_java_init.bin"
