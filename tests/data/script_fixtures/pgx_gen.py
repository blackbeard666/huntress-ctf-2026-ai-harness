"""Generate the XSLT v=3 polyglot fixtures (target xslt-v3-fixtures).

D23-D27 shape: `<?xml ..?>` on line 1, `<!-- HUNTRESS_ANALYSIS_V1:<TAG>-<material> -->` on line 2 (some written tight,
`..<material>-->`, so a marker reading must stop at `-->`), then an <xsl:stylesheet> holding one descriptor:
<xsl:variable name="huntress_descriptor" select="'..'"/>, <xsl:param ..>, text content <xsl:variable name="d">..</..>,
CDATA, or entity-escaped data (`&#x2E;` FRAG dots, `&#x3D;` base64 padding) and a use site
<xsl:value-of select="$..."/>. `-nomark` fixtures drop the marker. Encoders: stdlib base64/binascii only.
expected_plain is NOT taken from this script or lib.codec: each fixture's oracle_cmd applies the stylesheet with
libxslt's `xsltproc` (which resolves the entities / CDATA itself) and decodes its stdout with coreutils base64 / xxd.

    python3 -I tests/data/script_fixtures/pgx_gen.py
"""
import base64
import binascii
import hashlib
import json
import pathlib
import subprocess

D = pathlib.Path(__file__).resolve().parent
GEN = "python3 -I tests/data/script_fixtures/pgx_gen.py  (stdlib base64/binascii encode of the plan; xslt template)"
DEC = {"HEX": "xxd -r -p", "B64": "base64 -d", "HB64": "xxd -r -p | base64 -d", "FRAG": "tr -d . | xxd -r -p"}
ROLES = {  # role -> (TAG, verdict, attack, adapter, obfuscation, stage_profile, next_language, stage_count, steps)
    "benign-utility": ("HEX", "benign", "none", "local_parser", "plain_hex", "single_descriptor", "powershell", 2,
                       "decode_configuration,return_configuration"),
    "downloader": ("B64", "suspicious", "T1105", "http_client", "base64", "two_stage_download_execute", "jscript", 2,
                   "acquire_remote,dispatch_process"),
    "launcher": ("HB64", "suspicious", "T1220", "process_builder", "hex_base64", "three_stage_decode_write_launch",
                 "batch", 3, "decode_embedded,write_file,dispatch_process"),
    "staged-chain": ("FRAG", "suspicious", "T1220", "operation_graph", "fragmented_hex", "cross_language_handoff",
                     "vbscript", 3, "profile_host,decode_configuration,dispatch_language"),
}
HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n'
OPEN = ('<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">\n'
        '  <xsl:output method="text"/>\n')


def h(*parts, n=16):
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:n]


def plan(role, salt=""):
    tag, verdict, attack, adapter, obf, sp, nl, sc, steps = ROLES[role]
    x = h("pgx", role, salt)
    return ("v=3|language=xslt|role=%s|verdict=%s|attack=%s|adapter=%s|host_profile=standalone|obfuscation_profile=%s|"
            "stage_profile=%s|next_language=%s|stage_count=%d|steps=%s|campaign_id=XSLT-%s|"
            "url=https://xslt-%s.example.invalid/stage|file_path=/tmp/huntress-xslt/.%s.stage"
            % (role.replace("-", "_"), verdict, attack, adapter, obf, sp, nl, sc, steps, x[:8], x[:10], x))


def encode(tag, p):
    b = p.encode()
    if tag == "HEX":
        return binascii.hexlify(b).decode()
    if tag == "B64":
        return base64.b64encode(b).decode()
    if tag == "HB64":
        return binascii.hexlify(base64.b64encode(b)).decode()
    x = binascii.hexlify(b).decode()
    return ".".join(x[i:i + 24] for i in range(0, len(x), 24))


def esc(v):
    """Character references for the FRAG dots and the base64 padding (xsltproc resolves them, a grep does not)."""
    return v.replace(".", "&#x2E;").replace("=", "&#x3D;")


def cdata(v):
    return "<![CDATA[%s]]>" % v


