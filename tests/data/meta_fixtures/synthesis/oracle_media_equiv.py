"""Independent oracle: exiftool -j -Title (WAV INFO INAM / Vorbis TITLE / FLAC TITLE / ID3 TIT2) + libsndfile decode
(soundfile.read -> int16 PCM md5 for lossless members, soundfile.info frames/samplerate for duration) +
networkx.connected_components + hashlib.  usage: python3 oracle_media_equiv.py ZIP -> JSON of every value"""
import hashlib, io, json, re, sys, zipfile
import subprocess
import networkx as nx, soundfile as sf

z = zipfile.ZipFile(sys.argv[1])
names = z.namelist()
info = {}
for n in names:
    b = z.read(n)
    try:
        si = sf.info(io.BytesIO(b))
    except Exception:
        continue
    ex = json.loads(subprocess.run(["exiftool", "-j", "-Title", "-"], input=b, capture_output=True).stdout)[0]
    title = str(ex["Title"]) if "Title" in ex else None
    x = re.search(r"[0-9a-fA-F]{12,}", title or "")
    corr = x.group(0).lower() if x else None
    pcm = None
    if si.format in ("WAV", "FLAC", "AIFF"):
        pcm = hashlib.md5(sf.read(io.BytesIO(b), dtype="int16")[0].astype("<i2").tobytes()).hexdigest()
    info[n] = dict(tag=corr or (("t", title.casefold().strip()) if title else None), pcm=pcm,
                   frames=si.frames, dur=round(si.frames / si.samplerate * 100))


def groups(keys):
    G = nx.Graph(); G.add_nodes_from(info)
    for k in keys:
        by = {}
        for n in info:
            v = info[n][k]
            if v is not None:
                by.setdefault(json.dumps(v), []).append(n)
        for ms in by.values():
            G.add_edges_from((ms[0], x) for x in ms[1:])
    return sorted((sorted(c) for c in nx.connected_components(G)), key=lambda g: g[0])


eq = groups(["tag", "pcm"])
single = [g[0] for g in eq if len(g) == 1]
cj = lambda v: json.dumps(v, separators=(",", ":"))
print(json.dumps({
    "equivalence_groups": cj(eq), "odd_one_out": single[0] if len(single) == 1 else None,
    "duplicate_count": str(sum(len(g) - 1 for g in eq)), "group_count": str(len(eq)),
    "title_groups": cj(groups(["tag"])), "content_groups": cj(groups(["pcm"])),
    "duration_groups": cj(groups(["dur"])), "sample_count_groups": cj(groups(["frames"])),
    "md5_order": cj([n for _, n in sorted((hashlib.md5(z.read(n)).hexdigest(), n) for n in names)]),
    "sha1_order": cj([n for _, n in sorted((hashlib.sha1(z.read(n)).hexdigest(), n) for n in names)]),
    "size_order": cj([n for _, n in sorted((z.getinfo(n).file_size, n) for n in names)]),
}, indent=1))
