"""Generator for the JSON-carrier battery (target notebook-manifest-json-carrier): a D1-D20-style v=3 plan carried as
a script inside a JSON document -- Jupyter .ipynb (`source` = list of lines, `%%bash` / `!cmd` magics), VS Code
tasks.json (JSONC: comments + trailing commas, `command`/`args`, runOptions.runOn folderOpen), package.json
`scripts.postinstall`, composer.json `scripts`, .devcontainer.json `postCreateCommand` (JSONC), Logic App
`definition.actions.*.inputs`. stdlib only (json, base64, binascii, gzip). Each json carries an independent oracle
(python3 json / re + base64 / xxd / gunzip -- never lib.codec) that this generator runs to prove `expected_plain`."""
import base64
import binascii
import gzip
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).parent


def plan(host, lang, tag):
    return (f"v=3|language={lang}|role=staged_chain|verdict=suspicious|attack=T1059|adapter=operation_graph|"
            f"host_profile={host}|obfuscation_profile=base64|stage_profile=two_stage_download_execute|"
            f"next_language=powershell|stage_count=2|steps=acquire_remote,dispatch_process|campaign_id={tag}|"
            f"url=https://{tag.lower()}.example.invalid/stage|file_path=/tmp/huntress-{tag.lower()}/.stage")


b64 = lambda s: base64.b64encode(s.encode()).decode()
hx = lambda s: binascii.hexlify(s.encode()).decode()
gzb64 = lambda s: base64.b64encode(gzip.compress(s.encode(), mtime=0)).decode()
codes = lambda s: ",".join(str(ord(c)) for c in s)
lines = lambda t: [ln for ln in t.splitlines(True)]      # nbformat: list of lines, each keeping its "\n"

FX = []   # (file, text, expected_plain|None, decoy, generator note, oracle)

