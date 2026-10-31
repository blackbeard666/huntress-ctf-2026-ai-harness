"""false-friend-discriminator fixtures: expected from a stdlib HCFG backward-scan decoder + objcopy .text sha256
(never lib.binary). Usage: python3 pf_src/pf_fixtures.py <generic dir>"""
import hashlib, json, os, struct, subprocess, sys, tempfile, zipfile, zlib

D = sys.argv[1]
W = tempfile.mkdtemp()
GEN = "sh pf_src/pf_gen.sh  # mkblob.py (stdlib zlib.crc32 HCFG writer) + gcc -O2 fam.c / other.c, zip -X; D28 trio renamed"
ORC = "python3 pf_src/pf_fixtures.py  # stdlib HCFG backward scan (xor, zlib.crc32, json) / objcopy --only-section=.text + sha256"


def members(z):
    zf = zipfile.ZipFile(os.path.join(D, z))
    return [(i.filename, zf.read(i)) for i in zf.infolist()]


def hcfg(b):
    i = len(b)
    while (i := b.rfind(b"HCFG", 0, i)) >= 0:
        if i + 12 <= len(b):
            _, key, n, crc = struct.unpack_from("<BBHI", b, i + 4)
            p = bytes(c ^ key for c in b[i + 12:i + 12 + n])
            if len(p) == n and zlib.crc32(p) == crc:
                try:
                    return json.loads(p.decode())
                except ValueError:
                    pass
    return None


def text_sha(n, b):
    p = os.path.join(W, n)
    open(p, "wb").write(b)
    subprocess.run(["objcopy", "-O", "binary", "--only-section=.text", p, p + ".t"], check=True)
    return hashlib.sha256(open(p + ".t", "rb").read()).hexdigest()


def classes(ms, key):
    out = {}
    for n, b in ms:
        out.setdefault(key(n, b), []).append(n)
    return sorted(out.values(), key=len, reverse=True)


cfgkey = lambda n, b: json.dumps(hcfg(b), sort_keys=True)            # noqa: E731
prefix = lambda n, b: hcfg(b)["campaign"].split("-", 1)[0]           # noqa: E731
JS = {"kind": "json", "syntax": "compact JSON array of basenames"}
INT = {"kind": "integer", "syntax": "base-10 integer"}
TXT = {"kind": "exact_text", "syntax": "exact case-sensitive artifact-derived text only"}
LEAD = "In evidence.zip, Use all members in ZIP central-directory order. "
Q_CFG = LEAD + ("Decode each member's HCFG record (scan backward for HCFG magic, XOR payload, verify CRC32) and group "
                "members whose decoded config objects are byte-for-byte equal; the family is the largest group. ")
Q_PFX = LEAD + ("Decode each member's HCFG record and group members by the prefix of the decoded campaign value (the "
                "text before the first hyphen); the family is the largest group. ")
Q_TXT = LEAD + "Group members by identical .text section SHA-256; the family is the largest group. "


def fam_of(cl):
    if len(cl) > 1 and len(cl[0]) == len(cl[1]):
        return None
    return cl[0]


fx = []
five = members("pf_five.zip")
f = fam_of(classes(five, prefix))
fx.append(("pf_five.zip", "stranger_members", Q_PFX + "Submit the members outside the family as a JSON array of basenames "
           "in ZIP central-directory order.", JS, json.dumps([n for n, _ in five if n not in f], separators=(",", ":"))))
fx.append(("pf_five.zip", "family_size", Q_PFX + "How many members belong to the family?", INT, str(len(f))))
f = fam_of(classes(five, cfgkey))
fx.append(("pf_five.zip", "family_members", Q_CFG + "Submit the family's basenames as a JSON array sorted "
           "lexicographically.", JS, json.dumps(sorted(f), separators=(",", ":"))))
fx.append(("pf_five.zip", "family_config_campaign", Q_CFG + "Submit the family's common decoded campaign value.", TXT,
           hcfg(dict(five)[f[0]])["campaign"]))
f = fam_of(classes(five, text_sha))
fx.append(("pf_five.zip", "strangers", Q_TXT + "Submit the stranger members (not in the family) as a JSON array in ZIP "
           "central-directory order.", JS, json.dumps([n for n, _ in five if n not in f], separators=(",", ":"))))
f = fam_of(classes(five, prefix))
cs = {hcfg(dict(five)[n])["campaign"] for n in f}
fx.append(("pf_five.zip", "family_campaign", Q_PFX + "Submit the family's common decoded campaign value.", TXT,
           cs.pop() if len(cs) == 1 else None))   # decoy: prefix family spans two campaigns -> no common value
d28 = members("pf_d28_shuffled.zip")
f = fam_of(classes(d28, cfgkey))
odd = [n for n, _ in d28 if n not in f]
fx.append(("pf_d28_shuffled.zip", "false_friend_member", Q_CFG + "Submit the basename of the false friend (the member "
           "outside the family).", TXT, odd[0] if len(odd) == 1 else None))
fx.append(("pf_d28_shuffled.zip", "family_config_campaign", Q_CFG + "Submit the family's common decoded campaign value.",
           TXT, hcfg(dict(d28)[f[0]])["campaign"]))
fx.append(("pf_d28_shuffled.zip", "family_size", Q_CFG + "How many members belong to the family?", INT, str(len(f))))
tie = members("pf_tie.zip")
f = fam_of(classes(tie, text_sha))   # decoy: 2 + 2 tie -> no family
fx.append(("pf_tie.zip", "family_members", Q_TXT + "Submit the family's basenames as a JSON array in ZIP order.", JS,
           None if f is None else json.dumps(f, separators=(",", ":"))))
for mem, field, q, af, exp in fx:
    d = {"kind": "generic_field", "member": mem, "field": field, "question": q, "answer_format": af, "expected": exp,
         "decoy": exp is None, "generator_cmd": GEN, "oracle_cmd": ORC}
    json.dump(d, open(os.path.join(D, "%s.%s.json" % (mem, field)), "w"), indent=1)
    print(mem, field, exp)
