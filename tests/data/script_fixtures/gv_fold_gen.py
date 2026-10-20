"""Generator for the gv_fold_* fixtures (target groovy-literal-fold): D20 Groovy / Kotlin plans re-assembled at
runtime in each construct family, no HUNTRESS marker. stdlib only. Oracle (Groovy): real Groovy 4.0.12
(`java21 -cp groovy-4.0.12.jar groovy.ui.GroovyMain`) printing the descriptor; (Kotlin): python3 stdlib inverse."""
import base64, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
D20 = ("v=3|language=groovy|role=staged_chain|verdict=suspicious|attack=T1059|adapter=operation_graph|"
       "host_profile=standalone|obfuscation_profile=fragmented_hex|stage_profile=cross_language_handoff|"
       "next_language=vbscript|stage_count=3|steps=profile_host,decode_configuration,dispatch_language|"
       "campaign_id=GROOVY-6ffc2963|url=https://groovy-6ffc296364.example.invalid/stage|"
       "file_path=/tmp/huntress-groovy/.6ffc29636451e5a.stage")
JNK = ("v=3|language=groovy_jenkinsfile|role=stager|verdict=malicious|attack=T1059|adapter=pipeline_sh|"
       "host_profile=standalone|obfuscation_profile=hex|stage_profile=two_stage_download_execute|next_language=bash|"
       "stage_count=3|steps=checkout,fetch_stage,run_stage|campaign_id=GRO-601688e4|"
       "url=https://groovy-601688e49a.example.invalid/stage|file_path=/tmp/huntress-groovy/.9a2d85425c432971.stage")
KTS = ("v=3|language=kotlin_script|role=collector|verdict=malicious|attack=T1005|adapter=file_walk|"
       "host_profile=standalone|obfuscation_profile=b64|stage_profile=two_stage_download_execute|next_language=python|"
       "stage_count=2|steps=enumerate_files,stage_archive|campaign_id=KTS-45924496|"
       "url=https://kts-4592449603.example.invalid/stage|file_path=/tmp/huntress-kts/.033552827e67b273.stage")
ROT13 = str.maketrans("abcdefghijklmnopqrstuvwxyz", "nopqrstuvwxyzabcdefghijklm")