# 1. Jupyter notebook, python kernel, `%%bash` cell magic: bash descriptor split over two lines with `\` continuation
p = plan("jupyter_notebook", "bash", "NBSH-4a5b6c7d"); h = b64(p)
nb = {"cells": [
    {"cell_type": "markdown", "metadata": {}, "source": lines("# inert analysis fixture\nRun the setup cell.")},
    {"cell_type": "code", "execution_count": 1, "metadata": {}, "outputs": [
        {"output_type": "display_data", "metadata": {}, "data": {
            "image/png": base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\0" * 40).decode(), "text/plain": ["<Figure>"]}}],
     "source": lines("%%bash\n"
                     f"descriptor_4a5b6c7d=\"{h[:120]}\"\\\n\"{h[120:]}\"\n"
                     "echo \"$descriptor_4a5b6c7d\" | base64 -d >/dev/null\n")}],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
    "nbformat": 4, "nbformat_minor": 5}
FX.append(("jcar_ipynb_bash_magic.ipynb", json.dumps(nb, indent=1) + "\n", p, False,
           "python3 json.dumps(nbformat-4, source=list of lines) + stdlib base64; %%bash cell, `\\`-continued literal",
           "python3 -c \"import json,re,base64;s=''.join(json.load(open('jcar_ipynb_bash_magic.ipynb'))['cells'][1]['source']);"
           "print(base64.b64decode(''.join(re.findall(r'\\\"([A-Za-z0-9+/=]{20,})\\\"',s))).decode(),end='')\""))

# 2. Jupyter notebook, `!` shell escapes: the descriptor is built over several `!` lines (hex), python kernel
p = plan("jupyter_notebook", "bash", "NBBANG-8e9f0a1b"); x = hx(p); q = len(x) // 3
nb = {"cells": [
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [
        {"output_type": "stream", "name": "stdout", "text": ["ok\n"]}],
     "source": lines(f"!echo -n '{x[:q]}' > /tmp/.d_8e9f0a1b\n"
                     f"!echo -n '{x[q:2 * q]}' >> /tmp/.d_8e9f0a1b\n"
                     f"!echo -n '{x[2 * q:]}' >> /tmp/.d_8e9f0a1b\n"
                     "!xxd -r -p /tmp/.d_8e9f0a1b >/dev/null")}],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
    "nbformat": 4, "nbformat_minor": 4}
FX.append(("jcar_ipynb_bang_hex.ipynb", json.dumps(nb, indent=1) + "\n", p, False,
           "python3 json.dumps(nbformat-4) + stdlib binascii.hexlify, chunked over 3 `!echo` lines",
           "python3 -c \"import json,re;s=''.join(json.load(open('jcar_ipynb_bang_hex.ipynb'))['cells'][0]['source']);"
           "print(bytes.fromhex(''.join(re.findall(r\\\"'([0-9a-f]+)'\\\",s))).decode(),end='')\""))

# 3. VS Code tasks.json (JSONC): comments, trailing commas, runOn folderOpen, PowerShell command + args split
p = plan("vscode_tasks", "powershell", "VSCT-2c3d4e5f"); g = gzb64(p); k = len(g) // 2
tasks = (
    "// See https://go.microsoft.com/fwlink/?LinkId=733558\n"
    "{\n"
    "  \"version\": \"2.0.0\", /* workspace tasks */\n"
    "  \"tasks\": [\n"
    "    {\n"
    "      \"label\": \"restore\",\n"
    "      \"type\": \"shell\",\n"
    "      \"command\": \"powershell\",\n"
    "      \"args\": [\n"
    "        \"-NoProfile\",\n"
    "        \"-Command\",\n"
    f"        \"$descriptor_2c3d4e5f = '{g[:k]}' +\",\n"
    f"        \"'{g[k:]}';\",\n"
    "        \"$null = $descriptor_2c3d4e5f\", // decoded at runtime\n"
    "      ],\n"
    "      \"runOptions\": { \"runOn\": \"folderOpen\", },\n"
    "      \"presentation\": { \"reveal\": \"never\", },\n"
    "    },\n"
    "  ],\n"
    "}\n")
FX.append(("jcar_vscode_tasks_jsonc.json5", tasks, p, False,
           "hand-written JSONC (comments + trailing commas) around python3 gzip.compress(mtime=0)|base64, split over 2 args",
           "python3 -c \"import re,base64,gzip;s=open('jcar_vscode_tasks_jsonc.json5').read();"
           "print(gzip.decompress(base64.b64decode(''.join(re.findall(r\\\"'([A-Za-z0-9+/=]{20,})'\\\",s)))).decode(),end='')\""))

# 4. package.json scripts.postinstall: `node -e "..."` whose inner quotes are shell-escaped (\\" after JSON), base64
p = plan("npm_lifecycle", "node", "NPM-6a7b8c9d")
inner = (f'const descriptor_6a7b8c9d = \\"{b64(p)}\\"; '
         "const s = Buffer.from(descriptor_6a7b8c9d, 'base64').toString(); void s;")
pkg = {"name": "inert-fixture", "version": "1.0.0", "description": "inert analysis fixture",
       "scripts": {"test": "echo ok", "postinstall": f'node -e "{inner}"'}, "license": "MIT"}
FX.append(("jcar_npm_postinstall.json5", json.dumps(pkg, indent=2) + "\n", p, False,
           "python3 json.dumps(package.json) with node -e \"..\" (shell-escaped inner quotes), stdlib base64",
           "python3 -c \"import json,re,base64;s=json.load(open('jcar_npm_postinstall.json5'))['scripts']['postinstall'];"
           "print(base64.b64decode(re.search(r'([A-Za-z0-9+/=]{40,})',s).group(1)).decode(),end='')\""))

# 5. .devcontainer.json (JSONC) postCreateCommand argv list: bash -c with '-escaped quotes, hex descriptor
p = plan("devcontainer", "bash", "DEVC-0d1e2f3a")
body = f"descriptor_0d1e2f3a='{hx(p)}'; printf %s \"$descriptor_0d1e2f3a\" | xxd -r -p >/dev/null"
dev = ("{\n  // inert analysis fixture\n  \"name\": \"fixture\",\n  \"image\": \"mcr.microsoft.com/devcontainers/base:ubuntu\",\n"
       "  \"postCreateCommand\": [\"bash\", \"-c\", " + json.dumps(body).replace("'", "\\u0027") + "],\n"
       "  \"customizations\": { \"vscode\": { \"extensions\": [], }, },\n}\n")
FX.append(("jcar_devcontainer_postcreate.json5", dev, p, False,
           "hand-written JSONC; argv body via python3 json.dumps with ' written as \\u0027; stdlib binascii.hexlify",
           "python3 -c \"import re;s=open('jcar_devcontainer_postcreate.json5').read();"
           "print(bytes.fromhex(re.search(r'u0027([0-9a-f]{80,})',s).group(1)).decode(),end='')\""))

# 6. composer.json scripts (list form, `@php -r`), base64 descriptor in PHP
p = plan("composer_scripts", "php", "COMP-5b6c7d8e")
comp = {"name": "inert/fixture", "require": {},
        "scripts": {"post-install-cmd": ["@php -r \"$descriptor_5b6c7d8e = '" + b64(p) + "'; base64_decode($descriptor_5b6c7d8e);\"",
                                         "echo done"]}}
FX.append(("jcar_composer_scripts.json5", json.dumps(comp, indent=4) + "\n", p, False,
           "python3 json.dumps(composer.json), scripts list form, stdlib base64",
           "python3 -c \"import json,re,base64;s=json.load(open('jcar_composer_scripts.json5'))['scripts']['post-install-cmd'][0];"
           "print(base64.b64decode(re.search(r\\\"'([A-Za-z0-9+/=]{20,})'\\\",s).group(1)).decode(),end='')\""))

# 7. DECOY: tasks.json JSONC, folderOpen auto-run but benign; a long base64 that is not a plan
dec = ("{\n  // benign\n  \"version\": \"2.0.0\",\n  \"tasks\": [{\n    \"label\": \"build\", \"type\": \"shell\",\n"
       "    \"command\": \"bash\",\n    \"args\": [\"-c\", \"descriptor_00aa11bb='"
       + base64.b64encode(b"just a build banner, nothing to see here at all; inert text only.").decode()
       + "'; make all\",],\n    \"runOptions\": {\"runOn\": \"folderOpen\",},\n  },],\n}\n")
FX.append(("jcar_decoy_tasks_benign.json5", dec, None, True, "hand-written JSONC, stdlib base64 of a banner (no plan)",
           "python3 -c \"import re,base64;s=open('jcar_decoy_tasks_benign.json5').read();"
           "print(base64.b64decode(re.search(r\\\"'([A-Za-z0-9+/=]{20,})'\\\",s).group(1)))\"  # -> banner, not v=3"))

# 8. DECOY: notebook whose %%bash descriptor is a truncated gzip stream
p = plan("jupyter_notebook", "bash", "NBTR-9a8b7c6d"); g = gzb64(p)[:60]
nb = {"cells": [{"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                 "source": lines(f"%%bash\ndescriptor_9a8b7c6d=\"{g}\"\necho $descriptor_9a8b7c6d | base64 -d | gunzip\n")}],
      "metadata": {"kernelspec": {"language": "python", "name": "python3"}}, "nbformat": 4, "nbformat_minor": 5}
FX.append(("jcar_decoy_ipynb_truncgz.ipynb", json.dumps(nb, indent=1) + "\n", None, True,
           "python3 json.dumps(nbformat-4), gzip|base64 truncated to 60 chars",
           "python3 -c \"import json,re,base64,zlib;s=''.join(json.load(open('jcar_decoy_ipynb_truncgz.ipynb'))['cells'][0]['source']);"
           "print(zlib.decompressobj(31).decompress(base64.b64decode(re.search(r'\\\"([A-Za-z0-9+/=]{20,})\\\"',s).group(1)+'==')))\"  # -> partial/none"))

if __name__ == "__main__":
    for fn, text, exp, decoy, gen, orc in FX:
        (HERE / fn).write_text(text)
        stem = fn.rsplit(".", 1)[0]
        r = subprocess.run(orc.split("  #")[0], shell=True, cwd=HERE, capture_output=True, text=True)
        if not decoy:
            assert r.stdout == exp, (fn, r.stdout[:80], r.stderr[-300:])
        else:
            assert "v=3" not in r.stdout, fn
        (HERE / f"{stem}.json").write_text(json.dumps({
            "expected_plain": exp, "decoy": decoy,
            "generator_cmd": f"python3 tests/data/script_fixtures/json_carrier_gen.py  # {gen}, written as {fn}",
            "oracle_cmd": orc}, indent=1) + "\n")
        print("ok", fn)
