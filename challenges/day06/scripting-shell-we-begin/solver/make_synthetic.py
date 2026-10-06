#!/usr/bin/env python3
"""Build cases/synthetic-mastery-bash: set1 = the real Single Solve Bash fixtures (GM-confirmed answers), set2 = the
same six graphs re-encoded with new values and other representations / transforms / loop syntax (hex_compact +
repeating key array, rolling xor chained on the cipher byte, Material split over two variables, while/if loops, no
Codec const, CRLF). set2's expected.json is written from the plans we encode here, independently of the solver."""
import json, shutil, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SS = HERE.parent / "single_solve"
OUT = HERE / "cases" / "synthetic-mastery-bash"
EVID = SS / "artifacts" / "latest" / "evidence.zip"

FILES = {"host-context.sh": "bash-benign", "memory-stage.sh": "bash-stager", "embedded-write.sh": "bash-dropper",
         "remote-write.sh": "bash-downloader", "local-dispatch.sh": "bash-launcher", "staged-chain.sh": "bash-chain"}
ATTACK = {"benign_utility": "none", "stager": "T1105", "dropper": "T1140", "downloader": "T1105",
          "launcher": "T1059.004", "staged_chain": "T1059.004"}

H = "7c41d0e9a2"
PLANS = {  # name -> (role, indicator key, plan text)
    "host-context.sh": ("benign_utility", "host_id",
                        f"v=1|steps=decode_configuration,return_configuration|adapter=readonly_configuration|stage_count=1|campaign_id=campaign-{H}|host_id=host-{H}"),
    "memory-stage.sh": ("stager", "url",
                        f"v=1|steps=acquire_remote,dispatch_pipe|adapter=curl_stdout_pipe|stage_count=1|campaign_id=campaign-{H}1|url=https://{H}1.example.invalid/0badf00d.sh|user_agent=HuntressLab/{H}1"),
    "embedded-write.sh": ("dropper", "file_path",
                          f"v=1|steps=decode_embedded,write_file|adapter=base64_install|stage_count=1|campaign_id=campaign-{H}2|file_path=/var/tmp/huntress-cache/.stage-{H}2"),
    "remote-write.sh": ("downloader", "url",
                        f"v=1|steps=acquire_remote,write_file|adapter=curl_output|stage_count=1|campaign_id=campaign-{H}3|url=https://{H}3.example.invalid/feedface.sh|user_agent=HuntressLab/{H}3|file_path=/tmp/huntress-cache/.stage-{H}3"),
    "local-dispatch.sh": ("launcher", "file_path",
                          f"v=1|steps=locate_local,dispatch_process|adapter=bash_script|stage_count=1|campaign_id=campaign-{H}4|file_path=/tmp/huntress-cache/.stage-{H}4"),
    "staged-chain.sh": ("staged_chain", "cron_path",
                        f"v=1|steps=profile_host,acquire_remote,write_file,change_mode,dispatch_process|adapter=curl_arch_fallback|stage_count=5|campaign_id=campaign-{H}5|url=https://{H}5.example.invalid/c0ffee00.sh|user_agent=HuntressLab/{H}5|file_path=/tmp/huntress-cache/.stage-{H}5|arch_probe=uname-m|service_name=update-{H}5.service|cron_path=/etc/cron.d/update-{H}5"),
}

TAIL = '''
Recover_{f}() {{
  local -a e d
  local t i
  Load_{f}
  {call}
  t=''
  local octal character
  for i in "${{!d[@]}}"; do
    printf -v octal '%03o' "${{d[i]}}"
    printf -v character '%b' "\\\\$octal"
    t+="$character"
  done
  printf '%s\\n' "$t"
}}

Inspect_{f}() {{ Recover_{f}; }}

if [[ ${{HUNTRESS_INSPECT_ONLY:-0}} == 1 ]]; then Inspect_{f}; fi
'''