def parts(s, n):
    k = -(-len(s) // n)
    return [s[i:i + k] for i in range(0, len(s), k)]


def gq(s):          # Groovy single-quoted literal
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def kq(s):          # Kotlin / Groovy double-quoted literal ($ escaped)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$") + '"'


def gen():
    out = {}
    # 1. GString over locals + '..' + '..' + slashy + dollar-slashy (plain plan)
    a, b, c, d, e = parts(D20, 5)
    out["gv_fold_gstring_slashy.groovy"] = (D20, "\n".join([
        "// staged chain helper", f"def p1 = {gq(a)}", f"final String p2 = {gq(b)}",
        f"def p3 = /{c}/", f"def p4 = $/{d}/$",
        f"def descriptor_6ffc2963 = \"${{p1}}${{p2}}\" + p3 +", f"    \"$p4\" + {gq(e[:20])} + {gq(e[20:])}",
        "def buildPlan_6ffc2963 = { -> [descriptor: descriptor_6ffc2963].asImmutable() }", ""]))
    # 2. decodeBase64 / Base64.getDecoder / decodeHex / as byte[] (b64 material folds to the plan)
    a, b, c, d = parts(JNK, 4)
    out["gv_fold_b64_hex_bytes.groovy"] = (JNK, "\n".join([
        "import java.util.Base64", "import java.nio.charset.StandardCharsets",
        f"def x1 = new String({gq(base64.b64encode(a.encode()).decode())}.decodeBase64())",
        f"def x2 = new String(Base64.getDecoder().decode({kq(base64.b64encode(b.encode()).decode())}), StandardCharsets.UTF_8)",
        f"def x3 = new String({gq(c.encode().hex())}.decodeHex(), 'UTF-8')",
        f"def x4 = new String({list(d.encode())} as byte[])",
        "def descriptor_601688e4 = [x1, x2, x3, x4].join('')",
        "pipeline { agent any; stages { stage('noop') { steps { echo \"${descriptor_601688e4.length()}\" } } } }", ""]))
    # 3. char codes: collect { it as char }.join(), (char) 0x76, as char[], String.format, reverse, tr (rot13)
    a, b, c, d = parts(D20, 4)
    out["gv_fold_chars_tr.groovy"] = (D20, "\n".join([
        f"def c1 = {[ord(ch) for ch in a]}.collect {{ it as char }}.join()",
        f"def c2 = String.format('%c%c%c%c%c%c%s', {', '.join(str(ord(ch)) for ch in b[:6])}, {gq(b[6:])})",
        f"def c3 = new String({[ord(ch) for ch in c]} as char[])",
        f"def c4 = {gq(d[::-1].translate(ROT13))}.reverse().tr('a-z', 'n-za-m')",
        f"def descriptor_6ffc2963 = c1 + c2 + c3 + c4", ""]))
    # 4. ''' / """ with \ continuations, stripIndent, (char) casts, StringBuilder <<
    a, b, c = parts(JNK, 3)
    a1, a2 = a[:40], a[40:]
    out["gv_fold_triple_sb.groovy"] = (JNK, "\n".join([
        f"def t1 = '''{a1}\\\n{a2}'''", f"def t2 = \"\"\"\\\n    {b}\"\"\".stripIndent()",
        "def sb = new StringBuilder()", "sb << t1 << t2", f"sb.append((char) {ord(c[0])}).append({gq(c[1:])})",
        "def descriptor_9a2d8542 = sb.toString()", ""]))
    # decoy: assembled from an unbound env value + truncated base64 -> no plan
    out["gv_fold_decoy_unbound.groovy"] = (None, "\n".join([
        "def host = System.getenv('BUILD_HOST')",
        f"def descriptor_decoy = \"${{host}}\" + new String({gq(base64.b64encode(JNK.encode()).decode()[:40])}.decodeBase64())",
        "def label = ['build', 'test'].join('-').reverse()", ""]))
    # 5. Kotlin: buildString / listOf.joinToString / String(byteArrayOf) / toByteArray().map { xor }
    a, b, c, d = parts(KTS, 4)
    k = 0x2A
    xd = "".join(chr(ord(ch) ^ k) for ch in d)
    out["kt_fold_buildstring_xor.kts"] = (KTS, "\n".join([
        f"val k1 = buildString {{ append({kq(a[:30])}); append({kq(a[30:])}) }}",
        f"val k2 = listOf({', '.join(kq(x) for x in parts(b, 3))}).joinToString(\"\")",
        f"val k3 = String(byteArrayOf({', '.join(str(x) for x in c.encode())}))",
        f"val k4 = {kq(xd)}.toByteArray(Charsets.ISO_8859_1).map {{ (it.toInt() xor 0x{k:02X}).toChar() }}.joinToString(\"\")",
        "val descriptor_45924496: String = \"$k1$k2${k3}\" + k4", "println(descriptor_45924496.length)", ""]))
    out["kt_fold_decoy_benign.kts"] = (None, "\n".join([
        "val greeting = buildString { append(\"hello, \"); append(\"world\") }",
        "val descriptor_none = listOf(\"a\", \"b\", \"c\").joinToString(\"\")", "println(greeting + descriptor_none)", ""]))
    return out


if __name__ == "__main__":
    for name, (plan, text) in gen().items():
        (HERE / name).write_text(text)
        stem = name.rsplit(".", 1)[0]
        groovy = name.endswith(".groovy")
        var = next((ln.split()[1] for ln in text.splitlines() if ln.split()[:1] in (["def"], ["val"]) and "descriptor_" in ln.split()[1]), "")
        var = var.rstrip(":")
        fx = {"expected_plain": plan, "decoy": plan is None, "host": "groovy" if groovy else "kotlin",
              "generator_cmd": "python3 -I tests/data/script_fixtures/gv_fold_gen.py  (D20 plans -> Groovy/Kotlin runtime assembly)",
              "oracle_cmd": (f"(grep -v ^pipeline tests/data/script_fixtures/{name}; echo 'println {var}') > $TMPDIR/o.groovy && "
                             "/usr/lib/jvm/java-21-openjdk-amd64/bin/java -cp "
                             "tools/ghidra/Ghidra/Features/GhidraServer/data/yajsw-stable-13.18/lib/extended/groovy/groovy-4.0.12.jar "
                             "groovy.ui.GroovyMain $TMPDIR/o.groovy" if groovy else
                             "python3 -I -c \"import re,sys; s=open(sys.argv[1]).read(); ...\" (stdlib inverse of the generator: "
                             "concat literals, bytes(byteArrayOf), chr(b ^ 0x2A)); no kotlinc on the build host")}
        if plan is None:
            fx["oracle_cmd"] += "  -> the descriptor is not a v=3 plan (unbound env / truncated b64 / benign text)"
        (HERE / (stem + ".json")).write_text(json.dumps(fx, indent=1) + "\n")
        print(name, var)
