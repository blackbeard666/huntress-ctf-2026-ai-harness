"""Regenerate the malbolge fixtures: programs from malbolge_gen.pl (Perl, independent of lib/), plain text read back
by the PyPI `malbolge` 1.0.0 reference interpreter vendored at tools/malbolge-pkg (also independent of lib/)."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
HELLO = "(=<`#9]~6ZY32Vx/4Rs+0No-&Jk)\"Fh}|Bcy?`=*z]Kw%oG4UUS0/@-ejc(:'8dc"   # Wikipedia's Malbolge hello world


def oracle(prog):
    path = os.path.join(os.environ.get("TMPDIR", "/tmp"), "malbolge_fixture.mb")
    with open(path, "w") as f:
        f.write(prog)
    code = ("import sys; sys.path.insert(0, %r); from malbolge.malbolge import main; "
            "sys.argv = ['malbolge', %r]; main()") % (os.path.join(ROOT, "tools/malbolge-pkg"), path)
    r = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, stdin=subprocess.DEVNULL, timeout=120)
    return r.stdout.decode("utf-8", "replace"), r.returncode


def gen(plain, width=0):
    cmd = ["perl", os.path.join(HERE, "malbolge_gen.pl"), plain] + ([str(width)] if width else [])
    return subprocess.run(cmd, capture_output=True, check=True, text=True).stdout


def write(name, codec, plain, encoded, generator_cmd, decoy=False):
    out, rc = oracle(encoded)
    d = {"codec": codec, "plain": None if decoy else plain, "encoded": encoded, "generator_cmd": generator_cmd,
         "oracle_cmd": "python3 -c 'from malbolge.malbolge import main; main()' prog.mb   "
                       "# PyPI malbolge 1.0.0 vendored at tools/malbolge-pkg (PYTHONPATH)" +
                       ("  -> " + out.strip()[:60] if decoy else ""),
         "oracle_plain": out if not decoy else out.strip(), "expected": "none" if decoy else "match"}
    if decoy:
        d["decoy"] = True
    else:
        assert out == plain, (name, out, plain)
    with open(os.path.join(HERE, name + ".json"), "w") as f:
        json.dump(d, f, indent=1)
        f.write("\n")
    print(name, rc, repr(out[:80]))


if __name__ == "__main__":
    for tag, w in (("jade-lynx-72", 0), ("amber-falcon-42", 72)):
        plain = f"Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {tag}"
        write(f"malbolge-{tag.split('-')[0]}" + ("-wrapped" if w else ""), "malbolge", plain, gen(plain, w),
              f'perl tests/data/warmups_fixtures/malbolge_gen.pl "$plain"' + (f" {w}" if w else ""))
    # decoy 1: the published hello world with one char flipped -> invalid op at that index (interpreter refuses)
    bad = HELLO[:10] + chr(ord(HELLO[10]) + 1) + HELLO[11:]
    write("malbolge-decoy-corrupt-hello", "malbolge", None, bad,
          "python3 -c 'h=<Wikipedia Malbolge hello world>; print(h[:10] + chr(ord(h[10]) + 1) + h[11:])'", True)
    # decoy 2: the published hello world itself: a valid program, but 'Hello World!' is no warmup sentence / slug
    write("malbolge-decoy-hello-world", "malbolge", None, HELLO,
          "printf %s '<Wikipedia Malbolge hello world program>'", True)