# descriptor forms: form -> (name, body(value)); every form has a use site <xsl:value-of select="$name"/>
FORMS = {
    "select": ("huntress_descriptor",
               lambda v: '  <xsl:variable name="huntress_descriptor" select="\'%s\'"/>\n' % v),
    "param": ("huntress_descriptor", lambda v: '  <xsl:param name="huntress_descriptor" select="\'%s\'"/>\n' % v),
    "text": ("d", lambda v: '  <xsl:variable name="d">%s</xsl:variable>\n' % v),
    "selectesc": ("huntress_descriptor",
                  lambda v: '  <xsl:variable name="huntress_descriptor" select="\'%s\'"/>\n' % esc(v)),
    "paramesc": ("huntress_descriptor", lambda v: '  <xsl:param name="huntress_descriptor" select="\'%s\'"/>\n' % esc(v)),
    "textesc": ("d", lambda v: '  <xsl:variable name="d">%s</xsl:variable>\n' % esc(v)),
    "cdata": ("huntress_descriptor",
              lambda v: '  <xsl:variable name="huntress_descriptor">%s</xsl:variable>\n' % cdata(v)),
}
# role -> (form, tight marker `..-->`)
MARKED = {"benign-utility": ("text", True), "downloader": ("select", False), "launcher": ("param", True),
          "staged-chain": ("selectesc", False)}
NOMARK = {"paramesc": "staged-chain", "cdata": "downloader", "textesc": "downloader", "select": "launcher"}
ORACLE = "echo '<x/>' | xsltproc {f} - | %s"


def doc(marker, form, v):
    name, body = FORMS[form]
    return (HEAD + marker + OPEN + body(v) +
            '  <xsl:template match="/"><xsl:value-of select="$%s"/></xsl:template>\n</xsl:stylesheet>\n' % name)


def write(stem, role, src, ocmd, expect, decoy=False):
    sp = D / (stem + ".xsl")
    sp.write_text(src)
    ocmd = ocmd.replace("{f}", "tests/data/script_fixtures/" + sp.name)
    out = subprocess.run(["bash", "-c", ocmd], cwd=D.parents[2], capture_output=True).stdout.decode("utf-8", "replace")
    if not decoy:
        assert out == expect, (stem, out[:80], expect[:80])
    fx = {"expected_plain": None if decoy else out, "decoy": decoy, "language": "xslt", "role": role,
          "family": "polyglot-xslt", "generator_cmd": GEN, "oracle_cmd": ocmd}
    if decoy:
        fx["oracle_stdout"] = out
    else:  # GM-shaped fields, read from the ORACLE's plan text (k=v split, urlsplit), not from lib.codec
        from urllib.parse import urlsplit
        kv = dict(x.split("=", 1) for x in out.split("|"))
        fx["expected_fields"] = {k: v for k, v in kv.items() if k != "v"}
        fx["expected_fields"]["url_host"] = urlsplit(kv["url"]).hostname
        fx["expected_fields"]["file_dir"] = kv["file_path"].rsplit("/", 1)[0] + "/"
    (D / (stem + ".json")).write_text(json.dumps(fx, indent=1) + "\n")


def main():
    n = 0
    for role, (form, tight) in MARKED.items():
        tag = ROLES[role][0]
        p = plan(role)
        mat = encode(tag, p)
        marker = "<!-- HUNTRESS_ANALYSIS_V1:%s-%s%s-->\n" % (tag, mat, "" if tight else " ")
        write("polyglot-xslt-%s" % role, role, doc(marker, form, mat), ORACLE % DEC[tag], p)
        n += 1
    for form, role in NOMARK.items():
        tag = ROLES[role][0]
        p = plan(role, form)
        mat = encode(tag, p)
        write("polyglot-xslt-%s-nomark" % form, role, doc("<!-- inert analysis fixture -->\n", form, mat),
              ORACLE % DEC[tag], p)
        n += 1
    # marker only (tight `==-->`, no descriptor): the marker reading itself must stop at `-->`
    p = plan("downloader", "markeronly")
    mat = encode("B64", p)
    src = (HEAD + "<!-- HUNTRESS_ANALYSIS_V1:B64-%s-->\n" % mat + OPEN +
           '  <xsl:template match="/"><xsl:text>inert-analysis-fixture</xsl:text></xsl:template>\n</xsl:stylesheet>\n')
    write("polyglot-xslt-markeronly-tight", "downloader", src,
          "sed -n 2p {f} | sed -E 's/^<!-- HUNTRESS_ANALYSIS_V1:B64-//; s/-->$//' | base64 -d", p)
    junk = base64.b64encode(b"status=ok;inert-analysis-fixture;no plan here").decode()
    write("polyglot-xslt-decoy", "decoy", doc("<!-- HUNTRESS_ANALYSIS_V1:B64-%s-->\n" % junk, "select", junk),
          ORACLE % "base64 -d", None, decoy=True)
    write("polyglot-xslt-decoy-cdata-nomark", "decoy",
          doc("<!-- inert analysis fixture -->\n", "cdata", "&#x2E;inert;" + junk[:20]),
          ORACLE % "base64 -d", None, decoy=True)
    print("wrote %d fixtures + 2 decoys" % (n + 1))


if __name__ == "__main__":
    main()
