"""family-cluster-similarity-facts fixtures: expected values from cmp / objcopy / strings / readelf / objdump (never lib.binary).
Usage: python3 ms_src/ms_fixtures.py <generic dir>"""
import hashlib, json, os, re, subprocess, sys, tempfile, zipfile
from itertools import combinations

D = sys.argv[1]
W = tempfile.mkdtemp()
GEN = "sh ms_src/ms_gen.sh  # "
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True).stdout   # noqa: E731


def unpack(z):
    out = []
    for n in zipfile.ZipFile(os.path.join(D, z)).namelist():
        p = os.path.join(W, n)
        open(p, "wb").write(zipfile.ZipFile(os.path.join(D, z)).read(n))
        out.append(p)
    return out


def text_sha(p):
    sh(f"objcopy -O binary --only-section=.text {p} {p}.text")
    return hashlib.sha256(open(p + ".text", "rb").read()).hexdigest()


def strings(p):
    return set(sh(f"strings -a -n 4 {p}").split("\n")) - {""}


def secnames(p):
    return re.findall(r"^\s*\[\s*\d+\]\s+(\S*)\s+[A-Z_]+\s", sh(f"readelf -SW {p}"), re.M)


def fde_hashes(p):
    hs = []
    for lo, hi in re.findall(r"FDE cie=\w+ pc=([0-9a-f]+)\.\.([0-9a-f]+)", sh(f"readelf --debug-dump=frames {p}")):
        toks = []
        for ln in sh(f"objdump -d --no-show-raw-insn -M intel --start-address=0x{lo} --stop-address=0x{hi} {p}"
                     ).split("\n"):
            m = re.match(r"\s+[0-9a-f]+:\t(.*)$", ln)
            if not m:
                continue
            ins = m.group(1).split("#")[0].strip().split()
            k = 0
            while k < len(ins) and not re.search(r"[\[,]|^(?:0x)?[0-9a-f]+$|^[re]?[a-z]{1,2}x?$|^[xy]mm|^r\d", ins[k]) \
                    or k == 0:
                k += 1
            ops = " ".join(ins[k:])
            ops = re.sub(r" <[^>]*>", "", ops)
            kinds = ["m" if "[" in o else "i" if re.fullmatch(r"(?:0x)?[0-9a-f]+", o) else "r"
                     for o in ops.split(",")] if ops else []
            toks.append(" ".join(ins[:k]) + " " + ",".join(kinds))
        hs.append(hashlib.sha256("\n".join(toks).encode()).hexdigest())
    return hs


def fx(member, field, question, af, expected, oracle, decoy=False):
    d = {"kind": "generic_field", "member": member, "field": field, "question": question, "answer_format": af,
         "expected": expected, "generator_cmd": GEN + "gcc -O2/-O0/-g builds of ms_src/fam.c + other.c zipped "
                                                       "(ms_gcc.zip) / the D28 trio (ms_d28_trio.zip)",
         "oracle_cmd": oracle}
    if decoy:
        d["decoy"] = True
    open(os.path.join(D, f"{member}.{field}.json"), "w").write(json.dumps(d, indent=1) + "\n")


INT = {"kind": "integer", "syntax": "base-10 integer"}
BOOL = {"kind": "enum", "accepted_values": ["true", "false"]}
JS = {"kind": "json", "syntax": "compact JSON array"}
TXT = {"kind": "exact_text", "syntax": "exact member basename"}
U = "In evidence.zip, Use all d31-- members in ZIP central-directory order. "
U28 = U.replace("d31", "d28")

g = unpack("ms_gcc.zip")
a, b, o0, st = g
cmp_l = lambda x, y: len(sh(f"cmp -l {x} {y}").strip().split("\n"))   # noqa: E731
fx("ms_gcc.zip", "family_a_family_b_diff_bytes", U + "Compare family-a.elf and family-b.elf position by position and "
   "count the byte offsets whose values differ.", INT, str(cmp_l(a, b)), "cmp -l family-a.elf family-b.elf | wc -l")
fx("ms_gcc.zip", "family_a_o0_twin_first_diff_offset", U + "Report the zero-based file offset of the first byte that "
   "differs between family-a.elf and o0-twin.elf, in base 10.", INT,
   str(int(re.search(r"byte (\d+)", sh(f"cmp {a} {o0}")).group(1)) - 1), "cmp family-a.elf o0-twin.elf  # byte N -> N-1")
fx("ms_gcc.zip", "family_a_o0_twin_text_sha256_equal", U + "Submit true exactly when family-a.elf and o0-twin.elf "
   "have byte-identical .text sections (equal SHA-256), else false.", BOOL, str(text_sha(a) == text_sha(o0)).lower(),
   "objcopy -O binary --only-section=.text <m> /dev/stdout | sha256sum  # both members, compare")
sa, sb = strings(a), strings(st)
fx("ms_gcc.zip", "family_a_stranger_string_jaccard", U + "Take the sets of printable strings (strings -a -n 4) of "
   "family-a.elf and stranger.elf and submit their Jaccard index rounded to 4 decimal places.",
   {"kind": "pattern", "syntax": "decimal with 4 decimal places"}, "%.4f" % (len(sa & sb) / len(sa | sb)),
   "strings -a -n 4 <m> | sort -u  # both members; |A&B| / |A|B| via python sets")
