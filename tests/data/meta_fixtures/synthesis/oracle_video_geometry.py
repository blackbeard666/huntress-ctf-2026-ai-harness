"""Independent oracle: ffmpeg 7.0.2 demuxer report (`ffmpeg -i`: stream WxH, DAR, displaymatrix rotation, Duration,
title; `-f null` decoded frame count) + exiftool -j (ImageWidth/ImageHeight of stills, Make/Model/Title incl. QuickTime
Keys) + plain-python grouping. usage: python3 oracle_video_geometry.py ZIP -> JSON of every value"""
import json, math, os, re, subprocess, sys, tempfile, zipfile

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../tools/imageio_ffmpeg_pkg/imageio_ffmpeg/"
                 "binaries/ffmpeg-linux-x86_64-v7.0.2")
EX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../bin/exiftool")
SCREEN = {(1366, 768), (1440, 900), (1280, 800), (1920, 1200), (2560, 1440), (1536, 864), (1600, 900), (1680, 1050)}
z = zipfile.ZipFile(sys.argv[1])
d = tempfile.mkdtemp()
info = {}
for n in z.namelist():
    p = os.path.join(d, n)
    open(p, "wb").write(z.read(n))
    err = subprocess.run([F, "-hide_banner", "-i", p], capture_output=True, text=True).stderr
    m = re.search(r"Stream #0:\d+[^\n]*: Video: [^\n]*?, (\d+)x(\d+)", err)
    if not m:
        continue
    w, h = int(m.group(1)), int(m.group(2))
    dar = re.search(r"DAR (\d+):(\d+)", err)
    k = math.gcd(w, h)
    dar = "%s:%s" % dar.groups() if dar else "%d:%d" % (w // k, h // k)
    rot = re.search(r"rotation of (-?[\d.]+) degrees", err)
    rot = int(round(float(rot.group(1)))) if rot else 0
    ex = json.loads(subprocess.run([EX, "-j", "-Make", "-Model", "-AndroidManufacturer", "-AndroidModel", "-Title", p], capture_output=True, text=True).stdout)[0]
    corr = re.search(r"[0-9a-fA-F]{12,}", str(ex.get("Title", "")))
    dur = re.search(r"Duration: ([\d:.]+)", err)
    still = n.endswith((".jpg", ".png"))
    frames = None
    if not still:
        fe = subprocess.run([F, "-hide_banner", "-stats", "-i", p, "-map", "0:v:0", "-f", "null", "-"],
                            capture_output=True, text=True).stderr
        frames = re.findall(r"frame=\s*(\d+)", fe)[-1]
    key = corr.group(0).lower() if corr else (None if still else ("df", dur and dur.group(1), frames))
    info[n] = dict(w=w, h=h, dar=dar, rot=rot, key=key, dev=(str(ex.get("Make", ex.get("AndroidManufacturer", ""))).lower(),
                   str(ex.get("Model", ex.get("AndroidModel", ""))).lower()))
names = sorted(info)
if not names:
    sys.exit(print("none  (no video/still member)"))
area = lambda n: info[n]["w"] * info[n]["h"]  # noqa: E731
groups = {}
for n in names:
    groups.setdefault(json.dumps(info[n]["key"]) if info[n]["key"] else n, []).append(n)
crop_of, origs = {}, []
for g in groups.values():
    o = max(g, key=lambda n: (area(n), -names.index(n)))
    origs.append(o)
    crop_of.update({n: o for n in g if area(n) < area(o)})
claims = {n: info[n]["dev"] for n in names if any(info[n]["dev"])}
vals = list(claims.values())
maj = max(set(vals), key=vals.count) if vals else None
odd = [n for n in claims if claims[n] != maj]
if not (len(odd) == 1 and vals.count(maj) > len(vals) / 2):
    odd = [n for n in claims if (info[n]["w"], info[n]["h"]) in SCREEN]
grp = lambda k: {v: sorted(n for n in names if str(info[n][k]) == v) for v in sorted({str(info[n][k]) for n in names})}  # noqa: E731
print(json.dumps({
    "dimension_order": sorted(names, key=lambda n: (area(n), n)),
    "largest_frame_file": sorted(names, key=lambda n: (-area(n), n))[0],
    "aspect_ratio_groups": grp("dar"), "rotation_groups": grp("rot"),
    "original_files": sorted(origs), "cropped_files": sorted(crop_of), "crop_of": dict(sorted(crop_of.items())),
    "odd_device_file": odd[0] if len(odd) == 1 else None}, separators=(",", ":"), indent=None))
