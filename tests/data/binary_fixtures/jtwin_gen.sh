#!/bin/bash
# Clojure twin jars for the gensym-normalised jvm_patch_diff (REAL Clojure 1.12 AOT, clojure.lang.Compile; JDK jar).
# The B side compiles a padding namespace FIRST in the same JVM, so every fn__N / loading__N__auto____M gensym of the
# twin is shifted although its source is identical -> twins agree on gensym numbers only by accident (as D25 did).
# usage: bash jtwin_gen.sh   (writes jtwin_*.bin next to this script)
set -e
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../../.." && pwd)
J=$root/tools/jvmlangs/x/usr/share/java; CP="$J/clojure-1.12.jar:$J/spec.alpha.jar:$J/core.specs.alpha.jar"
w=$(mktemp -d); cd "$w"
body() {  # ns guard?
  cat <<C
(ns twin.$1 (:gen-class))
(defn checksum [xs] (reduce + (map (fn [x] (bit-and x 255)) xs)))
(defn parse-frame [v] $2)
(defn valid? [s] (and (string? s) (pos? (count s))))
(defn -main [& args] (println (checksum [1 2 3]) (parse-frame [1 2 3 4 5]) (valid? "x")))
C
}
pad='(ns twin.pad) (defn a [] (fn [] 1)) (defn b [] (fn [] 2)) (defn c [] (map (fn [x] x) [1]))'
build() {  # out-jar ns guard pad?
  mkdir -p $1/src/twin $1/out
  body $2 "$3" > $1/src/twin/$2.clj
  nss="twin.$2"
  if [ -n "$4" ]; then echo "$pad" > $1/src/twin/pad.clj; nss="twin.pad twin.$2"; fi
  java -cp "$CP:$1/src" -Dclojure.compile.path=$1/out clojure.lang.Compile $nss >/dev/null
  rm -f $1/out/twin/pad*.class
  (cd $1/out && jar --create --file "$w/$1.jar" twin)
}
build va vulnerable001 '(nth v 4)'
build vc corrected001 '(if (< 4 (count v)) (nth v 4) -1)' pad
build da old002 '(nth v 4)'
build db new002 '(nth v 4)' pad
cp va.jar "$here/jtwin_clj_a.bin"; cp vc.jar "$here/jtwin_clj_b.bin"
cp da.jar "$here/jtwin_decoy_a.bin"; cp db.jar "$here/jtwin_decoy_b.bin"
for j in va vc da db; do unzip -Z1 $j.jar | grep class; done
