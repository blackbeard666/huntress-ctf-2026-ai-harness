"""Generator for the jvm2_* fixtures (target jvm-dsl-script-route): synthetic, inert v=3 descriptor hosts in the next
JVM/build syntaxes -- Kotlin .kts (`const val`, `${}` templates, `mapOf(.. to ..)`), Gradle (build.gradle `ext.`,
build.gradle.kts `tasks.register { doLast { exec { commandLine } } }`), Java (`static final String` + `\\uXXXX`
escapes processed before lexing, text blocks), JSP (`<%-- --%>` / `<%! %>`), Scala (`s".."`, triple-quoted `|..`.stripMargin),
Clojure (`(def descriptor-<id> (str ..))`, `#_` discard, `;;` marker) and BeanShell -- each marker-less (descriptor
only) unless named *_marker, plus decoys (benign / discarded descriptor). Stdlib writer only; every `expected_plain`
is proven by the independent oracle_cmd (jshell/java for Java+BeanShell, perl/sed/base64/xxd for the rest).

    python3 -I tests/data/script_fixtures/jvm2_gen.py
"""
import base64
import hashlib
import json
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = "tests/data/script_fixtures/"
GEN = f"python3 -I {REL}jvm2_gen.py"


def plan_for(name, lang):
    h = hashlib.sha256(name.encode()).hexdigest()
    return h[:8], "|".join([
        "v=3", f"language={lang}", "role=stager", "verdict=malicious", "attack=T1059", "adapter=build_exec",
        "host_profile=standalone", "obfuscation_profile=b64", "stage_profile=two_stage_download_execute",
        "next_language=bash", "stage_count=2", "steps=fetch_stage,run_stage", f"campaign_id=JVM-{h[8:16]}",
        f"url=https://jvm-{h[8:18]}.example.invalid/stage", f"file_path=/tmp/huntress-jvm/.{h[16:32]}.stage"])


def b64(p):
    return base64.b64encode(p.encode()).decode()


def wrap(s, n=64):
    return textwrap.wrap(s, n, break_on_hyphens=False)


def jesc(s, every=7):
    """Java/Kotlin-style \\uXXXX for every `every`-th char (javac translates these before lexing)."""
    return "".join("\\u%04x" % ord(c) if i % every == 3 else c for i, c in enumerate(s))


BENIGN = b64("build cache warmup for the nightly inventory; nothing to execute")
T = " | tr -d ' \\n\\r|' | base64 -d"


