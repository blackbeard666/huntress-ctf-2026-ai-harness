"""Oracle for the synthesis order/group sibling fixtures, independent of lib.meta: unzip -Z -l (sizes) / zipinfo -T
(central-directory DOS times), unzip -p + md5sum/sha1sum/sha512sum, `file --mime-type`, exiftool -j -d %s
(DateTimeOriginal / PDF CreateDate / QuickTime CreateDate), `date -d` on the e-mail Date header, ffmpeg -i stderr
(Duration + first Video/Audio stream codec).  usage: python3 oracle_order_siblings.py ZIP -> JSON of every key."""
import json, os, re, subprocess, sys, tempfile

Z = sys.argv[1]
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../tools/imageio_ffmpeg_pkg/imageio_ffmpeg/"
                 "binaries/ffmpeg-linux-x86_64-v7.0.2")
EXIF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../bin/exiftool")
sh = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout  # noqa: E731
names, size, mtime = [], {}, {}
for ln in sh("zipinfo", "-T", "-l", Z).splitlines():
    p = ln.split()
    if len(p) >= 9 and p[0][0] in "-d?":
        n = p[-1]; names.append(n); size[n] = int(p[3]); mtime[n] = p[-2]   # yyyymmdd.hhmmss
d = tempfile.mkdtemp()
subprocess.run(["unzip", "-q", "-o", Z, "-d", d], check=True)
P = lambda n: os.path.join(d, n)  # noqa: E731
dig = {a: {n: sh(a + "sum", P(n)).split()[0] for n in names} for a in ("md5", "sha1", "sha512")}
mime = {n: sh("file", "-b", "--mime-type", P(n)).strip() for n in names}
ex = {j["SourceFile"].rsplit("/", 1)[-1]: j for j in json.loads(sh(EXIF, "-j", "-d", "%s", "-api", "QuickTimeUTC=1",
                                                                 *[P(n) for n in names]) or "[]")}
emb = {}
for n in names:
    j = ex.get(n, {})
    t = j.get("DateTimeOriginal") or (j.get("CreateDate") if mime[n] in ("application/pdf", "video/mp4") else None)
    if t is None and n.endswith(".eml"):
        m = re.search(r"(?m)^Date:\s*(.+)$", open(P(n), encoding="latin-1").read())
        t = sh("date", "-u", "-d", m.group(1).strip(), "+%s").strip() if m else None
    if t not in (None, "", "0000:00:00 00:00:00"):
        emb[n] = int(t)
dur, codec = {}, {}
for n in names:
    e = subprocess.run([F, "-hide_banner", "-i", P(n)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", e)
    if m and "Audio:" in e or (m and "Video:" in e and "image" not in mime[n]):
        dur[n] = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    v = re.search(r"Stream #0:\d+.*?: Video: (\w+)", e) or re.search(r"Stream #0:\d+.*?: Audio: (\w+)", e)
    if v:
        codec.setdefault(v.group(1), []).append(n)
EXT = {"image/jpeg": {"jpg", "jpeg"}, "image/png": {"png"}, "application/pdf": {"pdf"}, "application/zip": {"zip"},
       "audio/x-wav": {"wav"}, "audio/mpeg": {"mp3"}, "audio/flac": {"flac"}, "video/mp4": {"mp4"},
       "text/plain": {"txt", "eml"}, "message/rfc822": {"eml"}}
mis = [n for n in names if n.rsplit(".", 1)[-1].lower() not in EXT.get(mime[n], {n.rsplit(".", 1)[-1].lower()})]
srt = lambda k: [n for n in sorted(k, key=lambda n: (k[n], n))]  # noqa: E731
out = {"size_order": srt(size), "md5_order": srt(dig["md5"]), "sha1_order": srt(dig["sha1"]),
       "sha512_order": srt(dig["sha512"]), "mtime_order": srt(mtime), "creation_time_order": srt(emb),
       "duration_order": srt(dur), "codec_groups": {c: sorted(v) for c, v in sorted(codec.items())},
       "extension_mismatch_files": mis, "largest_file": srt(size)[-1], "oldest_file": srt(mtime)[0],
       "newest_file": srt(mtime)[-1], "_mime": mime, "_dur": dur, "_emb": emb}
print(json.dumps(out, separators=(",", ":")))
