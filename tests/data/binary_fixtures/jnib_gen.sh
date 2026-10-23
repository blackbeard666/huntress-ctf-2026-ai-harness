#!/usr/bin/env bash
# Generator for the jnib_*.{jar,bin} fixtures (lib.binary.jni_bridge_facts). Independent writers: javac/jar (native
# methods + loadLibrary), javac -h (JNI export mangling), gcc / aarch64-linux-gnu-gcc -shared -I$JAVA_HOME/include.
# usage: jnib_gen.sh <workdir>   (writes the fixtures next to this script)
set -euo pipefail
OUT=$(cd "$(dirname "$0")" && pwd); W=${1:?workdir}; mkdir -p "$W"; cd "$W"
# HCFG blob (same layout as bytecode_gen.sh): 'HCFG' ver=1 key len u16le crc32 (gzip trailer) + JSON, base64 (coreutils).
hcfg() { local P=$1 LEN; LEN=$(printf '%s' "$P" | wc -c)
  { printf 'HCFG\x01\x00'; perl -e 'print pack("v", $ARGV[0])' "$LEN"; printf '%s' "$P" | gzip -c | tail -c8 | head -c4
    printf '%s' "$P"; } | base64 -w0; }
CFG_J=$(hcfg '{"c2":"203.0.113.7:443","flag":"flag{jni_jar_side}"}')
CFG_S=$(hcfg '{"c2":"198.51.100.4:8443","flag":"flag{jni_so_side}"}')
JH=$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")"); INC="-I$JH/include -I$JH/include/linux"

# 1. static-export pair: javac -h emits Java_<mangled> names (pkg underscore -> _1, overload -> __<sig>).
mkdir -p s/org/hctf/native_x && cat > s/org/hctf/native_x/Gate.java <<'EOF'
package org.hctf.native_x;
public class Gate {
    static { System.loadLibrary("gatekeeper"); }
    public native String open(String key);
    public static native int check(int[] a);
    public static native int check(String s);
    private native byte[] xor_key(byte[] in, int k);
    public static final String CFG = "CFG_J_HERE";
    public int plain() { return CFG.length(); }
}
EOF
sed -i "s|CFG_J_HERE|$CFG_J|" s/org/hctf/native_x/Gate.java
(cd s && javac -h . -d cls org/hctf/native_x/Gate.java && jar cf "$OUT/jnib_static.jar" -C cls .)
{ echo '#include "org_hctf_native_x_Gate.h"'
  grep -o 'Java_[A-Za-z0-9_]*' s/org_hctf_native_x_Gate.h | sort -u | sed 's/.*/void *&(void *e, void *o) { (void)e; return o; }/'
  echo 'const char *gate_tag(void) { return "gate"; }'; } | sed 's/#include.*//' > s/gate.c
gcc -shared -fPIC -O1 -Wl,-soname,libgatekeeper.so -o "$OUT/jnib_static.bin" s/gate.c

# 2. RegisterNatives pair: JNI_OnLoad + FindClass + RegisterNatives over a static JNINativeMethod table.
mkdir -p r/com/acme && cat > r/com/acme/Licensor.java <<'EOF'
package com.acme;
public final class Licensor {
    static { Runtime.getRuntime().loadLibrary("licz"); }
    public static native boolean verify(String serial, long seed);
    native int[] table();
    public native void reset();
}
EOF
(cd r && javac -d cls com/acme/Licensor.java && jar cf "$OUT/jnib_register.jar" -C cls .)
cat > r/licz.c <<'EOF'
#include <jni.h>
static jboolean lic_verify(JNIEnv *e, jclass c, jstring s, jlong seed) { (void)e; (void)c; (void)s; return seed == 0x4843; }
static jintArray lic_table(JNIEnv *e, jobject o) { (void)o; return (*e)->NewIntArray(e, 4); }
static void lic_reset(JNIEnv *e, jobject o) { (void)e; (void)o; }
const char lic_cfg[] = "CFG_S_HERE";
static const JNINativeMethod methods[] = {
    {"verify", "(Ljava/lang/String;J)Z", (void *)lic_verify},
    {"table", "()[I", (void *)lic_table},
    {"reset", "()V", (void *)lic_reset},
};
JNIEXPORT jint JNI_OnLoad(JavaVM *vm, void *r) {
    JNIEnv *env; (void)r;
    if ((*vm)->GetEnv(vm, (void **)&env, JNI_VERSION_1_6) != JNI_OK) return -1;
    jclass c = (*env)->FindClass(env, "com/acme/Licensor");
    if (!c || (*env)->RegisterNatives(env, c, methods, 3) < 0) return -1;
    return JNI_VERSION_1_6;
}
EOF
sed -i "s|CFG_S_HERE|$CFG_S|" r/licz.c
gcc -shared -fPIC -O1 $INC -o "$OUT/jnib_register.bin" r/licz.c
# 3. same RegisterNatives lib for aarch64 (R_AARCH64_RELATIVE relocs), stripped of .symtab.
aarch64-linux-gnu-gcc -shared -fPIC -O1 $INC -s -o "$OUT/jnib_register_a64.bin" r/licz.c

# 4. decoy: a jar with no native methods/loadLibrary + a plain C .so with no JNI surface.
mkdir -p d && cat > d/Plain.java <<'EOF'
public class Plain { public static String loadLibrary(String s) { return s + "x"; } public int go() { return 1; } }
EOF
(cd d && javac -d cls Plain.java && jar cf "$OUT/jnib_decoy_nojni.jar" -C cls .)
echo 'int add(int a, int b) { return a + b; } const char *s = "(Ljava/lang/String;)V";' > d/plain.c
gcc -shared -fPIC -O1 -o "$OUT/jnib_decoy_nojni.bin" d/plain.c
# 5. decoy: neither member is a jar/class or ELF/PE (renamed text).
printf 'PK? not a jar\nJava_com_x_Y_z\n' > "$OUT/jnib_decoy_text.jar"; cp "$OUT/jnib_decoy_text.jar" "$OUT/jnib_decoy_text.bin"