def cases():
    out = []

    def add(name, ext, lang, render, oracle, decoy=False, enc="b64"):
        ident, plan = plan_for(name, lang)
        mat = BENIGN if decoy else (b64(plan) if enc == "b64" else plan.encode().hex())
        out.append((name, ext, render(ident, mat), None if decoy else plan, oracle(REL + name + ext, ident), decoy))

    # --- Kotlin script ---------------------------------------------------------------------------------------------
    add("jvm2_kts_constval", ".kts", "kotlin_script", lambda i, m: "\n".join([
        "// settings helper", "object Cfg {", f'    const val DESCRIPTOR_{i.upper()} = "{m}"', "}", "",
        f"println(Cfg.DESCRIPTOR_{i.upper()}.length)", ""]),
        lambda p, i: f"sed -n 's/.*const val DESCRIPTOR_{i.upper()} = \"\\(.*\\)\"$/\\1/p' {p}" + T)
    add("jvm2_kts_template", ".kts", "kotlin_script", lambda i, m: "\n".join([
        f'val p0 = "{m[:40]}"', f'val p1 = "{m[40:100]}"', f'val p2 = "{m[100:]}"',
        f'val descriptor_{i} = "${{p0}}$p1${{p2}}"', f"println(descriptor_{i}.length)", ""]),
        lambda p, i: f"perl -ne 'print $1 if /^val p\\d = \"(.*)\"$/' {p}" + T)
    add("jvm2_kts_mapof", ".kts", "kotlin_script", lambda i, m: "\n".join([
        "val cfg = mapOf(", '    "name" to "inventory",', f'    "descriptor_{i}" to "{m[:70]}" +',
        f'        "{m[70:]}",', '    "retries" to "3"', ")", f'println(cfg["descriptor_{i}"]!!.length)', ""]),
        lambda p, i: f"perl -0ne 'print \"$1$2\" if /\"descriptor_{i}\" to \"(.*?)\" \\+\\s+\"(.*?)\"/s' {p}" + T)
    add("jvm2_kts_rawtrim", ".kts", "kotlin_script", lambda i, m: "\n".join(
        [f'val descriptor_{i} = """'] + ["    " + x for x in wrap(m)] + ['""".trimIndent().replace("\\n", "")',
                                                                         f"println(descriptor_{i}.length)", ""]),
        lambda p, i: f"sed -n '/= \"\"\"$/,/^\"\"\"/p' {p} | grep -v '\"\"\"'" + T)
    # --- Gradle ----------------------------------------------------------------------------------------------------
    add("jvm2_gradle_kts_exec", ".gradle.kts", "gradle_kotlin", lambda i, m: "\n".join([
        "plugins { java }", "", f'val descriptor_{i} = "{m}"', "",
        'tasks.register("warmup") {', "    doLast {", "        exec {",
        f'            commandLine("sh", "-c", "echo ${{descriptor_{i}}} | base64 -d >/dev/null")',
        "        }", "    }", "}", ""]),
        lambda p, i: f"sed -n 's/^val descriptor_{i} = \"\\(.*\\)\"$/\\1/p' {p}" + T)
    add("jvm2_gradle_ext", ".gradle", "gradle_groovy", lambda i, m: "\n".join([
        "apply plugin: 'java'", "", f"ext.descriptor_{i} = '{m[:80]}' +", f"    '{m[80:]}'", "",
        "task warmup {", "    doLast {", f"        exec {{ commandLine 'sh', '-c', \"echo ${{descriptor_{i}.size()}}\" }}",
        "    }", "}", ""]),
        lambda p, i: f"perl -0ne \"print \\$1.\\$2 if /ext\\.descriptor_{i} = '(.*?)' \\+\\s+'(.*?)'/s\" {p}" + T)
    add("jvm2_gradle_extblock", ".gradle", "gradle_groovy", lambda i, m: "\n".join([
        "ext {", "    retries = 3", f'    descriptor_{i} = """{m}"""', "}", "",
        "tasks.register('warmup') { doLast { println descriptor_" + i + ".length() } }", ""]),
        lambda p, i: f"perl -ne 'print $1 if /descriptor_{i} = \"\"\"(.*)\"\"\"/' {p}" + T)
    # --- Java / JSP / BeanShell ------------------------------------------------------------------------------------
    add("jvm2_java_uescape", ".java", "java", lambda i, m: "\n".join([
        "public class Warmup {", f'    static final String DESCRIPTOR_{i.upper()} = "{jesc(m[:90])}"',
        f'        + "{jesc(m[90:])}";', "    public static void main(String[] a) {",
        f"        System.out.print(DESCRIPTOR_{i.upper()});", "    }", "}", ""]),
        lambda p, i: f"cp {p} $TMPDIR/Warmup.java && java $TMPDIR/Warmup.java" + T)
    add("jvm2_java_textblock", ".java", "java", lambda i, m: "\n".join(
        ["public class Warmup {", f'    private static final String descriptor_{i} = """'] +
        ["        " + x for x in wrap(m)] + ['        """;', "    public static void main(String[] a) {",
                                             f"        System.out.print(descriptor_{i});", "    }", "}", ""]),
        lambda p, i: f"cp {p} $TMPDIR/Warmup.java && java $TMPDIR/Warmup.java" + T)
    add("jvm2_jsp_decl", ".jsp", "jsp", lambda i, m: "\n".join([
        '<%@ page contentType="text/html" %>', "<%-- inventory page --%>",
        f'<%! private static final String descriptor_{i} = "{m[:64]}"', f'      + "{m[64:]}"; %>',
        f"<html><body><%= descriptor_{i}.length() %></body></html>", ""]),
        lambda p, i: f"perl -0ne 'print \"$1$2\" if /descriptor_{i} = \"(.*?)\"\\s+\\+ \"(.*?)\"/s' {p}" + T)
    add("jvm2_bsh_string", ".bsh", "beanshell", lambda i, m: "\n".join([
        "import java.util.*;", f'String descriptor_{i} = "{m[:50]}"', f'    + "{m[50:]}";',
        f"print(descriptor_{i}.length());", ""]),
        lambda p, i: f"(echo 'class B {{ public static void main(String[] a) {{'; sed '/^import/d; s/^print(.*$//' {p}; "
                     f"echo 'System.out.print(descriptor_{i}); }} }}') > $TMPDIR/B.java && java $TMPDIR/B.java" + T)
    # --- Scala -----------------------------------------------------------------------------------------------------
    add("jvm2_scala_strip", ".sc", "scala", lambda i, m: "\n".join(
        [f'val descriptor_{i} = """' + "|" + wrap(m)[0]] + ["  |" + x for x in wrap(m)[1:]] +
        ['  |""".stripMargin.replace("\\n", "")', f"println(descriptor_{i}.length)", ""]),
        lambda p, i: f"perl -0ne 'print $1 if /\"\"\"(.*?)\"\"\"/s' {p} | sed 's/^ *|//'" + T)
    add("jvm2_scala_interp", ".sc", "scala", lambda i, m: "\n".join([
        f'val head = "{m[:60]}"', f'val descriptor_{i} = s"${{head}}{m[60:]}"', f"println(descriptor_{i}.length)", ""]),
        lambda p, i: f"perl -ne 'print $1 if /^val head = \"(.*)\"$/; print $1 if /s\"\\$\\{{head\\}}(.*)\"$/' {p}" + T)
    # --- Clojure ---------------------------------------------------------------------------------------------------
    add("jvm2_clj_def", ".clj", "clojure", lambda i, m: "\n".join([
        "(ns inventory.warmup)", ";; build cache warmup", f"#_(def descriptor-{i} \"{BENIGN}\")",
        f"(def ^:private descriptor-{i}", f'  (str "{m[:70]}"', f'       "{m[70:]}"))', "",
        f"(println (count descriptor-{i}))", ""]),
        lambda p, i: f"grep -v '^#_' {p} | perl -0ne 'print \"$1$2\" if /\\(str \"(.*?)\"\\s+\"(.*?)\"/s'" + T)
    add("jvm2_clj_hex", ".clj", "clojure", lambda i, m: "\n".join([
        "(ns inventory.warmup)", f'(def descriptor-{i} "{m}")', f"(println (count descriptor-{i}))", ""]),
        lambda p, i: f"sed -n 's/^(def descriptor-{i} \"\\(.*\\)\")$/\\1/p' {p} | xxd -r -p", enc="hex")
    # --- decoys ----------------------------------------------------------------------------------------------------
    add("jvm2_kts_decoy", ".kts", "kotlin_script", lambda i, m: "\n".join([
        f'const val DESCRIPTOR_{i.upper()} = "{m}"', f"println(DESCRIPTOR_{i.upper()}.length)", ""]),
        lambda p, i: f"sed -n 's/.*DESCRIPTOR_{i.upper()} = \"\\(.*\\)\"$/\\1/p' {p}" + T, decoy=True)
    add("jvm2_clj_decoy_discard", ".clj", "clojure", lambda i, m: "\n".join([
        "(ns inventory.warmup)", f'(def descriptor-{i} "{m}")', f"(println (count descriptor-{i}))", ""]),
        lambda p, i: f"sed -n 's/^(def descriptor-{i} \"\\(.*\\)\")$/\\1/p' {p}" + T, decoy=True)
    add("jvm2_java_decoy", ".java", "java", lambda i, m: "\n".join([
        "public class Warmup {", f'    static final String DESCRIPTOR_{i.upper()} = "{jesc(m)}";',
        "    public static void main(String[] a) {", f"        System.out.print(DESCRIPTOR_{i.upper()});", "    }",
        "}", ""]),
        lambda p, i: f"cp {p} $TMPDIR/Warmup.java && java $TMPDIR/Warmup.java" + T, decoy=True)
    return out


def main():
    for name, ext, src, plan, oracle, decoy in cases():
        (HERE / (name + ext)).write_text(src)
        (HERE / (name + ".json")).write_text(json.dumps({
            "expected_plain": plan, "decoy": decoy, "host": name.split("_")[1],
            "generator_cmd": f"{GEN}  ({'benign base64 descriptor, no plan' if decoy else 'plan -> descriptor'})",
            "oracle_cmd": oracle + ("   # -> benign text, not a v=3 plan" if decoy else "")}, indent=1) + "\n")


if __name__ == "__main__":
    main()