def build(name, plan):
    raw = plan.encode()
    f = "%08x" % (0x5eb00000 + sum(name.encode()))
    head = "#!/usr/bin/env bash\n# synthetic variant (inert)\n"
    if name == "host-context.sh":  # hex_compact + repeating_key_xor with a key array in Decode_
        key = [0x13, 0x37, 0xc4]
        enc = bytes(b ^ key[i % 3] for i, b in enumerate(raw)).hex()
        body = (f"readonly Material_{f}='{enc}'\nreadonly Codec_{f}='hex_compact|repeating_key_xor|13,37,c4'\n\n"
                f"Load_{f}() {{\n  e=()\n  local raw=\"${{Material_{f}}}\" i\n"
                f"  for ((i=0; i<${{#raw}}; i+=2)); do e+=(\"$((16#${{raw:i:2}}))\"); done\n}}\n\n"
                f"Decode_{f}() {{\n  d=()\n  local -a key=(0x13 0x37 0xc4)\n  local i\n"
                f"  for ((i=0; i<${{#e[@]}}; i++)); do\n    d+=(\"$(( e[i] ^ key[i % ${{#key[@]}}] ))\")\n  done\n}}\n")
        call = f"if ((2 > 1)); then Decode_{f}; fi"
    elif name == "memory-stage.sh":  # decimal_comma + rolling xor on the previous cipher byte, no Codec const
        out, prev = [], 0x5a
        for b in raw:
            c = b ^ prev
            out.append(c)
            prev = c
        body = (f"readonly Material_{f}='{','.join(map(str, out))}'\n\n"
                f"Load_{f}() {{\n  e=()\n  local IFS=','\n  read -r -a e <<< \"${{Material_{f}}}\"\n}}\n\n"
                f"Decode_{f}() {{\n  d=()\n  local prev=90 i\n"
                f"  for i in \"${{!e[@]}}\"; do d+=(\"$(( e[i] ^ prev ))\"); prev=${{e[i]}}; done\n}}\n")
        call = f"case 1 in 1) Decode_{f} ;; esac"
    elif name == "embedded-write.sh":  # hex_colon + subtract_modulo_256, Material split over two variables
        enc = ":".join("%02x" % ((b - 0x2d) % 256) for b in raw)
        mid = len(enc) // 2
        body = (f"readonly Material_{f}_a='{enc[:mid]}'\nreadonly Material_{f}_b='{enc[mid:]}'\n"
                f"readonly Codec_{f}='hex_colon|subtract_modulo_256|2d'\n\n"
                f"Load_{f}() {{\n  e=()\n  local joined=\"${{Material_{f}_a}}${{Material_{f}_b}}\" h\n"
                f"  for h in ${{joined//:/ }}; do e+=(\"$((16#$h))\"); done\n}}\n\n"
                f"Decode_{f}() {{\n  d=()\n  local i=0\n  while ((i < ${{#e[@]}})); do\n"
                f"    d[i]=$(( (e[i] + 45) % 256 ))\n    ((i++))\n  done\n}}\n")
        call = f"Decode_{f} || return 70"
    elif name == "remote-write.sh":  # base64 + single_byte_xor, double-quoted material, CRLF file
        import base64
        enc = base64.b64encode(bytes(b ^ 0xa7 for b in raw)).decode()
        body = (f"declare -r Material_{f}=\"{enc}\"\ndeclare -r Codec_{f}=\"base64_literal|single_byte_xor|a7\"\n\n"
                f"Load_{f}() {{\n  e=()\n  local p\n  while read -r p; do [[ -n \"$p\" ]] && e+=(\"$p\"); done < <(printf '%s' \"${{Material_{f}}}\" | base64 -d | od -An -v -tu1 | tr -s ' ' '\\n' | sed '/^$/d')\n}}\n\n"
                f"Decode_{f}() {{\n  d=()\n  local i\n  for ((i=0; i<${{#e[@]}}; i++)); do\n"
                f"    if ((1)); then d+=(\"$(( e[i] ^ 0xa7 ))\"); fi\n  done\n}}\n")
        call = f"for pass in 1; do Decode_{f}; done"
    elif name == "local-dispatch.sh":  # decimal_pipe stored reversed, Decode_ walks it backwards (reverse_bytes)
        enc = "|".join(map(str, raw[::-1]))
        body = (f"readonly Material_{f}='{enc}'\nreadonly Codec_{f}='decimal_pipe|reverse_bytes|'\n\n"
                f"Load_{f}() {{\n  e=()\n  local IFS='|'\n  read -r -a e <<< \"${{Material_{f}}}\"\n}}\n\n"
                f"Decode_{f}() {{\n  d=()\n  local i\n  for ((i=${{#e[@]}}-1; i>=0; i--)); do d+=(\"${{e[i]}}\"); done\n}}\n")
        call = f"Decode_{f}"
    else:  # staged-chain: octal list + add_modulo_256, appended with +=
        enc = " ".join("%o" % ((b + 0x31) % 256) for b in raw)
        third = len(enc) // 3
        cut1 = enc.index(" ", third)
        body = (f"Material_{f}='{enc[:cut1]}'\nMaterial_{f}+='{enc[cut1:]}'\nreadonly Codec_{f}='octal_space|add_modulo_256|31'\n\n"
                f"Load_{f}() {{\n  e=()\n  local o\n  for o in ${{Material_{f}}}; do e+=(\"$((8#$o))\"); done\n}}\n\n"
                f"Decode_{f}() {{\n  d=()\n  local i\n  for ((i=0; i<${{#e[@]}}; i++)); do\n"
                f"    d+=(\"$(((e[i] - 49 + 256) % 256))\")\n  done\n}}\n")
        call = f"Decode_{f}"
    src = head + body + TAIL.format(f=f, call=call)
    if name == "remote-write.sh":
        src = src.replace("\n", "\r\n")
    return src.encode()


