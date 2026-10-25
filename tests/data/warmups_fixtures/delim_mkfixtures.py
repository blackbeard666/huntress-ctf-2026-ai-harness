"""Offline generator for tests/data/warmups_fixtures/delim-*.json (delimited-field framing: CSV / TSV / Lisp char
lists / YAML flow sequences, one char or word per field). Every writer and reader is an independent standard tool:
CSV = Python csv / Ruby CSV (each writes, the other reads); TSV = a Perl writer, Python reader; Scheme = CHICKEN 5.3
csi (tools/lisp, dpkg -x of chicken-bin) writes, SBCL 2.6 reads, and the reverse for CL; Clojure 1.12 (tools/jvmlangs)
prn writes, clojure.edn reads; YAML = PyYAML 6 safe_dump flow style writes, Ruby Psych reads. Never lib.warmups_codecs.
Run: python3 -I tests/data/warmups_fixtures/delim_mkfixtures.py"""
import json
import os
import subprocess

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(D, "..", "..", ".."))
LISP = ("R=tools/lisp/root; export LD_LIBRARY_PATH=$R/usr/lib/x86_64-linux-gnu:$R/usr/lib SBCL_HOME=$R/usr/lib/sbcl; ")
CSI = LISP + "$R/usr/bin/csi -q -e "
SBCL = LISP + "$R/usr/bin/sbcl --script <(echo {prog})"
CLJJ = "J=tools/jvmlangs/x/usr/share/java; "
CLJ = ("java -cp $J/clojure-1.12.0.jar:$J/spec.alpha-0.5.238.jar:$J/core.specs.alpha-0.4.74.jar "
       "clojure.main -e ")


def P(slug, head="Nice work decoding this warmup!"):
    return f"{head} To solve, submit this exact answer to the Game Master: {slug}"


PY_CSV_ORACLE = ("python3 -I -c \"import csv,sys; print(''.join(f for r in csv.reader(sys.stdin, delimiter={d!r}) "
                 "for f in r), end='')\"")
RB_CSV_ORACLE = "ruby -rcsv -e 'print CSV.parse(STDIN.read, col_sep: \"{d}\").flatten.join'"
RB_YAML_ORACLE = ("ruby -ryaml -e 'v = YAML.safe_load(STDIN.read); raise \"not a list of strings\" unless "
                  "v.is_a?(Array) && v.all? { |x| x.is_a?(String) }; print v.join'")
PY_TSV_ORACLE = ("python3 -I -c \"import sys,codecs; t=sys.stdin.read(); "
                 "print(''.join(codecs.decode(f, 'unicode_escape') for f in t.split(chr(9))), end='')\"")

