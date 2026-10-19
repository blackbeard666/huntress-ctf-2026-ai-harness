"""Generator (ffmpeg 7.0.2 lavfi testsrc + libx264 / crop filter / mdta+title tags / -display_rotation, Pillow JPEG+EXIF
and PNG writer, stdlib zipfile): members for the cross-file video geometry fixtures.
usage: python3 gen_video_geometry.py OUTDIR  -> OUTDIR/{geo.zip, screen.zip, nomedia.zip}"""
import io, os, subprocess, sys, zipfile
from PIL import Image

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../tools/imageio_ffmpeg_pkg/imageio_ffmpeg/"
                 "binaries/ffmpeg-linux-x86_64-v7.0.2")
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
files = {}


def ff(*a):
    subprocess.run([F, "-y", "-loglevel", "error", *a], check=True)


def clip(name, size, frames, title=None, make=None, model=None, android=False, crop=None, rot=None, src=None):
    p, tmp = os.path.join(out, name), os.path.join(out, "tmp_" + name.rsplit(".", 1)[0] + ".mp4")
    inp = ["-i", src] if src else ["-f", "lavfi", "-i", "testsrc=size=%s:rate=10" % size]
    vf = ["-vf", "crop=%s" % crop] if crop else []
    ff(*inp, "-frames:v", str(frames), *vf, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", tmp)
    md = []
    if title:
        md += ["-metadata", "title=" + title]
    if make and not android:
        md += ["-metadata", "com.apple.quicktime.make=" + make, "-metadata", "com.apple.quicktime.model=" + model]
    if make and android:
        md += ["-metadata", "com.android.manufacturer=" + make, "-metadata", "com.android.model=" + model]
    pre = ["-display_rotation:v:0", str(rot)] if rot is not None else []
    flags = ["-movflags", "use_metadata_tags"] if not name.endswith(".mkv") else []
    ff(*pre, "-i", tmp, "-c", "copy", *flags, *md, p)
    files[name] = open(p, "rb").read()
    return tmp


def still(name, size, make=None, model=None):
    im = Image.new("RGB", size, (40, 90, 160))
    bio = io.BytesIO()
    if name.endswith(".jpg"):
        ex = Image.Exif()
        if make:
            ex[271], ex[272] = make, model
        im.save(bio, "JPEG", quality=60, exif=ex.tobytes())
    else:
        im.save(bio, "PNG")
    files[name] = bio.getvalue()


def pack(zname, order):
    with zipfile.ZipFile(os.path.join(out, zname), "w") as z:
        for n in order:
            z.writestr(zipfile.ZipInfo(n, (2026, 10, 18, 12, 0, 0)), files[n])


A = clip("a_full.mp4", "320x240", 10, "Huntress clip a1b2c3d4e5f6", "Apple", "iPhone 15 Pro")
clip("a_crop.mp4", None, 10, "Huntress clip a1b2c3d4e5f6", "Apple", "iPhone 15 Pro", crop="160:120:80:60", src=A)
B = clip("b_full.mov", "640x360", 8, "Huntress clip 0f9e8d7c6b5a", "Apple", "iPhone 15 Pro", rot=90)
clip("b_crop.mkv", None, 8, "Huntress clip 0f9e8d7c6b5a", crop="320:180:0:0", src=B)
clip("c_odd.mp4", "240x240", 6, "Huntress clip 99aa88bb77cc", "samsung", "SM-S918B", android=True)
still("d_still.jpg", (400, 300), "Apple", "iPhone 15 Pro")
E = clip("e_plain.mp4", "200x150", 7)
clip("e_small.mp4", None, 7, crop="100:75:0:0", src=E)
files["note.txt"] = b"Evidence note: clips pulled from the shared drive.\n"
pack("geo.zip", ["note.txt", "e_small.mp4", "b_crop.mkv", "a_full.mp4", "d_still.jpg", "c_odd.mp4", "a_crop.mp4",
                 "b_full.mov", "e_plain.mp4"])

clip("f1.mp4", "320x240", 5, "Huntress clip 111111aaaaaa", "Apple", "iPhone 14")
clip("f2.mp4", "1366x768", 2, "Huntress clip 222222bbbbbb", "Apple", "iPhone 14")
still("f3.jpg", (640, 480), "Apple", "iPhone 14")
pack("screen.zip", ["f3.jpg", "f2.mp4", "f1.mp4"])

files["readme.md"] = b"# nothing to see\n"
pack("nomedia.zip", ["note.txt", "readme.md"])
for n in os.listdir(out):
    if n.startswith("tmp_"):
        os.remove(os.path.join(out, n))