ha, ho = fde_hashes(a), fde_hashes(o0)
fx("ms_gcc.zip", "family_a_o0_twin_func_hash_overlap", U + "Treat every .eh_frame FDE pc range as one function, hash "
   "its normalised instructions (mnemonic plus operand kinds, immediates and displacements masked) and count the "
   "functions of family-a.elf whose hash also occurs in o0-twin.elf (multiset intersection).", INT,
   str(sum(min(ha.count(h), ho.count(h)) for h in set(ha))),
   "readelf --debug-dump=frames <m> (FDE pc=lo..hi) + objdump -d -M intel --start/--stop-address per FDE; "
   "mnemonic + r/i/m operand kinds, sha256 per FDE, multiset overlap")
ts = {p: text_sha(p) for p in g}
big = max((sorted([q for q in g if ts[q] == ts[p]], key=g.index) for p in g), key=len)
fx("ms_gcc.zip", "family_members", U + "Cluster the members by identical .text SHA-256 and submit the members of the "
   "family (the largest cluster) as a JSON array of basenames in ZIP order.", JS,
   json.dumps([os.path.basename(p) for p in big], separators=(",", ":")),
   "objcopy -O binary --only-section=.text <m> | sha256sum for each member; group equal digests")
diff = {(x, y): cmp_l(x, y) if os.path.getsize(x) == os.path.getsize(y) else 10 ** 9 for x, y in combinations(g, 2)}
par = {p: p for p in g}
for (x, y), v in diff.items():
    if v <= 30:
        par[y] = par[x]
fx("ms_gcc.zip", "cluster_count", U + "Two members belong to the same cluster when they differ in at most 30 bytes "
   "(same size). Submit the number of clusters.", INT, str(len(set(par.values()))),
   "cmp -l <x> <y> | wc -l for each same-size pair; union pairs with <= 30")
fam = set(big)
look = [p for p in g if p not in fam and any(secnames(p) == secnames(f) for f in fam)]
fx("ms_gcc.zip", "false_friend", U + "Family = members sharing an identical .text SHA-256. The false friend shares a "
   "family member's section-name table but not its .text. Submit the false friend's basename.", TXT,
   os.path.basename(look[0]) if len(look) == 1 else None, "readelf -SW <m> section names + objcopy .text sha256sum")
fx("ms_gcc.zip", "strangers", U + "Family = members sharing an identical .text SHA-256; a stranger shares neither the "
   "family's .text nor its section-name table nor its size. Submit the strangers' basenames as a JSON array.", JS,
   json.dumps([os.path.basename(p) for p in g if p not in fam and p not in look], separators=(",", ":")),
   "readelf -SW <m> section names + objcopy .text sha256sum + stat -c %s")
fx("ms_gcc.zip", "alpha_bravo_diff_bytes", U + "Count the differing bytes between alpha.elf and bravo.elf.", INT, None,
   "unzip -l ms_gcc.zip  # no member basename ends alpha / bravo: field absent", decoy=True)

t = unpack("ms_d28_trio.zip")
fa, fb, ff = t
fx("ms_d28_trio.zip", "family_a_family_b_diff_bytes", U28 + "Compare family-a.elf and family-b.elf position by "
   "position and count the byte offsets whose values differ.", INT, str(cmp_l(fa, fb)),
   "cmp -l family-a.elf family-b.elf | wc -l")
n = min(os.path.getsize(fa), os.path.getsize(ff))
fx("ms_d28_trio.zip", "family_a_false_friend_first_diff", U28 + "Report the zero-based file offset of the first byte "
   "that differs between family-a.elf and false-friend.elf, in base 10.", INT,
   str(int(re.search(r"byte (\d+)", sh(f"cmp {fa} {ff}")).group(1)) - 1), "cmp family-a.elf false-friend.elf")
ts = {p: text_sha(p) for p in t}
fx("ms_d28_trio.zip", "cluster_count", U28 + "Cluster the members by identical .text section SHA-256 and submit the "
   "number of clusters.", INT, str(len(set(ts.values()))), "objcopy -O binary --only-section=.text <m> | sha256sum")
fam = [p for p in t if list(ts.values()).count(ts[p]) > 1]
look = [p for p in t if p not in fam and any(secnames(p) == secnames(f) for f in fam)]
fx("ms_d28_trio.zip", "false_friend", U28 + "Family = members sharing an identical .text SHA-256. The false friend "
   "shares a family member's section-name table but not its .text. Submit the false friend's basename.", TXT,
   os.path.basename(look[0]) if len(look) == 1 else None, "readelf -SW <m> section names + objcopy .text sha256sum")
oracle = ("python3 -c 'from elftools.elf.elffile import ELFFile; ...'  # sections (header order, NOBITS skipped) "
          "whose data() is equal in both")
from elftools.elf.elffile import ELFFile   # noqa: E402 -- the oracle library (lib.binary parses headers itself)
ea, eb = ELFFile(open(fa, "rb")), ELFFile(open(ff, "rb"))
db = {}
for s in eb.iter_sections():
    db.setdefault(s.name, s)
same = [s.name for s in ea.iter_sections() if s.name and s["sh_type"] != "SHT_NOBITS" and s.name in db
        and db[s.name]["sh_type"] != "SHT_NOBITS" and s.data() == db[s.name].data()]
fx("ms_d28_trio.zip", "family_a_false_friend_same_sections", U28 + "List the sections (section-header order of "
   "family-a.elf, NOBITS excluded) whose bytes are identical in family-a.elf and false-friend.elf as a JSON array.",
   JS, json.dumps(same, separators=(",", ":")), oracle)
o = os.path.join(D, "ms_o0_twin.elf")
fx("ms_o0_twin.elf", "family_a_family_b_diff_bytes", "Compare family-a.elf and family-b.elf and count the differing "
   "bytes.", INT, None, "file ms_o0_twin.elf  # one ELF alone, no group / evidence zip: field absent", decoy=True)
print("ok")
