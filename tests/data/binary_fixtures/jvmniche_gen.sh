#!/bin/bash
# Build the jvmniche_* fixtures: hand-built classfiles with each niche JVM compiler's shape (no jython/jrubyc/ceylon/
# kotlinc installed) -- javac 21 against STUB runtime classes (stubs are NOT packed, like the GM's unbundled jars),
# then `jar`. SourceFile is renamed to the real unit (hello.py / beacon.rb / run.ceylon / hello.main.kts) by a stdlib
# CONSTANT_Utf8 rewrite (javac always writes X.java). HCFG blob: coreutils `base64 -w0`, never lib.
# usage: bash jvmniche_gen.sh
set -e
here=$(cd "$(dirname "$0")" && pwd)
w=$(mktemp -d); cd "$w"; mkdir -p stub/out
json='{"c2":"https://niche.example/gate","id":"day27-niche"}'
blob=$(python3 -c '
import sys, zlib, struct
j = sys.argv[1].encode(); k = 0x3c
print((b"HCFG" + bytes([1, k]) + struct.pack("<H", len(j)) + struct.pack("<I", zlib.crc32(j)) + bytes(c ^ k for c in j)).hex())' "$json" | xxd -r -p | base64 -w0)
rensrc() {  # rensrc <class> <old SourceFile> <new SourceFile>: rewrite the CONSTANT_Utf8 (u1 tag, u2 len, bytes)
python3 - "$@" <<'P'
import sys, struct
f, a, b = sys.argv[1], sys.argv[2].encode(), sys.argv[3].encode()
d = open(f, "rb").read()
old = b"\x01" + struct.pack(">H", len(a)) + a
assert d.count(old) == 1, (f, a)
open(f, "wb").write(d.replace(old, b"\x01" + struct.pack(">H", len(b)) + b))
P
}
# --- runtime stubs (compile-time only) ---
mkdir -p stub/src && cd stub/src
cat > Stubs.java <<'J'
J
mk() { mkdir -p "$(dirname "$1")"; printf '%s\n' "$2" > "$1.java"; }
mk org/python/core/PyObject 'package org.python.core; public class PyObject {}'
mk org/python/core/PyString 'package org.python.core; public class PyString extends PyObject { public static PyString fromInterned(String s) { return null; } }'
mk org/python/core/PyCode 'package org.python.core; public class PyCode {}'
mk org/python/core/PyFrame 'package org.python.core; public class PyFrame {}'
mk org/python/core/ThreadState 'package org.python.core; public class ThreadState {}'
mk org/python/core/PyRunnable 'package org.python.core; public interface PyRunnable { PyCode getMain(); }'
mk org/python/core/PyFunctionTable 'package org.python.core; public abstract class PyFunctionTable { public abstract PyObject call_function(int i, PyFrame f, ThreadState t); }'
mk org/jruby/runtime/ThreadContext 'package org.jruby.runtime; public class ThreadContext {}'
mk org/jruby/runtime/builtin/IRubyObject 'package org.jruby.runtime.builtin; public interface IRubyObject {}'
mk org/jruby/ast/executable/AbstractScript 'package org.jruby.ast.executable; public abstract class AbstractScript {}'
mk org/jruby/RubyString 'package org.jruby; public class RubyString implements org.jruby.runtime.builtin.IRubyObject { public static RubyString newString(Object r, String s) { return null; } }'
mk com/redhat/ceylon/compiler/java/metadata/Ceylon 'package com.redhat.ceylon.compiler.java.metadata; @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME) public @interface Ceylon { int major(); }'
mk com/redhat/ceylon/compiler/java/metadata/Module 'package com.redhat.ceylon.compiler.java.metadata; @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME) public @interface Module { String name(); String version(); }'
mk ceylon/language/print_ 'package ceylon.language; public final class print_ { public static void print(Object o) {} }'
mk kotlin/Metadata 'package kotlin; @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME) public @interface Metadata { int k(); int[] mv(); }'
mk kotlin/script/templates/standard/ScriptTemplateWithArgs 'package kotlin.script.templates.standard; public abstract class ScriptTemplateWithArgs { public ScriptTemplateWithArgs(String[] a) {} }'
mk org/eclipse/xtext/xbase/lib/InputOutput 'package org.eclipse.xtext.xbase.lib; public class InputOutput { public static <T> T println(T o) { return o; } }'
mk org/eclipse/xtext/xbase/lib/Pure 'package org.eclipse.xtext.xbase.lib; public @interface Pure {}'
rm Stubs.java
javac --release 17 -d ../out $(find . -name '*.java')
cd "$w"; S=$w/stub/out
# 1) Jython: hello.py -> hello$py extends PyFunctionTable implements PyRunnable; code objects f$0 greet$1 beacon$2
mkdir -p jy/out
cat > 'jy/hello$py.java' <<J
import org.python.core.*;
public class hello\$py extends PyFunctionTable implements PyRunnable {
    static final PyCode f\$0 = null, greet\$1 = null, beacon\$2 = null;
    static final PyObject _1 = PyString.fromInterned("$blob"), _2 = PyString.fromInterned("hello");
    public PyObject f\$0(PyFrame f, ThreadState t) { return _2; }
    public PyObject greet\$1(PyFrame f, ThreadState t) { return _2; }
    public PyObject beacon\$2(PyFrame f, ThreadState t) { return _1; }
    public PyCode getMain() { return f\$0; }
    public static void main(String[] a) {}
    public PyObject call_function(int i, PyFrame f, ThreadState t) { switch (i) { case 0: return f\$0(f, t); case 1: return greet\$1(f, t); default: return beacon\$2(f, t); } }
}
J
javac --release 17 -cp "$S" -d jy/out 'jy/hello$py.java'
rensrc 'jy/out/hello$py.class' 'hello$py.java' hello.py
printf 'Main-Class: hello$py\nCreated-By: jython 2.7.3\n' > jy/m.txt
(cd jy/out && jar --create --file "$w/jy.jar" --manifest "$w/jy/m.txt" .); cp jy.jar "$here/jvmniche_jython_jar.bin"
# 2) JRuby AOT: beacon.rb -> beacon extends AbstractScript, RUBY$script + RUBY$method$<name>$N; HCFG in beacon$Cfg
mkdir -p jr/out
cat > jr/beacon.java <<J
import org.jruby.ast.executable.AbstractScript; import org.jruby.runtime.ThreadContext; import org.jruby.runtime.builtin.IRubyObject;
public class beacon extends AbstractScript {
    public IRubyObject RUBY\$script(ThreadContext c, IRubyObject self) { return RUBY\$method\$connect\$0(c, self); }
    public static IRubyObject RUBY\$method\$connect\$0(ThreadContext c, IRubyObject self) { return beacon\$Cfg.load(); }
    public static IRubyObject RUBY\$method\$decode\$1(ThreadContext c, IRubyObject self) { return self; }
    public static void main(String[] a) {}
}
class beacon\$Cfg { static IRubyObject load() { return org.jruby.RubyString.newString(null, "$blob"); } }
J
javac --release 17 -cp "$S" -d jr/out jr/beacon.java
rensrc jr/out/beacon.class beacon.java beacon.rb; rensrc 'jr/out/beacon$Cfg.class' beacon.java beacon.rb
printf 'Main-Class: beacon\nCreated-By: jrubyc 9.4\n' > jr/m.txt
(cd jr/out && jar --create --file "$w/jr.jar" --manifest "$w/jr/m.txt" .); cp jr.jar "$here/jvmniche_jruby_jar.bin"
# 3) Ceylon: module acme.relay -> acme/relay/$module_ (@Module) + toplevel run() -> acme/relay/run_ (@Ceylon), HCFG in run_
mkdir -p cy/out cy/acme/relay
cat > 'cy/acme/relay/$module_.java' <<'J'
package acme.relay;
@com.redhat.ceylon.compiler.java.metadata.Module(name = "acme.relay", version = "1.0.0") final class $module_ {}
J
cat > cy/acme/relay/run_.java <<J
package acme.relay;
@com.redhat.ceylon.compiler.java.metadata.Ceylon(major = 8) public final class run_ {
    private run_() {}
    static final String cfg = "$blob";
    public static void run() { ceylon.language.print_.print(cfg); }
    public static void main(String[] a) { run(); }
}
J
javac --release 17 -cp "$S" -d cy/out 'cy/acme/relay/$module_.java' cy/acme/relay/run_.java
rensrc cy/out/acme/relay/run_.class run_.java run.ceylon; rensrc 'cy/out/acme/relay/$module_.class' '$module_.java' module.ceylon
printf 'Main-Class: acme.relay.run_\n' > cy/m.txt
(cd cy/out && jar --create --file "$w/cy.jar" --manifest "$w/cy/m.txt" acme); cp cy.jar "$here/jvmniche_ceylon_jar.bin"
# 4) Kotlin script, BARE class: hello.main.kts -> Hello_main extends ScriptTemplateWithArgs + @kotlin.Metadata
mkdir -p ks/out
cat > ks/Hello_main.java <<J
@kotlin.Metadata(k = 1, mv = {1, 9, 0}) public class Hello_main extends kotlin.script.templates.standard.ScriptTemplateWithArgs {
    static final String cfg = "$blob";
    public Hello_main(String[] a) { super(a); System.out.println(cfg); }
}
J
javac --release 17 -cp "$S" -d ks/out ks/Hello_main.java
rensrc ks/out/Hello_main.class Hello_main.java hello.main.kts; cp ks/out/Hello_main.class "$here/jvmniche_kts_class.bin"
# 5) Xtend: plain Java output (SourceFile Greeter.java) + org/eclipse/xtext/xbase/lib refs; HCFG in a 2nd class acme/Keys
mkdir -p xt/out xt/acme
cat > xt/acme/Greeter.java <<'J'
package acme;
import org.eclipse.xtext.xbase.lib.InputOutput;
public class Greeter { @org.eclipse.xtext.xbase.lib.Pure public String greet() { return InputOutput.<String>println("hi " + Keys.K.length()); }
    public static void main(String[] a) { new Greeter().greet(); } }
J
printf 'package acme;\nfinal class Keys { static final String K = new String("%s"); }\n' "$blob" > xt/acme/Keys.java
javac --release 17 -cp "$S" -d xt/out xt/acme/Greeter.java xt/acme/Keys.java
printf 'Main-Class: acme.Greeter\n' > xt/m.txt
(cd xt/out && jar --create --file "$w/xt.jar" --manifest "$w/xt/m.txt" acme); cp xt.jar "$here/jvmniche_xtend_jar.bin"
# 6) DECOY: plain javac jar, class NAMED hello$py + RUBY-ish method-free, runtime paths only as STRING LITERALS, + HCFG
mkdir -p dc/out
cat > 'dc/hello$py.java' <<J
public class hello\$py { static final String A = "org/python/core/PyFunctionTable", B = "org/jruby/Ruby", C = "$blob";
    public static void main(String[] a) { System.out.println(A + B + C); } }
J
javac --release 17 -d dc/out 'dc/hello$py.java'
printf 'Main-Class: hello$py\n' > dc/m.txt
(cd dc/out && jar --create --file "$w/dc.jar" --manifest "$w/dc/m.txt" .); cp dc.jar "$here/jvmniche_decoy_literals_jar.bin"
# 7) DECOY: truncated jar (first 200 bytes of the Jython jar)
head -c 200 jy.jar > "$here/jvmniche_decoy_trunc.bin"
rm -rf "$w"