def main():
    contract = json.loads((SS / "contract.json").read_text())
    confirmed = json.loads((SS / "answers.json").read_text())
    qs = [q for q in contract["questions"] if q["id"].startswith("bash-")]
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "artifacts").mkdir(parents=True)
    shutil.copy(EVID, OUT / "artifacts" / "evidence-01.zip")
    with zipfile.ZipFile(OUT / "artifacts" / "evidence-02.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for name, (_, _, plan) in PLANS.items():
            z.writestr(name, build(name, plan))
    ids, questions, expected = [], [], {}
    for n in (1, 2):
        for q in qs:
            q2 = dict(q, id="set%d.%s" % (n, q["id"]), artifact=q["artifact"].replace("evidence.zip", "evidence-%02d.zip" % n))
            ids.append(q2["id"])
            questions.append(q2)
            if n == 1:
                expected[q2["id"]] = confirmed[q["id"]]
                continue
            member = q["artifact"].split("->")[-1].strip()
            role, ind, plan = PLANS[member]
            kv = dict(x.split("=", 1) for x in plan.split("|"))
            suffix = q["id"][len(FILES[member]) + 1:]
            expected[q2["id"]] = {"role": role, "attack": ATTACK[role], "adapter": kv["adapter"],
                                  "campaign": kv["campaign_id"], "stage-count": kv["stage_count"],
                                  "steps": kv["steps"].replace(",", ">")}.get(suffix) or kv[suffix.replace("-", "_")]
    c = {"mode": "mastery", "name": contract.get("name"), "prompt": contract.get("prompt"),
         "artifacts": [{"filename": "evidence-01.zip"}, {"filename": "evidence-02.zip"}],
         "questions": questions, "answer_ids": ids}
    (OUT / "contract.json").write_text(json.dumps(c, indent=1))
    (OUT / "expected.json").write_text(json.dumps(expected, indent=1))
    print("wrote", OUT, len(ids), "ids")


if __name__ == "__main__":
    sys.exit(main())