FIX = [
    ("delim-csv-quoteall-python-amber", P("amber-heron-58", 'Nice work decoding this "warmup"!'),
     "python3 -I -c \"import csv,sys; csv.writer(sys.stdout, quoting=csv.QUOTE_ALL, lineterminator='')"
     ".writerow(list(sys.argv[1]))\" \"$plain\"", RB_CSV_ORACLE.format(d=",")),
    ("delim-csv-minimal-ruby-cobalt", P("cobalt-otter-31", 'Nice work decoding this "warmup"!'),
     "ruby -rcsv -e 'print CSV.generate_line(ARGV[0].chars, row_sep: \"\")' \"$plain\"",
     PY_CSV_ORACLE.format(d=",")),
    ("delim-csv-words-semicolon-python-clover", P("clover-finch-12"),
     "python3 -I -c \"import csv,sys,re; w=csv.writer(sys.stdout, delimiter=';', lineterminator='\\r\\n'); "
     "w.writerow(re.findall(r'\\S+\\s*', sys.argv[1]))\" \"$plain\"", RB_CSV_ORACLE.format(d=";")),
    ("delim-tsv-escapes-perl-jade", P("jade-lynx-72", "Nice work decoding this warmup! \\o/\t"),
     "perl -CSA -e 'print join \"\\t\", map { (my $c = $_) =~ s/\\\\/\\\\\\\\/g; $c =~ s/\\t/\\\\t/g; "
     "$c =~ s/\\n/\\\\n/g; $c } split //, $ARGV[0]' \"$plain\"", PY_TSV_ORACLE),
    ("delim-scheme-chicken-maple", P("maple-badger-90"),
     LISP + "python3 -I -c \"import json,sys; print(json.dumps(sys.argv[1]))\" \"$plain\" | "
     "$R/usr/bin/csi -q -e '(write (string->list (read)))'   # plain in as a string literal on stdin",
     SBCL.format(prog="'(princ (coerce (read) (quote string)))'")),
    ("delim-cl-sbcl-amber", P("amber-stoat-47"),
     SBCL.format(prog="'(prin1 (coerce (second sb-ext:*posix-argv*) (quote list)))'") + " \"$plain\"",
     CSI + "'(display (list->string (read)))'"),
    ("delim-clojure-vector-jade", P("jade-otter-63"),
     CLJJ + "printf %s \"$plain\" | " + CLJ + "'(prn (vec (slurp *in*)))'",
     CLJJ + CLJ + "'(print (apply str (clojure.edn/read-string (slurp *in*))))'"),
    ("delim-yaml-flow-chars-pyyaml-cobalt", P("cobalt-raven-25"),
     "python3 -I -c \"import sys,yaml; sys.stdout.write(yaml.safe_dump(list(sys.argv[1]), default_flow_style=True, "
     "width=10**9).strip())\" \"$plain\"", RB_YAML_ORACLE),
    ("delim-yaml-flow-words-wrapped-pyyaml-clover", P("clover-heron-84"),
     "python3 -I -c \"import sys,yaml,re; sys.stdout.write(yaml.safe_dump(re.findall(r'\\S+\\s*', sys.argv[1]), "
     "default_flow_style=True).strip())\" \"$plain\"", RB_YAML_ORACLE),
]
DECOYS = [
    ("delim-decoy-csv-unterminated-quote", "python3 -I -c \"import csv,sys; csv.writer(sys.stdout, "
     "quoting=csv.QUOTE_ALL, lineterminator='').writerow(list(sys.argv[1]))\" \"$plain\" | head -c -1   "
     "# QUOTE_ALL run, final closing quote cut", RB_CSV_ORACLE.format(d=","), P("amber-heron-58")),
    ("delim-decoy-yaml-int-codes", "python3 -I -c \"import sys,yaml; sys.stdout.write(yaml.safe_dump([ord(c) for c in "
     "sys.argv[1]], default_flow_style=True, width=10**9).strip())\" \"$plain\"   # char CODES, ints not strings",
     RB_YAML_ORACLE, P("jade-lynx-72")),
    ("delim-decoy-scheme-bad-charname", "printf %s '(#\\N #\\i #\\bogusname #\\c #\\e)'   # unknown char name",
     CSI + "'(display (list->string (read)))'", None),
    ("delim-decoy-prose-commas", "printf %s 'Agenda: coffee, standup, \"quick\" sync; then lunch | notes, etc.'   "
     "# hand-written prose with , ; | and quotes", RB_CSV_ORACLE.format(d=","), None),
]


def sh(cmd, plain=None, stdin=None):
    env = dict(os.environ, plain=plain or "")
    r = subprocess.run(["bash", "-c", cmd], cwd=ROOT, env=env, input=stdin, capture_output=True, text=True,
                       timeout=120)
    lines = [x.strip() for x in r.stderr.splitlines() if x.strip()]
    return r.returncode, r.stdout, ([x for x in lines if "rror" in x] or lines[-1:])[:1]


for name, plain, gen, orc in FIX:
    rc, enc, err = sh(gen, plain)
    assert rc == 0 and enc, (name, err)
    rc, got, err = sh(orc, stdin=enc)
    assert rc == 0 and got == plain, (name, got, err)
    json.dump({"codec": "delimited-fields", "plain": plain, "encoded": enc, "generator_cmd": gen, "oracle_cmd": orc,
               "oracle_plain": got, "expected": "match"}, open(os.path.join(D, name + ".json"), "w"), indent=1,
              ensure_ascii=False)
    print("ok", name, repr(enc[:70]))
for name, gen, orc, plain in DECOYS:
    rc, enc, err = sh(gen, plain)
    assert enc, (name, err)
    rc2, got, err2 = sh(orc, stdin=enc)
    note = f"oracle rc={rc2}: {err2[0] if err2 else ''}".strip()
    assert rc2 != 0 or got != (plain or ""), (name, got)
    json.dump({"codec": "delimited-fields", "plain": None, "encoded": enc, "generator_cmd": gen, "oracle_cmd": orc,
               "oracle_plain": got if rc2 == 0 else "", "oracle_note": note[:300], "decoy": True, "expected": "none"},
              open(os.path.join(D, name + ".json"), "w"), indent=1, ensure_ascii=False)
    print("decoy", name, repr(enc[:70]), note[:120])
